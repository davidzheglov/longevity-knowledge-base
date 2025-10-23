"""
Gene Normalization Module
Provides functionality to normalize gene names, aliases, and IDs to canonical symbols.
"""

import pandas as pd
import re
from typing import Optional, Dict

# Global variable to store the gene alias map
GENE_ALIAS_MAP = None


def build_gene_alias_map(file_path: str) -> Dict[str, dict]:
    """
    Builds a reverse index: alias -> full gene information.
    
    Args:
        file_path: Path to the gene_info.txt TSV file
        
    Returns:
        Dictionary mapping normalized gene names to gene information
    """
    # Read TSV
    df = pd.read_csv(file_path, sep='\t', dtype=str)
    
    alias_to_gene = {}
    
    for _, row in df.iterrows():
        symbol = row['symbol']
        synonyms = row['synonyms']
        entrez = row['entrez_id']
        gene_type = row['type']
        hgnc = row['hgnc_id']
        ensembl = row['ensembl_id']
        
        # Collect all possible names
        all_names = set()
        all_names.add(symbol)
        all_names.add(entrez)  # Can search by Entrez ID
        
        if pd.notna(synonyms) and synonyms != '':
            for syn in synonyms.split('|'):
                syn = syn.strip()
                if syn:
                    all_names.add(syn)
        
        # Normalize for robust search (case-insensitive, no special chars)
        normalized_names = set()
        for name in all_names:
            if not name:
                continue
            normalized_names.add(name)
            # Normalized version: only letters/numbers, uppercase
            clean = re.sub(r'[^A-Za-z0-9]', '', name).upper()
            normalized_names.add(clean)
        
        gene_info = {
            'canonical_symbol': symbol,
            'entrez_id': entrez,
            'type': gene_type,
            'hgnc_id': hgnc,
            'ensembl_id': ensembl,
            'all_names': sorted(all_names)
        }
        
        # Fill index (don't overwrite if already exists)
        for name in normalized_names:
            if name not in alias_to_gene:
                alias_to_gene[name] = gene_info
    
    return alias_to_gene


def initialize_gene_map(file_path: str = 'data/gene_info.txt'):
    """
    Initialize the global gene alias map.
    
    Args:
        file_path: Path to the gene_info.txt file
    """
    global GENE_ALIAS_MAP
    GENE_ALIAS_MAP = build_gene_alias_map(file_path)


def normalize_gene(query: str) -> Optional[Dict]:
    """
    Normalizes a gene query to canonical gene information.
    
    Args:
        query: Gene name, alias, or Entrez ID
        
    Returns:
        Dictionary with gene information including:
        - canonical_symbol: Official gene symbol
        - entrez_id: Entrez Gene ID
        - type: Gene type (e.g., protein-coding)
        - hgnc_id: HGNC identifier
        - ensembl_id: Ensembl gene ID
        - all_names: List of all known aliases
        - query: Original query string
        
        Returns None if gene not found
    """
    if GENE_ALIAS_MAP is None:
        raise RuntimeError("Gene alias map not initialized. Call initialize_gene_map() first.")
    
    if not query or not isinstance(query, str):
        return None
    
    original = query.strip()
    clean = re.sub(r'[^A-Za-z0-9]', '', original).upper()
    
    for cand in [original, clean]:
        if cand in GENE_ALIAS_MAP:
            info = GENE_ALIAS_MAP[cand].copy()
            info['query'] = original
            return info
    
    return None


# Example usage and tests
if __name__ == "__main__":
    # Initialize the map
    initialize_gene_map('../data/gene_info.txt')
    
    # Test queries
    test_queries = ["OCT4", "Oct-4", "OCT3/4", "POU5F1", "OTF3", "5460"]
    
    for q in test_queries:
        res = normalize_gene(q)
        if res:
            print(f"✅ '{q}' → {res['canonical_symbol']} ({res['type']}) | aliases: {', '.join(res['all_names'][:5])}")
        else:
            print(f"❌ '{q}' → NOT FOUND")
