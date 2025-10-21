"""
Brunet Aging Clocks Module

Provides functionality to analyze genes in the Brunet aging clocks model,
which includes both Chronological and Biological aging predictions based on
cell-type-specific protein expression in the brain.

Data source: Brunet lab aging clocks (Chronological_Bootstrap.xlsx, Biological_Bootstrap.xlsx)
"""

import pandas as pd
import os
from typing import Dict, Optional
from .gene_normalization import normalize_gene


# Data file paths
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
CHRONOLOGICAL_FILE = os.path.join(DATA_DIR, "Chronological_Bootstrap.xlsx")
BIOLOGICAL_FILE = os.path.join(DATA_DIR, "Biological_Bootstrap.xlsx")


# Cell type display names
CELL_DISPLAY = {
    'Oligodendro': 'Oligodendrocytes',
    'Microglia': 'Microglia',
    'Endothelial': 'Endothelial',
    'Astrocyte_qNSC': 'Astrocytes & quiescent Neural Stem Cells',
    'aNSC_NPC': 'activated Neural Stem Cells & Neural Progenitor Cells',
    'Neuroblast': 'Neuroblast'
}


def _prepare_rankings(df: pd.DataFrame) -> Dict:
    """
    Prepares ranking data for all cell types in the model.
    
    Args:
        df: DataFrame with columns: Celltype, canonical_symbol, Coef
        
    Returns:
        Dictionary with rankings for each cell type
    """
    rankings = {}
    
    for cell in CELL_DISPLAY:
        subset = df[df['Celltype'] == cell].copy()
        
        if subset.empty:
            rankings[cell] = {
                'all': pd.DataFrame(),
                'positive': pd.DataFrame(),
                'negative': pd.DataFrame(),
                'total': 0
            }
            continue
        
        # Absolute ranking
        subset['abs_coef'] = subset['Coef'].abs()
        all_ranked = subset.sort_values('abs_coef', ascending=False).reset_index(drop=True)
        
        # Positive (accelerating) ranking
        pos = subset[subset['Coef'] > 0].sort_values('Coef', ascending=False).reset_index(drop=True)
        
        # Negative (decelerating) ranking
        neg = subset[subset['Coef'] < 0].sort_values('Coef', ascending=True).reset_index(drop=True)
        
        rankings[cell] = {
            'all': all_ranked,
            'positive': pos,
            'negative': neg,
            'total': len(subset)
        }
    
    return rankings


def _find_gene_in_model(df: pd.DataFrame, rankings: Dict, cell: str, gene: str) -> str:
    """
    Finds a gene's involvement in a specific cell type within a model.
    
    Args:
        df: Full model DataFrame
        rankings: Pre-computed rankings dictionary
        cell: Cell type to search in
        gene: Canonical gene symbol
        
    Returns:
        Formatted string describing the gene's role and ranking
    """
    row = df[(df['Celltype'] == cell) & (df['canonical_symbol'] == gene)]
    
    if row.empty:
        return "Not involved."
    
    coef = row['Coef'].iloc[0]
    effect = "accelerating aging" if coef > 0 else "decelerating aging"
    
    # Global ranking (by absolute coefficient)
    all_df = rankings[cell]['all']
    global_idx = all_df[all_df['canonical_symbol'] == gene].index
    global_rank = global_idx[0] + 1 if len(global_idx) > 0 else None
    
    # Directional ranking
    if coef > 0:
        dir_df = rankings[cell]['positive']
        dir_total = len(dir_df)
        dir_label = "accelerating"
    else:
        dir_df = rankings[cell]['negative']
        dir_total = len(dir_df)
        dir_label = "decelerating"
    
    dir_idx = dir_df[dir_df['canonical_symbol'] == gene].index
    dir_rank = dir_idx[0] + 1 if len(dir_idx) > 0 else None
    
    total_in_cell = rankings[cell]['total']
    
    if global_rank is not None and dir_rank is not None:
        return (f"{coef:+.2f} ({effect}, "
                f"#{dir_rank} out of {dir_total} {dir_label}, "
                f"#{global_rank} out of {total_in_cell} by absolute coefficient)")
    else:
        return f"{coef:+.2f} ({effect})"


