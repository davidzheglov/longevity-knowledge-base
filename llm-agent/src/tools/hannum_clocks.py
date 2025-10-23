"""
Hannum Aging Clocks Module

Provides functionality to analyze genes in the Hannum epigenetic aging clocks,
which predict biological age based on DNA methylation patterns across different
tissue types and gene expression changes.

Data source: Hannum lab aging models (Blood, Breast, Kidney, Lung, Transcription)
"""

import pandas as pd
import os
from typing import Dict, Optional, List
from .gene_normalization import normalize_gene


# Data file paths
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
BLOOD_FILE = os.path.join(DATA_DIR, "Blood.xlsx")
BREAST_FILE = os.path.join(DATA_DIR, "Breast.xlsx")
KIDNEY_FILE = os.path.join(DATA_DIR, "Kidney.xlsx")
LUNG_FILE = os.path.join(DATA_DIR, "Lung.xlsx")
TRANSCRIPTION_FILE = os.path.join(DATA_DIR, "Transcription.xlsx")


# Model definitions
CPG_MODELS = {
    'Blood': BLOOD_FILE,
    'Breast': BREAST_FILE,
    'Kidney': KIDNEY_FILE,
    'Lung': LUNG_FILE
}


def _analyze_cpg_sites(gene: str, model_name: str, df: pd.DataFrame) -> Dict:
    """
    Analyzes CpG methylation sites for a gene in a specific tissue model.
    
    Args:
        gene: Canonical gene symbol
        model_name: Name of the tissue model
        df: DataFrame with CpG site data (columns: Marker, Genes, Coefficient)
        
    Returns:
        Dictionary with site analysis results
    """
    # Find all CpG sites for this gene
    # Note: 'Genes' column may contain multiple genes separated by comma/space
    gene_sites = df[df['Genes'].str.contains(gene, case=False, na=False)].copy()
    
    if gene_sites.empty:
        return {
            'present': False,
            'sites': [],
            'total': 0,
            'positive': 0,
            'negative': 0
        }
    
    # Convert coefficients to numeric
    gene_sites['Coefficient'] = pd.to_numeric(
        gene_sites['Coefficient'].astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    )
    
    sites = []
    for _, row in gene_sites.iterrows():
        marker = row['Marker']
        coef = row['Coefficient']
        effect = "hypermethylation (aging)" if coef > 0 else "hypomethylation (aging)"
        
        # Get ranking by absolute coefficient
        df_ranked = df.copy()
        df_ranked['Coefficient'] = pd.to_numeric(
            df_ranked['Coefficient'].astype(str).str.replace(',', '.', regex=False),
            errors='coerce'
        )
        df_ranked['abs_coef'] = df_ranked['Coefficient'].abs()
        df_ranked = df_ranked.sort_values('abs_coef', ascending=False).reset_index(drop=True)
        rank = df_ranked[df_ranked['Marker'] == marker].index[0] + 1 if len(df_ranked[df_ranked['Marker'] == marker]) > 0 else None
        
        sites.append({
            'cpg': marker,
            'coefficient': coef,
            'effect': effect,
            'rank': rank,
            'total': len(df)
        })
    
    return {
        'present': True,
        'sites': sites,
        'total': len(sites),
        'positive': len(gene_sites[gene_sites['Coefficient'] > 0]),
        'negative': len(gene_sites[gene_sites['Coefficient'] < 0])
    }


