import pandas as pd
import re
from typing import Optional, Dict, Annotated

from agents import RunContextWrapper, function_tool
from context import RunContext

def build_gene_alias_map(file_path: str = "files/gene_info.txt") -> Dict[str, dict]:
    df = pd.read_csv(file_path, sep='\t', dtype=str)

    alias_to_gene = {}

    for _, row in df.iterrows():
        symbol = row['symbol']
        synonyms = row['synonyms']
        entrez = row['entrez_id']
        gene_type = row['type']
        hgnc = row['hgnc_id']
        ensembl = row['ensembl_id']

        all_names = set()
        all_names.add(symbol)
        all_names.add(entrez)  

        if pd.notna(synonyms) and synonyms != '':
            for syn in synonyms.split('|'):
                syn = syn.strip()
                if syn:
                    all_names.add(syn)

        normalized_names = set()
        for name in all_names:
            if not name:
                continue
            normalized_names.add(name)
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

        for name in normalized_names:
            if name not in alias_to_gene:
                alias_to_gene[name] = gene_info

    return alias_to_gene

@function_tool
def normalize_gene(wrapper: RunContextWrapper[RunContext], query: Annotated[str, "The gene to normalize"]) -> Optional[Dict]:
    """Normalizes a query to a canonical gene. """
    gene_alias_map = wrapper.context.gene_alias_map

    original = query.strip()
    clean = re.sub(r'[^A-Za-z0-9]', '', original).upper()

    for cand in [original, clean]:
        if cand in gene_alias_map:
            info = gene_alias_map[cand].copy()
            info['query'] = original
            return info

    return None