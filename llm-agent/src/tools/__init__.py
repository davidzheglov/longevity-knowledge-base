"""
Longevity Knowledge Base - Tools Package
Comprehensive toolkit for bioinformatics analysis focused on aging and longevity research.
"""

# Gene and protein tools
from .gene_normalization import normalize_gene, initialize_gene_map
from .protein_sequence import find_uniprot, download_uniprot_fasta
from .mutations import mutate_replace, mutate_delete, mutate_insert, mutate_truncate
from .variants import get_gene_variants_excel

# Alignment tools
from .alignment import pairwise_protein_alignment, msa_mafft

# Phylogeny tools
from .phylogeny import plot_mammalian_tree
from .phylogeny_advanced import build_phylo_tree_nj, build_phylo_tree_ml

# Aging clock tools
from .aging_clocks import generate_horvath_gene_report, generate_phenoage_gene_report
from .brunet_clocks import generate_brunet_gene_report
from .hannum_clocks import generate_hannum_gene_report

# Mammal data tools
from .mammal_data import generate_mammal_report

# UniProt parser tools
from .uniprot_parsers import get_reactome_pathways, get_go_annotation, get_drug_info

# UniProt/HPA utility tools
from .uniprot_utils import (
    get_uniprot_features,
    get_protein_function,
    get_hpa_html,
    extract_hpa_summary,
    fetch_and_extract_hpa,
)

# Proteomics tools
from .proteomics import generate_gene_report_pdf
from .mutations_advanced import apply_protein_mutations
from .analysis import compare_solubility_and_pI
from .structure import (
    structural_alignment,
    simple_stability_score,
    compare_stability_simple,
    download_pdb_structures_for_protein,
    smart_visualize,
)
from .literature import fetch_articles_structured, fetch_articles_detailed_log
from .pipeline import generate_comprehensive_prediction

__version__ = "1.0.0"

__all__ = [
    # Gene normalization
    "normalize_gene",
    "initialize_gene_map",
    
    # Protein sequences
    "find_uniprot",
    "download_uniprot_fasta",
    
    # Mutations
    "mutate_replace",
    "mutate_delete", 
    "mutate_insert",
    "mutate_truncate",
    
    # Variants
    "get_gene_variants_excel",
    
    # Alignment
    "pairwise_protein_alignment",
    "msa_mafft",
    
    # Phylogeny
    "plot_mammalian_tree",
    "build_phylo_tree_nj",
    "build_phylo_tree_ml",
    
    # Aging clocks
    "generate_horvath_gene_report",
    "generate_phenoage_gene_report",
    "generate_brunet_gene_report",
    "generate_hannum_gene_report",
    
    # Mammal data
    "generate_mammal_report",
    
    # UniProt parsers
    "get_reactome_pathways",
    "get_go_annotation",
    "get_drug_info",
    "get_uniprot_features",
    "get_protein_function",
    "get_hpa_html",
    "extract_hpa_summary",
    "fetch_and_extract_hpa",
    # Proteomics
    "generate_gene_report_pdf",
    # Advanced mutations & analysis
    "apply_protein_mutations",
    "compare_solubility_and_pI",
    # Structural
    "structural_alignment",
    "simple_stability_score",
    "compare_stability_simple",
    "download_pdb_structures_for_protein",
    "smart_visualize",
    # Literature
    "fetch_articles_structured",
    "fetch_articles_detailed_log",
    # Pipeline
    "generate_comprehensive_prediction",
]
