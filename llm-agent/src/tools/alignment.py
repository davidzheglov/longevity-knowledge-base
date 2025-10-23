"""
Sequence Alignment Module
Functions for pairwise and multiple sequence alignment.
"""

import os
import subprocess
import tempfile
import shutil
from Bio import Align, AlignIO, SeqIO
from Bio.Align import substitution_matrices
from typing import List, Tuple, Optional


def pairwise_protein_alignment(
    fasta1: str,
    fasta2: str,
    output_file: Optional[str] = None,
    output_dir: str = "outputs",
    matrix_name: str = "BLOSUM62",
    gap_open: float = -10,
    gap_extend: float = -0.5
) -> str:
    """
    Perform global pairwise protein alignment (Needleman-Wunsch with affine gaps).
    
    Args:
        fasta1: Path to first FASTA file
        fasta2: Path to second FASTA file
        output_file: Output file path (optional)
        output_dir: Output directory
        matrix_name: Substitution matrix (e.g., "BLOSUM62", "PAM250")
        gap_open: Gap opening penalty (negative)
        gap_extend: Gap extension penalty (negative)
        
    Returns:
        Path to output alignment file
    """
    def read_seq(path):
        records = list(SeqIO.parse(path, "fasta"))
        if len(records) != 1:
            raise ValueError(f"File {path} must contain exactly one sequence.")
        return str(records[0].seq).upper()
    
    seq1 = read_seq(fasta1)
    seq2 = read_seq(fasta2)
    
    # Configure aligner
    aligner = Align.PairwiseAligner()
    aligner.substitution_matrix = substitution_matrices.load(matrix_name)
    aligner.open_gap_score = gap_open
    aligner.extend_gap_score = gap_extend
    aligner.mode = 'global'  # Needleman-Wunsch
    
    # Get best alignment
    alignments = aligner.align(seq1, seq2)
    best = next(alignments)
    
    # Generate output filename
    if output_file is None:
        base1 = os.path.splitext(os.path.basename(fasta1))[0]
        base2 = os.path.splitext(os.path.basename(fasta2))[0]
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"alignment_{base1}_vs_{base2}.txt")
    
    # Write output with parameters
    with open(output_file, "w") as f:
        f.write("=== Protein Global Pairwise Alignment (Needleman-Wunsch) ===\n\n")
        f.write(f"Input files:\n  - Sequence 1: {fasta1}\n  - Sequence 2: {fasta2}\n\n")
        f.write("Alignment parameters:\n")
        f.write(f"  Substitution matrix: {matrix_name}\n")
        f.write(f"  Gap open penalty:    {gap_open}\n")
        f.write(f"  Gap extend penalty:  {gap_extend}\n\n")
        f.write(f"Alignment score: {best.score}\n")
        f.write("-" * 70 + "\n")
        f.write(str(best))
    
    print(f"[OK] Pairwise alignment saved to: {output_file}")
    return output_file


def msa_mafft(
    fasta_files: List[str],
    output_prefix: str = "msa",
    output_dir: str = "outputs"
) -> Tuple[str, str]:
    """
    Perform multiple sequence alignment using MAFFT.
    
    Args:
        fasta_files: List of FASTA file paths
        output_prefix: Prefix for output files
        output_dir: Output directory
        
    Returns:
        Tuple of (fasta_file_path, log_file_path)
    """
    if not shutil.which("mafft"):
        raise RuntimeError("MAFFT not installed. Install with: apt-get install mafft (Linux) or brew install mafft (Mac)")
    
    # Create temporary merged file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".fasta", delete=False) as tmp:
        merged = tmp.name
    
    try:
        # Merge input FASTA files
        with open(merged, "w") as out:
            for f in fasta_files:
                rec = SeqIO.read(f, "fasta")
                SeqIO.write(rec, out, "fasta")
        
        # Run MAFFT
        cmd = ["mafft", "--auto", "--thread", "4", merged]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Output filenames
        os.makedirs(output_dir, exist_ok=True)
        fasta_file = os.path.join(output_dir, f"{output_prefix}.fasta")
        log_file = os.path.join(output_dir, f"{output_prefix}.log.txt")
        
        # Save clean FASTA (alignment only)
        with open(fasta_file, "w") as f:
            f.write(result.stdout)
        
        # Save log separately
        with open(log_file, "w") as f:
            f.write(f"MAFFT multiple alignment log\n")
            f.write("="*50 + "\n")
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write(f"Input files: {', '.join(fasta_files)}\n")
            f.write(f"Stderr:\n{result.stderr}\n")

        print(f"[OK] MSA: {fasta_file}, log: {log_file}")
        return fasta_file, log_file
    
    finally:
        if os.path.exists(merged):
            os.remove(merged)
