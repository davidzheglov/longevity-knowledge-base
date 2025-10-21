import os
import tempfile
from pathlib import Path

import pandas as pd

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools import generate_gene_report_pdf


def test_generate_gene_report_pdf_with_minimal_inputs():
    with tempfile.TemporaryDirectory() as tmp:
        g2p = pd.DataFrame({
            'GeneSymbol': ['TP53', 'BRCA1'],
            'Peptide': ['PEPTIDE1', 'PEPTIDE2'],
        })
        p2m = pd.DataFrame({
            'Peptide': ['PEPTIDE1', 'PEPTIDE2'],
            'Model': ['ModelA', 'ModelB'],
        })

        g2p_path = Path(tmp) / 'Gene_to_Peptide.xlsx'
        p2m_path = Path(tmp) / 'Peptide_to_Model.xlsx'
        g2p.to_excel(g2p_path, index=False)
        p2m.to_excel(p2m_path, index=False)

        out_pdf = Path(tmp) / 'tp53_report.pdf'
        result = generate_gene_report_pdf('TP53', str(out_pdf), str(g2p_path), str(p2m_path))
        assert 'error' not in result
        assert os.path.exists(result['pdf_file'])
        assert os.path.getsize(result['pdf_file']) > 0


def test_generate_gene_report_pdf_no_rows_creates_pdf():
    with tempfile.TemporaryDirectory() as tmp:
        g2p = pd.DataFrame({
            'GeneSymbol': ['BRCA1'],
            'Peptide': ['PEPTIDE2'],
        })
        p2m = pd.DataFrame({
            'Peptide': ['PEPTIDE1', 'PEPTIDE2'],
            'Model': ['ModelA', 'ModelB'],
        })

        g2p_path = Path(tmp) / 'Gene_to_Peptide.xlsx'
        p2m_path = Path(tmp) / 'Peptide_to_Model.xlsx'
        g2p.to_excel(g2p_path, index=False)
        p2m.to_excel(p2m_path, index=False)

        out_pdf = Path(tmp) / 'tp53_report_empty.pdf'
        result = generate_gene_report_pdf('TP53', str(out_pdf), str(g2p_path), str(p2m_path))
        assert 'error' not in result
        assert result['rows'] == 0
        assert os.path.exists(result['pdf_file'])
        assert os.path.getsize(result['pdf_file']) > 0
