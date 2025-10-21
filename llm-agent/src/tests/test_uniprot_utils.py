import os
import pytest
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.uniprot_utils import get_uniprot_features, get_protein_function, get_hpa_html

def test_get_uniprot_features_human_tp53():
    result = get_uniprot_features("TP53", organism="human")
    assert isinstance(result, dict)
    assert "accession" in result
    assert "features" in result
    assert result["gene"] == "TP53"
    assert len(result["features"]) > 0

def test_get_uniprot_features_invalid_gene():
    result = get_uniprot_features("FAKEGENE123", organism="human")
    assert isinstance(result, dict)
    assert "error" in result
    assert "Gene not found" in result["error"]

def test_get_uniprot_features_empty_gene():
    result = get_uniprot_features("", organism="human")
    assert isinstance(result, dict)
    assert "error" in result

def test_get_protein_function_human_tp53():
    result = get_protein_function("TP53", organism="human")
    assert isinstance(result, dict)
    assert "accession" in result
    assert "function" in result
    assert result["gene"] == "TP53"
    assert isinstance(result["function"], str)
    assert len(result["function"]) > 0

def test_get_protein_function_invalid_gene():
    result = get_protein_function("FAKEGENE123", organism="human")
    assert isinstance(result, dict)
    assert "error" in result
    assert "Gene not found" in result["error"]

def test_get_protein_function_empty_gene():
    result = get_protein_function("", organism="human")
    assert isinstance(result, dict)
    assert "error" in result

def test_get_hpa_html_tp53(tmp_path):
    out_path = get_hpa_html("TP53", output_dir=tmp_path)
    if out_path.startswith("Error:"):
        # Accept error if site is unreachable
        assert "Could not fetch HPA page" in out_path or "Network error" in out_path
    else:
        assert os.path.exists(out_path)
        with open(out_path, encoding="utf-8") as f:
            html = f.read()
        assert "Human Protein Atlas" in html or "TP53" in html

def test_get_hpa_html_invalid_gene(tmp_path):
    out_path = get_hpa_html("FAKEGENE123", output_dir=tmp_path)
    assert out_path.startswith("Error:")
    assert "Could not fetch HPA page" in out_path

def test_get_hpa_html_empty_gene(tmp_path):
    out_path = get_hpa_html("", output_dir=tmp_path)
    assert out_path.startswith("Error:")
    assert "Gene name is empty" in out_path