def generate_brunet_gene_report(gene_query: str, output_dir: str = ".") -> Dict:
    """
    Generates a Brunet aging clock report for a gene across all brain cell types.
    
    The Brunet clocks predict aging based on protein expression changes in different
    brain cell types. This function analyzes both Chronological and Biological models.
    
    Args:
        gene_query: Gene name, alias, or Entrez ID (e.g., 'SPP1', 'p53', '5460')
        output_dir: Directory to save the report file (default: current directory)
        
    Returns:
        Dictionary containing:
        - 'gene_query': Original query string
        - 'canonical_symbol': Normalized gene symbol
        - 'report_file': Path to saved report
        - 'results': Dictionary with results for each cell type
        
    Example:
        >>> result = generate_brunet_gene_report("APOE")
        >>> print(result['canonical_symbol'])
        'APOE'
        >>> print(result['results']['Oligodendro']['chronological'])
        '+0.15 (accelerating aging, #5 out of 120 accelerating, #8 out of 450 by absolute coefficient)'
    """
    # Normalize gene name
    norm_result = normalize_gene(gene_query)
    
    if norm_result is None:
        # Gene not found - create report about this
        safe_input = "".join(c for c in gene_query if c.isalnum() or c in ('_', '-', '/'))
        output_path = os.path.join(output_dir, f"Brunet_Report_{safe_input}.txt")
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Gene Query: {gene_query}\n")
            f.write("=" * 50 + "\n")
            f.write("[X] Gene not recognized.\n")
            f.write("Could not map the input to any known canonical gene symbol.\n")
            f.write("Please check spelling or try an official HGNC symbol.\n")
        
        return {
            'gene_query': gene_query,
            'canonical_symbol': None,
            'report_file': output_path,
            'results': {}
        }
    
    canonical_symbol = norm_result['canonical_symbol']
    original_query = norm_result.get('query', gene_query)
    
    # Load data files
    try:
        df_chrono = pd.read_excel(CHRONOLOGICAL_FILE)
        df_bio = pd.read_excel(BIOLOGICAL_FILE)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Required data file not found: {e}. "
                                f"Ensure Chronological_Bootstrap.xlsx and Biological_Bootstrap.xlsx "
                                f"are in {DATA_DIR}")
    
    # Clean and prepare data
    for df in [df_chrono, df_bio]:
        df.columns = df.columns.str.strip()
        if 'Coefficient' in df.columns:
            df.rename(columns={'Coefficient': 'Coef'}, inplace=True)
        elif 'Coef' not in df.columns:
            raise KeyError(f"Expected 'Coefficient' or 'Coef' column not found. "
                           f"Available: {list(df.columns)}")
    
    # Convert coefficients to numeric
    for df in [df_chrono, df_bio]:
        df['Coef'] = pd.to_numeric(
            df['Coef'].astype(str).str.replace(',', '.', regex=False),
            errors='coerce'
        )
    
    # Prepare rankings
    chrono_rankings = _prepare_rankings(df_chrono)
    bio_rankings = _prepare_rankings(df_bio)
    
    # Generate report
    report_lines = []
    report_lines.append(f"Brunet Aging Clock Report for: {original_query}")
    report_lines.append(f"(Canonical symbol: {canonical_symbol})")
    report_lines.append("=" * len(report_lines[0]))
    report_lines.append("")
    report_lines.append("This report shows protein expression changes associated with aging")
    report_lines.append("in different brain cell types, from the Brunet lab aging clocks.")
    report_lines.append("")
    
    results = {}
    
    for raw_cell, display_cell in CELL_DISPLAY.items():
        chrono_res = _find_gene_in_model(df_chrono, chrono_rankings, raw_cell, canonical_symbol)
        bio_res = _find_gene_in_model(df_bio, bio_rankings, raw_cell, canonical_symbol)
        
        results[raw_cell] = {
            'chronological': chrono_res,
            'biological': bio_res
        }
        
        report_lines.append(f"{display_cell}:")
        report_lines.append(f"  Chronological: {chrono_res}")
        report_lines.append(f"  Biological:    {bio_res}")
        report_lines.append("")
    
    # Save report
    safe_name = "".join(c for c in canonical_symbol if c.isalnum() or c in ('_', '-'))
    output_path = os.path.join(output_dir, f"Brunet_Report_{safe_name}.txt")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    return {
        'gene_query': original_query,
        'canonical_symbol': canonical_symbol,
        'report_file': output_path,
        'results': results
    }
