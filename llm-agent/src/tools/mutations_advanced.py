"""
Advanced mutation utilities for protein FASTA files.

Functions:
- apply_protein_mutations: apply blind mutations (rep/del/ins) to a protein sequence from FASTA.

Notes:
- Positions are 1-based (UniProt convention).
- No validation against original residue identity ("blind" mutations).
"""

from __future__ import annotations

import re
from typing import List, Optional
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def apply_protein_mutations(
    fasta_path: str,
    mutations: List[str],
    output_fasta: Optional[str] = None,
    report_path: str = "mutations_report.txt",
) -> SeqRecord:
    """
    Apply a list of blind mutations to a protein sequence loaded from FASTA.

    Supported mutation syntaxes:
    - rep123:V            → replace residue at 123 with 'V'
    - rep120-125:GFP      → replace residues 120..125 with 'GFP'
    - del123              → delete residue 123
    - del120-125          → delete residues 120..125 (inclusive)
    - ins123:GFP          → insert 'GFP' after residue 123

    Args:
        fasta_path: Path to input FASTA file (single-sequence).
        mutations: List of mutation strings (see above).
        output_fasta: If provided, save mutated FASTA to this path.
        report_path: Path to write a plain-text report.

    Returns:
        Bio.SeqRecord of the mutated sequence.
    """
    record = SeqIO.read(fasta_path, "fasta")
    seq = str(record.seq)

    report_lines = [
        f"Input FASTA: {fasta_path}",
        f"Original length: {len(seq)} aa",
        f"Mutations provided: {len(mutations)}",
        "=" * 60,
    ]

    parsed: List[tuple[str, int, int, str]] = []
    for mut in mutations:
        m = mut.strip()
        if not m:
            continue

        r = re.match(r"^rep(\d+):([A-Z]+)$", m)
        if r:
            pos = int(r.group(1))
            new_part = r.group(2)
            parsed.append(("rep", pos, pos, new_part))
            continue

        r = re.match(r"^rep(\d+)-(\d+):([A-Z]+)$", m)
        if r:
            start, end = int(r.group(1)), int(r.group(2))
            new_part = r.group(3)
            parsed.append(("rep", start, end, new_part))
            continue

        r = re.match(r"^del(\d+)$", m)
        if r:
            pos = int(r.group(1))
            parsed.append(("del", pos, pos, ""))
            continue

        r = re.match(r"^del(\d+)-(\d+)$", m)
        if r:
            start, end = int(r.group(1)), int(r.group(2))
            parsed.append(("del", start, end, ""))
            continue

        r = re.match(r"^ins(\d+):([A-Z]+)$", m)
        if r:
            pos = int(r.group(1))
            ins = r.group(2)
            parsed.append(("ins", pos, pos, ins))
            continue

        raise ValueError(f"Unsupported mutation format: '{m}'")

    # Apply from right to left (descending start) so indices stay valid
    parsed.sort(key=lambda t: t[1], reverse=True)
    s_list = list(seq)

    for kind, start, end, payload in parsed:
        i_start = start - 1
        i_end = end  # exclusive in 0-based

        if kind == "rep":
            if start == end:
                if i_start >= len(s_list) or i_start < 0:
                    raise IndexError(f"Position {start} out of range (len={len(s_list)})")
                old = s_list[i_start]
                s_list[i_start] = payload
                report_lines.append(f"REPLACE: pos {start} '{old}' -> '{payload}'")
            else:
                if i_end > len(s_list) or i_start < 0:
                    raise IndexError(f"Range {start}-{end} out of range (len={len(s_list)})")
                old = ''.join(s_list[i_start:i_end])
                del s_list[i_start:i_end]
                s_list[i_start:i_start] = list(payload)
                report_lines.append(f"REPLACE RANGE: {start}-{end} '{old}' -> '{payload}'")

        elif kind == "del":
            if i_end > len(s_list) or i_start < 0:
                raise IndexError(f"Range {start}-{end} out of range (len={len(s_list)})")
            old = ''.join(s_list[i_start:i_end])
            del s_list[i_start:i_end]
            if start == end:
                report_lines.append(f"DELETE: pos {start} '{old}' removed")
            else:
                report_lines.append(f"DELETE RANGE: {start}-{end} '{old}' removed")

        elif kind == "ins":
            if i_start + 1 > len(s_list) or i_start < -1:
                raise IndexError(f"Cannot insert after position {start} (len={len(s_list)})")
            s_list[i_start + 1:i_start + 1] = list(payload)
            report_lines.append(f"INSERT: after {start} added '{payload}'")

    mutated = ''.join(s_list)
    out_record: SeqRecord = record[:]  # shallow copy
    out_record.seq = Seq(mutated)

    if output_fasta:
        Path(output_fasta).parent.mkdir(parents=True, exist_ok=True)
        SeqIO.write(out_record, output_fasta, "fasta")
        report_lines.append(f"\nMutated FASTA saved to: {output_fasta}")

    report_lines.append(f"\nFinal length: {len(mutated)} aa")
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text("\n".join(report_lines), encoding="utf-8")

    return out_record
