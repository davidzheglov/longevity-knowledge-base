"""
Proteomics utilities: Generate a simple PDF report for a gene based on peptide and model mappings.

This implements a minimal, robust version inspired by the notebook's proteomics report:
- Load Gene->Peptide and Peptide->Model mappings from Excel
- Filter rows for the requested gene
- Join peptide-to-model info
- Render a simple PDF with a title, summary stats, and a table of peptides/models

Dependencies: pandas, reportlab
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, List

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def _default_data_path() -> Path:
    # Default to the repo data directory if available
    here = Path(__file__).resolve().parent.parent
    candidate = here / "data"
    # Fallback relative to llm-agent root
    if not candidate.exists():
        candidate = Path(__file__).resolve().parents[2] / "data"
    return candidate


def generate_gene_report_pdf(
    gene: str,
    output_file: str = "gene_report.pdf",
    gene_to_peptide_path: Optional[str] = None,
    peptide_to_model_path: Optional[str] = None,
) -> Dict:
    """
    Generate a simple proteomics PDF report for a gene.

    Args:
        gene: Gene symbol to report on (e.g., "TP53").
        output_file: Path to write the PDF report.
        gene_to_peptide_path: Optional override path to Gene_to_Peptide.xlsx.
        peptide_to_model_path: Optional override path to Peptide_to_Model.xlsx.

    Returns:
        { "pdf_file": str, "rows": int, "peptides": int, "models": int }
        or { "error": str }
    """
    if not gene or not isinstance(gene, str):
        return {"error": "gene must be a non-empty string"}

    data_dir = _default_data_path()
    g2p_path = Path(gene_to_peptide_path) if gene_to_peptide_path else (data_dir / "Gene_to_Peptide.xlsx")
    p2m_path = Path(peptide_to_model_path) if peptide_to_model_path else (data_dir / "Peptide_to_Model.xlsx")

    if not g2p_path.exists():
        return {"error": f"Missing Gene_to_Peptide file: {g2p_path}"}
    if not p2m_path.exists():
        return {"error": f"Missing Peptide_to_Model file: {p2m_path}"}

    try:
        g2p = pd.read_excel(g2p_path)
        p2m = pd.read_excel(p2m_path)
    except Exception as e:
        return {"error": f"Error reading Excel files: {e}"}

    # Heuristic column names
    # Expect columns like: GeneSymbol, Peptide
    gene_col = None
    for c in g2p.columns:
        if str(c).lower() in ("gene", "genesymbol", "symbol"):
            gene_col = c
            break
    peptide_col_g2p = None
    for c in g2p.columns:
        if str(c).lower() in ("peptide", "peptide_sequence", "seq"):
            peptide_col_g2p = c
            break
    if gene_col is None or peptide_col_g2p is None:
        return {"error": "Gene_to_Peptide.xlsx must contain gene and peptide columns"}

    peptide_col_p2m = None
    for c in p2m.columns:
        if str(c).lower() in ("peptide", "peptide_sequence", "seq"):
            peptide_col_p2m = c
            break
    # Model/Assay columns are optional; we gather whatever exists
    model_cols: List[str] = [c for c in p2m.columns if str(c).lower() in ("model", "assay", "platform", "panel", "cohort")]

    # Filter and join
    sub = g2p[g2p[gene_col].astype(str).str.upper() == gene.upper()].copy()
    sub.rename(columns={peptide_col_g2p: "Peptide"}, inplace=True)
    if sub.empty:
        # Still create a PDF with a message
        _render_pdf(output_file, gene, [], rows=0, peptides=0, models=0)
        return {"pdf_file": output_file, "rows": 0, "peptides": 0, "models": 0}

    p2m_renamed = p2m.rename(columns={peptide_col_p2m: "Peptide"})
    cols_to_keep = ["Peptide"] + model_cols
    p2m_small = p2m_renamed[cols_to_keep] if model_cols else p2m_renamed[["Peptide"]]
    merged = pd.merge(sub[["Peptide"]], p2m_small, on="Peptide", how="left").drop_duplicates()

    # Prepare rows for table
    headers = ["Peptide"] + (model_cols if model_cols else [])
    table_rows = [headers]
    for _, r in merged.iterrows():
        row = [str(r.get(h, "")) for h in headers]
        table_rows.append(row)

    models_count = merged[model_cols].notna().sum().sum() if model_cols else 0
    _render_pdf(output_file, gene, table_rows, rows=len(merged), peptides=sub.shape[0], models=int(models_count))

    return {
        "pdf_file": output_file,
        "rows": int(len(merged)),
        "peptides": int(sub.shape[0]),
        "models": int(models_count),
    }


def _render_pdf(output_file: str, gene: str, table_rows: List[List[str]], rows: int, peptides: int, models: int) -> None:
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Proteomics Report: {gene}", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Summary: rows={rows}, peptides={peptides}, models={models}", styles['Normal']))
    story.append(Spacer(1, 12))

    if table_rows:
        t = Table(table_rows)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No peptide or model data found for this gene.", styles['Italic']))

    doc.build(story)
