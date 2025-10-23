"""
Composite pipelines built on top of atomic tools.

Note: Heavy steps like AlphaFold are not run in this environment; this function
creates a folder, applies mutations, and computes simple property comparisons.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any
import shutil

from .protein_sequence import find_uniprot
from .mutations_advanced import apply_protein_mutations
from .analysis import compare_solubility_and_pI


def generate_comprehensive_prediction(protein_name: str, mutations: List[str], output_dir: str = ".") -> Dict[str, Any]:
    """
    Minimal end-to-end mutation impact pipeline without structural prediction.

    Steps:
    1) Find UniProt and save WT FASTA
    2) Apply mutations to create mutant FASTA
    3) Compare GRAVY and pI

    Returns a dict with artifact paths and notes about skipped steps.
    """
    info = find_uniprot(protein_name, organism="human", save_to_file=True, output_dir=output_dir)
    if info.get("error"):
        return {"error": info["error"]}

    symbol = info.get("canonical_symbol") or protein_name
    base = Path(output_dir) / f"{symbol}_analysis"
    base.mkdir(parents=True, exist_ok=True)

    # Copy WT FASTA into folder
    wt_src = Path(info.get("fasta_file") or "")
    wt_fasta = base / f"{symbol}.fasta"
    if wt_src.is_file():
        shutil.copy(str(wt_src), str(wt_fasta))
    else:
        # Save from in-memory sequence
        seq_txt = info.get("fasta") or ""
        wt_fasta.write_text(seq_txt, encoding="utf-8")

    # Mutate
    mut_fasta = base / f"{symbol}_mutated.fasta"
    report = base / f"{symbol}_mutations.txt"
    apply_protein_mutations(str(wt_fasta), mutations, output_fasta=str(mut_fasta), report_path=str(report))

    # Compare simple properties
    cmp_path = base / f"{symbol}_solubility_pI.txt"
    compare_solubility_and_pI(str(wt_fasta), str(mut_fasta), output_file=str(cmp_path))

    # Compose summary
    summary = base / f"{symbol}_summary.txt"
    summary.write_text(
        "\n".join([
            f"Protein: {symbol}",
            f"WT FASTA: {wt_fasta}",
            f"Mutant FASTA: {mut_fasta}",
            f"Mutation report: {report}",
            f"Solubility/pI: {cmp_path}",
            "",
            "Structural prediction and alignment were skipped in this environment.",
        ]),
        encoding="utf-8",
    )

    return {
        "symbol": symbol,
        "folder": str(base.resolve()),
        "wt_fasta": str(wt_fasta.resolve()),
        "mut_fasta": str(mut_fasta.resolve()),
        "mutation_report": str(report.resolve()),
        "solubility_report": str(cmp_path.resolve()),
        "summary": str(summary.resolve()),
        "note": "AlphaFold and structural analyses are not executed by default.",
    }