def _analyze_transcription(gene: str, df: pd.DataFrame) -> Optional[Dict]:
    """
    Analyzes gene expression changes in the Transcription model.
    
    Args:
        gene: Canonical gene symbol
        df: DataFrame with gene expression data (columns: Genes, Coefficient)
        
    Returns:
        Dictionary with transcription analysis or None if not present
    """
    gene_row = df[df['Genes'].str.contains(gene, case=False, na=False)]
    
    if gene_row.empty:
        return None
    
    coef = pd.to_numeric(
        gene_row['Coefficient'].iloc[0]
        if isinstance(gene_row['Coefficient'].iloc[0], (int, float))
        else str(gene_row['Coefficient'].iloc[0]).replace(',', '.'),
        errors='coerce'
    )
    
    effect = "increased expression with aging" if coef > 0 else "decreased expression with aging"
    
    # Get ranking
    df_ranked = df.copy()
    df_ranked['Coefficient'] = pd.to_numeric(
        df_ranked['Coefficient'].astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    )
    df_ranked['abs_coef'] = df_ranked['Coefficient'].abs()
    df_ranked = df_ranked.sort_values('abs_coef', ascending=False).reset_index(drop=True)
    
    rank = df_ranked[df_ranked['Genes'].str.contains(gene, case=False, na=False)].index[0] + 1 if len(df_ranked[df_ranked['Genes'].str.contains(gene, case=False, na=False)]) > 0 else None
    
    return {
        'coefficient': coef,
        'effect': effect,
        'rank': rank,
        'total': len(df)
    }


def _find_shared_and_unique_sites(gene: str, all_results: Dict) -> Dict:
    """
    Identifies CpG sites that are shared across models vs unique to one model.
    
    Args:
        gene: Canonical gene symbol
        all_results: Dictionary with results from all CpG models
        
    Returns:
        Dictionary with shared/unique site analysis
    """
    # Collect all CpG sites by model
    sites_by_model = {}
    for model, result in all_results.items():
        if model == 'Transcription' or not result['present']:
            continue
        sites_by_model[model] = set(s['cpg'] for s in result['sites'])
    
    if not sites_by_model:
        return {'shared': [], 'unique': {}}
    
    # Find shared sites (present in multiple models)
    all_sites = set()
    for sites in sites_by_model.values():
        all_sites.update(sites)
    
    shared = []
    for site in all_sites:
        models_with_site = [m for m, sites in sites_by_model.items() if site in sites]
        if len(models_with_site) > 1:
            shared.append({
                'cpg': site,
                'models': models_with_site
            })
    
    # Find unique sites (present in only one model)
    unique = {}
    for model, sites in sites_by_model.items():
        unique_to_model = []
        for site in sites:
            models_with_site = [m for m, s in sites_by_model.items() if site in s]
            if len(models_with_site) == 1:
                unique_to_model.append(site)
        if unique_to_model:
            unique[model] = unique_to_model
    
    return {'shared': shared, 'unique': unique}


