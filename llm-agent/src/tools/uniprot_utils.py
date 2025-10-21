"""
UniProt and Human Protein Atlas Utility Functions
Implements:
- get_uniprot_features
- get_protein_function
- get_hpa_html
- extract_hpa_summary (new)
- fetch_and_extract_hpa (new)
"""
import requests
import os
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
import re

# --- 1. UniProt Feature Annotations ---
def get_uniprot_features(gene: str, organism: str = "human") -> Dict:
    """
    Downloads UniProt feature annotations for a gene (chains, domains, epitopes, etc.).
    Returns a dictionary of features.
    """
    # Map organism to taxonomy ID
    taxid_map = {
        "human": "9606",
        "mouse": "10090",
        "rat": "10116"
    }
    taxid = taxid_map.get(organism.lower(), "9606")
    
    # Search UniProt for gene
    url = f"https://rest.uniprot.org/uniprotkb/search?query=gene_exact:{gene}+AND+organism_id:{taxid}&fields=accession"
    resp = requests.get(url)
    if resp.status_code != 200 or not resp.json().get('results'):
        return {"error": "Gene not found in UniProt"}
    accession = resp.json()['results'][0]['primaryAccession']
    
    # Get features
    feat_url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    resp = requests.get(feat_url)
    if resp.status_code != 200:
        return {"error": "Could not fetch UniProt entry"}
    entry = resp.json()
    features = entry.get('features', [])
    result = {}
    for feat in features:
        ftype = feat.get('type')
        desc = feat.get('description', '')
        loc = feat.get('location', {})
        start = loc.get('start', {}).get('value')
        end = loc.get('end', {}).get('value')
        result.setdefault(ftype, []).append({
            "description": desc,
            "start": start,
            "end": end
        })
    return {
        "gene": gene,
        "accession": accession,
        "features": result
    }

# --- 2. UniProt Protein Function Description ---
def get_protein_function(gene: str, organism: str = "human") -> Dict:
    """
    Fetches protein function description from UniProt for a gene.
    Returns a dictionary with function text and accession.
    """
    taxid_map = {
        "human": "9606",
        "mouse": "10090",
        "rat": "10116"
    }
    taxid = taxid_map.get(organism.lower(), "9606")
    url = f"https://rest.uniprot.org/uniprotkb/search?query=gene_exact:{gene}+AND+organism_id:{taxid}&fields=accession"
    resp = requests.get(url)
    if resp.status_code != 200 or not resp.json().get('results'):
        return {"error": "Gene not found in UniProt"}
    accession = resp.json()['results'][0]['primaryAccession']
    entry_url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
    resp = requests.get(entry_url)
    if resp.status_code != 200:
        return {"error": "Could not fetch UniProt entry"}
    entry = resp.json()
    comments = entry.get('comments', [])
    function_text = None
    for c in comments:
        if c.get('type') == 'FUNCTION':
            function_text = c.get('texts', [{}])[0].get('value')
            break
    return {
        "gene": gene,
        "accession": accession,
        "function": function_text or "No function description found"
    }

# --- 3. Human Protein Atlas HTML Downloader ---
def get_hpa_html(gene: str, output_dir: str = ".") -> str:
    """
    Downloads the HTML page for a gene from The Human Protein Atlas.
    Returns the path to the saved HTML file.
    """
    if not gene or not gene.strip():
        return "Error: Gene name is empty"
    # Try to normalize to get Ensembl ID and canonical symbol for HPA URL
    url = None
    try:
        # Lazy import to avoid circular imports at module load
        from .gene_normalization import normalize_gene
        norm = normalize_gene(gene)
        if norm and norm.get("ensembl_id"):
            symbol = norm.get("canonical_symbol", gene)
            ensembl_id = norm["ensembl_id"]
            url = f"https://www.proteinatlas.org/{ensembl_id}-{symbol}"
    except Exception:
        # Fall back below
        pass
    if url is None:
        # Fallback: direct symbol URL (may redirect to search)
        url = f"https://www.proteinatlas.org/{gene}"
    try:
        resp = requests.get(url)
    except Exception as e:
        return f"Error: Network error: {e}"
    if resp.status_code != 200:
        return f"Error: Could not fetch HPA page for {gene}"
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"HPA_{gene}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(resp.text)
    return out_path


# --- 4. HPA HTML summary extractor (from notebook) ---
def extract_hpa_summary(html_file: str) -> str:
    """
    Parse a saved HPA HTML page and extract key expression/localization summaries
    into a concise text report. Returns the path to the saved .txt report.
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    gene = os.path.splitext(os.path.basename(html_file))[0]

    def get_value(section_title: str, key_phrase: str) -> str:
        # Find section by header text
        section_header = soup.find('th', string=lambda s: s and section_title.strip() in s)
        if not section_header:
            return "Not found"
        table = section_header.find_parent('table')
        if not table:
            return "Not found"
        # Find row whose <th> contains the key_phrase (ignoring trailing sup i)
        for row in table.find_all('tr'):
            th = row.find('th')
            if not th:
                continue
            full_text = ''.join(th.stripped_strings)
            clean_text = re.sub(r'i$', '', full_text).strip()
            if key_phrase in clean_text:
                td = row.find('td')
                if td:
                    return td.get_text(strip=True)
        return "Not found"

    tissue_spec = get_value("TISSUE RNA EXPRESSION", "Tissue specificity")
    cell_spec = get_value("CELL TYPE RNA EXPRESSION", "Single cell type specificity")
    prognostic = get_value("CANCER & CELL LINES", "Prognostic summary")
    pred_loc = get_value("PROTEIN EXPRESSION AND LOCALIZATION", "Predicted location")

    report = (
        f"TISSUE RNA EXPRESSION\n"
        f"Tissue specificity\t{tissue_spec}\n\n"
        f"CELL TYPE RNA EXPRESSION\n"
        f"Single cell type specificity\t{cell_spec}\n\n"
        f"CANCER & CELL LINES\n"
        f"Prognostic summary\t{prognostic}\n\n"
        f"PROTEIN EXPRESSION AND LOCALIZATION\n"
        f"Predicted location\t{pred_loc}\n"
    )

    output_file = os.path.join(os.path.dirname(html_file), f"{gene}_HPA_Expression.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    return output_file


def fetch_and_extract_hpa(query: str, output_dir: str = ".") -> Optional[str]:
    """
    Convenience helper: downloads HPA HTML for a gene symbol and extracts a
    structured summary file. Returns the path to the text report, or None on error.
    Note: This variant expects an HPA-friendly identifier; to use Ensembl-based
    URLs, normalize externally and pass the "ENSEMBL-SYMBOL" form.
    """
    html_file = get_hpa_html(query, output_dir=output_dir)
    if isinstance(html_file, str) and os.path.exists(html_file):
        return extract_hpa_summary(html_file)
    return None
