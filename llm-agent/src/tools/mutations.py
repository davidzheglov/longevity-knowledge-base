"""
Mutations Module
Functions for introducing mutations into protein sequences.
"""

import os
from typing import Optional


def _get_seq_from_fasta(fasta_str: str) -> str:
    """Extract sequence from FASTA string (removes header)."""
    lines = fasta_str.strip().splitlines()
    seq = "".join(lines[1:])  # Everything except header
    return seq


def mutate_replace(gene: str, pos: int, new_aa: str, output_dir: str = "outputs") -> str:
    """
    Replace an amino acid at a specific position.
    
    Args:
        gene: Gene symbol
        pos: Position (1-based)
        new_aa: New amino acid (single letter code)
        output_dir: Directory to save output
        
    Returns:
        Path to the saved mutated FASTA file
    """
    from .protein_sequence import find_uniprot
    
    res = find_uniprot(gene, save_to_file=False)
    if "error" in res:
        raise ValueError(f"Could not find protein for gene '{gene}': {res['error']}")
    
    header = res["fasta"].splitlines()[0]
    seq = _get_seq_from_fasta(res["fasta"])
    
    # 1-based → 0-based
    idx = pos - 1
    if idx < 0 or idx >= len(seq):
        raise ValueError(f"Position {pos} out of range for sequence length {len(seq)}")
    
    new_seq = seq[:idx] + new_aa + seq[idx + 1:]
    new_header = f"{header} | REPL {pos}{seq[idx]}>{new_aa}"
    
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{gene}_repl_{pos}{seq[idx]}{new_aa}.fasta")
    with open(filename, "w") as f:
        f.write(new_header + "\n" + new_seq)
    
    print(f"✅ Replacement mutation: {gene} at position {pos}: {seq[idx]}->{new_aa}")
    return filename


def mutate_delete(gene: str, pos: int, output_dir: str = "outputs") -> str:
    """
    Delete an amino acid at a specific position.
    
    Args:
        gene: Gene symbol
        pos: Position (1-based)
        output_dir: Directory to save output
        
    Returns:
        Path to the saved mutated FASTA file
    """
    from .protein_sequence import find_uniprot
    
    res = find_uniprot(gene, save_to_file=False)
    if "error" in res:
        raise ValueError(f"Could not find protein for gene '{gene}': {res['error']}")
    
    header = res["fasta"].splitlines()[0]
    seq = _get_seq_from_fasta(res["fasta"])
    
    idx = pos - 1
    if idx < 0 or idx >= len(seq):
        raise ValueError(f"Position {pos} out of range for sequence length {len(seq)}")
    
    deleted_aa = seq[idx]
    new_seq = seq[:idx] + seq[idx + 1:]
    new_header = f"{header} | DEL {pos}{deleted_aa}"
    
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{gene}_del_{pos}{deleted_aa}.fasta")
    with open(filename, "w") as f:
        f.write(new_header + "\n" + new_seq)
    
    print(f"✅ Deletion mutation: {gene} deleted {deleted_aa} at position {pos}")
    return filename


def mutate_insert(gene: str, pos: int, ins_aa: str, output_dir: str = "outputs") -> str:
    """
    Insert amino acid(s) after a specific position.
    
    Args:
        gene: Gene symbol
        pos: Position after which to insert (1-based)
        ins_aa: Amino acid(s) to insert (single letter codes)
        output_dir: Directory to save output
        
    Returns:
        Path to the saved mutated FASTA file
    """
    from .protein_sequence import find_uniprot
    
    res = find_uniprot(gene, save_to_file=False)
    if "error" in res:
        raise ValueError(f"Could not find protein for gene '{gene}': {res['error']}")
    
    header = res["fasta"].splitlines()[0]
    seq = _get_seq_from_fasta(res["fasta"])
    
    # Insert AFTER position pos (1-based)
    idx = pos  # After 1st position → index 1 in 0-based
    if pos < 0 or idx > len(seq):
        raise ValueError(f"Insert position {pos} invalid for sequence length {len(seq)}")
    
    new_seq = seq[:idx] + ins_aa + seq[idx:]
    new_header = f"{header} | INS after {pos}:{ins_aa}"
    
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{gene}_ins_{pos}{ins_aa}.fasta")
    with open(filename, "w") as f:
        f.write(new_header + "\n" + new_seq)
    
    print(f"✅ Insertion mutation: {gene} inserted {ins_aa} after position {pos}")
    return filename


def mutate_truncate(gene: str, pos: int, output_dir: str = "outputs") -> str:
    """
    Truncate protein sequence at a specific position.
    
    Args:
        gene: Gene symbol
        pos: Position to truncate at (inclusive, 1-based)
        output_dir: Directory to save output
        
    Returns:
        Path to the saved truncated FASTA file
    """
    from .protein_sequence import find_uniprot
    
    res = find_uniprot(gene, save_to_file=False)
    if "error" in res:
        raise ValueError(f"Could not find protein for gene '{gene}': {res['error']}")
    
    header = res["fasta"].splitlines()[0]
    seq = _get_seq_from_fasta(res["fasta"])
    
    if pos < 1 or pos > len(seq):
        raise ValueError(f"Position {pos} out of range for sequence length {len(seq)}")
    
    # Truncate up to pos (1-based → index = pos)
    truncated_seq = seq[:pos]
    
    new_header = f"{header} | TRUNCATED after {pos}"
    
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{gene}_trunc_{pos}.fasta")
    with open(filename, "w") as f:
        f.write(new_header + "\n" + truncated_seq)
    
    print(f"✅ Truncation: {gene} truncated to position {pos} → length {len(truncated_seq)}")
    return filename