def generate_hannum_gene_report(gene_query: str, output_dir: str = ".") -> Dict:
    """
    Generates a Hannum epigenetic aging clock report for a gene across tissue types.
    
    The Hannum clocks predict biological age based on DNA methylation at CpG sites
    and gene expression changes. This function analyzes Blood, Breast, Kidney, Lung
    (CpG methylation) and Transcription (gene expression) models.
    
    Args:
        gene_query: Gene name, alias, or Entrez ID (e.g., 'ELOVL2', 'p53', '10765')
        output_dir: Directory to save the report file (default: current directory)
        
    Returns:
        Dictionary containing:
        - 'gene_query': Original query string
        - 'canonical_symbol': Normalized gene symbol
        - 'report_file': Path to saved report
        - 'cpg_models': Results for each CpG-based model (Blood, Breast, Kidney, Lung)
        - 'transcription': Gene expression results
        - 'cross_tissue': Shared and unique CpG site analysis
        
    Example:
        >>> result = generate_hannum_gene_report("ELOVL2")
        >>> print(result['canonical_symbol'])
        'ELOVL2'
        >>> print(result['cpg_models']['Blood']['total'])
        3  # Number of CpG sites in blood model
    """
    # Normalize gene name
    norm_result = normalize_gene(gene_query)
    
    if norm_result is None:
        # Gene not found
        safe_input = "".join(c for c in gene_query if c.isalnum() or c in ('_', '-', '/'))
        output_path = os.path.join(output_dir, f"Hannum_Report_{safe_input}.txt")
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
            'cpg_models': {},
            'transcription': None,
            'cross_tissue': {}
        }
    
    canonical_symbol = norm_result['canonical_symbol']
    original_query = norm_result.get('query', gene_query)
    
    # Load data files
    try:
        cpg_data = {}
        for model_name, file_path in CPG_MODELS.items():
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()
            cpg_data[model_name] = df
        
        df_transcription = pd.read_excel(TRANSCRIPTION_FILE)
        df_transcription.columns = df_transcription.columns.str.strip()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Required data file not found: {e}. "
                                f"Ensure Blood.xlsx, Breast.xlsx, Kidney.xlsx, Lung.xlsx, "
                                f"and Transcription.xlsx are in {DATA_DIR}")
    
    # Analyze each CpG model
    cpg_results = {}
    for model_name, df in cpg_data.items():
        cpg_results[model_name] = _analyze_cpg_sites(canonical_symbol, model_name, df)
    
    # Analyze transcription
    trans_result = _analyze_transcription(canonical_symbol, df_transcription)
    
    # Find shared and unique sites
    cross_tissue = _find_shared_and_unique_sites(canonical_symbol, cpg_results)
    
    # Generate report
    report_lines = []
    report_lines.append(f"Hannum Epigenetic Aging Clock Report for: {original_query}")
    report_lines.append(f"(Canonical symbol: {canonical_symbol})")
    report_lines.append("=" * len(report_lines[0]))
    report_lines.append("")
    report_lines.append("This report shows DNA methylation changes at CpG sites and gene")
    report_lines.append("expression changes associated with aging, from the Hannum lab clocks.")
    report_lines.append("")
    
    # CpG methylation models
    report_lines.append("═══ CpG METHYLATION MODELS ═══")
    report_lines.append("")
    
    for model_name in ['Blood', 'Breast', 'Kidney', 'Lung']:
        result = cpg_results[model_name]
        report_lines.append(f"{model_name}:")
        
        if not result['present']:
            report_lines.append("  Not present in this model.")
        else:
            report_lines.append(f"  Total CpG sites: {result['total']}")
            report_lines.append(f"  Hypermethylating: {result['positive']}, Hypomethylating: {result['negative']}")
            report_lines.append("")
            
            for site in result['sites']:
                report_lines.append(f"    {site['cpg']}: {site['coefficient']:+.4f} ({site['effect']})")
                if site['rank']:
                    report_lines.append(f"      Rank #{site['rank']} out of {site['total']} by absolute coefficient")
        
        report_lines.append("")
    
    # Transcription model
    report_lines.append("═══ TRANSCRIPTION (GENE EXPRESSION) ═══")
    report_lines.append("")
    if trans_result is None:
        report_lines.append("Not present in transcription model.")
    else:
        report_lines.append(f"Coefficient: {trans_result['coefficient']:+.4f} ({trans_result['effect']})")
        if trans_result['rank']:
            report_lines.append(f"Rank #{trans_result['rank']} out of {trans_result['total']} by absolute coefficient")
    report_lines.append("")
    
    # Cross-tissue analysis
    if cross_tissue['shared'] or cross_tissue['unique']:
        report_lines.append("═══ CROSS-TISSUE ANALYSIS ═══")
        report_lines.append("")
        
        if cross_tissue['shared']:
            report_lines.append("Shared CpG sites (present in multiple tissues):")
            for item in cross_tissue['shared']:
                report_lines.append(f"  {item['cpg']}: {', '.join(item['models'])}")
            report_lines.append("")
        
        if cross_tissue['unique']:
            report_lines.append("Unique CpG sites (tissue-specific):")
            for model, sites in cross_tissue['unique'].items():
                report_lines.append(f"  {model}: {', '.join(sites)}")
            report_lines.append("")
    
    # Save report
    safe_name = "".join(c for c in canonical_symbol if c.isalnum() or c in ('_', '-'))
    output_path = os.path.join(output_dir, f"Hannum_Report_{safe_name}.txt")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    
    return {
        'gene_query': original_query,
        'canonical_symbol': canonical_symbol,
        'report_file': output_path,
        'cpg_models': cpg_results,
        'transcription': trans_result,
        'cross_tissue': cross_tissue
    }
