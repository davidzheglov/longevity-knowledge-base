"""
Gene Variants Module
Functions for retrieving gene variant information.
"""

import requests
import pandas as pd
from typing import Optional
import os


def get_gene_variants_excel(
    query: str,
    output_dir: str = "outputs",
    output_excel: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    Get protein variants for a human gene from UniProt Variation API and save to Excel.
    
    Args:
        query: Gene symbol or alias
        output_dir: Directory to save output
        output_excel: Custom output filename (optional)
        
    Returns:
        DataFrame with variant information, or None if failed
    """
    from .gene_normalization import normalize_gene
    from .protein_sequence import find_uniprot
    
    # 1. Normalize gene
    print(f"🔍 Normalizing query: '{query}'")
    norm = normalize_gene(query)
    if not norm:
        print(f"❌ Could not normalize gene: {query}")
        return None
    symbol = norm["canonical_symbol"]
    print(f"✅ Canonical symbol: {symbol}")
    
    # 2. Find UniProt ID
    print(f"📥 Searching for UniProt ID for {symbol}...")
    uniprot_result = find_uniprot(symbol, organism="human", save_to_file=False)
    if "error" in uniprot_result:
        print(f"❌ UniProt ID not found: {uniprot_result['error']}")
        return None
    uniprot_id = uniprot_result["uniprot_id"]
    print(f"✅ Found UniProt ID: {uniprot_id}")
    
    # 3. Query Variation API
    url = f"https://www.ebi.ac.uk/proteins/api/variation/{uniprot_id}?format=json"
    print(f"📡 Requesting variants...")
    try:
        response = requests.get(url, timeout=20)
        if response.status_code != 200:
            print(f"❌ HTTP error {response.status_code}")
            return None
        data = response.json()
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None
    
    # 4. Parse variants
    features = data.get("features", [])
    variants = [f for f in features if f.get("type") == "VARIANT"]
    if not variants:
        print("⚠️ No variants of type 'VARIANT' found")
        return None
    print(f"✅ Found {len(variants)} variants")
    
    records = []
    for v in variants:
        # Get first available ID from xrefs
        variant_id = "N/A"
        for xref in v.get("xrefs", []):
            candidate = xref.get("id")
            if candidate:
                variant_id = candidate
                break
        
        # Consequence type
        consequence = v.get("consequenceType", "N/A")
        
        # Amino acid and cDNA changes
        aa_changes = []
        cdna_changes = []
        for loc in v.get("locations", []):
            loc_str = loc.get("loc", "")
            if loc_str.startswith("p."):
                aa_changes.append(loc_str)
            elif loc_str.startswith("c."):
                cdna_changes.append(loc_str)
        aa_change = "; ".join(sorted(set(aa_changes))) or "N/A"
        cdna_change = "; ".join(sorted(set(cdna_changes))) or "N/A"
        
        # Predictions
        polyphen_pred = polyphen_score = sift_pred = sift_score = "N/A"
        for pred in v.get("predictions", []):
            algo = pred.get("predAlgorithmNameType", "")
            if algo == "PolyPhen":
                polyphen_pred = pred.get("predictionValType", "N/A")
                polyphen_score = pred.get("score", "N/A")
            elif algo == "SIFT":
                sift_pred = pred.get("predictionValType", "N/A")
                sift_score = pred.get("score", "N/A")
        
        # Diseases
        diseases = []
        for assoc in v.get("association", []):
            if assoc.get("disease"):
                diseases.append(assoc.get("name", ""))
        disease_assoc = "; ".join(sorted(set(diseases))) or "N/A"
        
        # Genomic location
        genomic_loc = v.get("genomicLocation", ["N/A"])[0] if v.get("genomicLocation") else "N/A"
        
        # Codon
        codon = v.get("codon", "N/A")
        
        # Somatic status
        somatic = "Yes" if v.get("somaticStatus") == 1 else "No"
        
        records.append({
            "Variant ID": variant_id,
            "Consequence": consequence,
            "Amino acid change (p.)": aa_change,
            "cDNA change (c.)": cdna_change,
            "PolyPhen prediction": polyphen_pred,
            "PolyPhen score": polyphen_score,
            "SIFT prediction": sift_pred,
            "SIFT score": sift_score,
            "Disease association": disease_assoc,
            "Genomic location": genomic_loc,
            "Codon": codon,
            "Somatic": somatic
        })
    
    # 5. Save to Excel
    df = pd.DataFrame(records)
    if output_excel is None:
        os.makedirs(output_dir, exist_ok=True)
        output_excel = os.path.join(output_dir, f"{symbol}_variants.xlsx")
    df.to_excel(output_excel, index=False)
    print(f"✅ Success! Results saved to: {output_excel}")
    return df
