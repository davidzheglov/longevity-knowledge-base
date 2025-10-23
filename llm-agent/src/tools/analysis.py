"""
Lightweight analysis helpers for protein properties.

Functions:
- compare_solubility_and_pI: compare GRAVY and isoelectric point between two FASTA sequences.
"""

from __future__ import annotations

from typing import Dict
from pathlib import Path
from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis


def compare_solubility_and_pI(
    wt_fasta: str,
    mut_fasta: str,
    output_file: str = "solubility_pI_comparison.txt",
    tol: float = 0.001,
) -> Dict:
    """
    Compare GRAVY (hydropathy) and isoelectric point (pI) between two proteins.

    Args:
        wt_fasta: FASTA path for wild-type sequence.
        mut_fasta: FASTA path for mutant sequence.
        output_file: Text report path.
        tol: Delta threshold to treat solubility change as "no significant change".

    Returns:
        Dict with metrics and output_file path.
    """
    for p in [wt_fasta, mut_fasta]:
        if not Path(p).is_file():
            raise FileNotFoundError(f"FASTA not found: {p}")

    wt_record = SeqIO.read(wt_fasta, "fasta")
    mut_record = SeqIO.read(mut_fasta, "fasta")

    def clean(seq: str) -> str:
        return ''.join([c for c in seq.upper() if c.isalpha()])

    wt_seq = clean(str(wt_record.seq))
    mut_seq = clean(str(mut_record.seq))

    allowed = set("ACDEFGHIKLMNPQRSTVWY")
    if not set(wt_seq).issubset(allowed):
        bad = set(wt_seq) - allowed
        raise ValueError(f"Invalid amino acids in wild-type sequence: {bad}")
    if not set(mut_seq).issubset(allowed):
        bad = set(mut_seq) - allowed
        raise ValueError(f"Invalid amino acids in mutant sequence: {bad}")

    wt = ProteinAnalysis(wt_seq)
    mu = ProteinAnalysis(mut_seq)
    wt_gravy, mu_gravy = wt.gravy(), mu.gravy()
    wt_pi, mu_pi = wt.isoelectric_point(), mu.isoelectric_point()

    d_gravy = mu_gravy - wt_gravy
    d_pi = mu_pi - wt_pi

    if d_gravy > tol:
        sol = "↓ solubility (more hydrophobic)"
    elif d_gravy < -tol:
        sol = "↑ solubility (more hydrophilic)"
    else:
        sol = "≈ no significant change in solubility"

    lines = [
        "=== Protein Comparison: Wild-Type vs Mutant ===",
        f"Wild-type — GRAVY: {wt_gravy:.3f}, pI: {wt_pi:.2f}",
        f"Mutant     — GRAVY: {mu_gravy:.3f}, pI: {mu_pi:.2f}",
        f"ΔGRAVY (mut - wt): {d_gravy:+.3f} → {sol}",
        f"ΔpI (mut - wt): {d_pi:+.2f}",
    ]
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(output_file).write_text("\n".join(lines), encoding="utf-8")

    return {
        "wt": {"GRAVY": wt_gravy, "pI": wt_pi},
        "mut": {"GRAVY": mu_gravy, "pI": mu_pi},
        "delta_GRAVY": d_gravy,
        "delta_pI": d_pi,
        "output_file": str(Path(output_file).resolve()),
    }
