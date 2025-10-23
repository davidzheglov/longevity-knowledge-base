"""
OpenAI Function Calling Schemas for LLM Agent Tools

This module defines the function schemas that can be used with OpenAI's function calling API.
Each schema describes a tool function with its parameters, types, and descriptions.
"""

# Gene Normalization
NORMALIZE_GENE_SCHEMA = {
    "name": "normalize_gene",
    "description": "Normalizes a gene name, alias, or Entrez ID to its canonical HGNC symbol. Handles various formats like 'p53', 'Oct4', 'TP53', etc. Returns gene information including symbol, Entrez ID, type, and aliases.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Gene name, alias, or Entrez ID to normalize (e.g., 'p53', 'Oct4', 'TP53', '7157')"
            }
        },
        "required": ["query"]
    }
}

# Protein Sequence
FIND_UNIPROT_SCHEMA = {
    "name": "find_uniprot",
    "description": "Searches UniProt for a gene and retrieves its protein sequence in FASTA format. Returns protein information including canonical symbol, UniProt ID, FASTA sequence, and known aliases. Can search in different organisms.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Gene name or alias to search for"
            },
            "organism": {
                "type": "string",
                "description": "Organism to search in. Use 'human' for Homo sapiens, or provide scientific name (e.g., 'Mus musculus')",
                "default": "human"
            },
            "save_to_file": {
                "type": "boolean",
                "description": "Whether to save the FASTA sequence to a file",
                "default": True
            }
        },
        "required": ["query"]
    }
}

DOWNLOAD_UNIPROT_FASTA_SCHEMA = {
    "name": "download_uniprot_fasta",
    "description": "Downloads FASTA sequence for a gene from any organism in UniProt. Searches both reviewed (Swiss-Prot) and unreviewed (TrEMBL) databases. Returns the path to the saved FASTA file.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene_name": {
                "type": "string",
                "description": "Gene symbol to search for"
            },
            "organism": {
                "type": "string",
                "description": "Scientific name of the organism (e.g., 'Mus musculus', 'Equus caballus')"
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save the FASTA file",
                "default": "."
            },
            "allow_unreviewed": {
                "type": "boolean",
                "description": "Whether to include unreviewed (TrEMBL) entries if no reviewed entry is found",
                "default": True
            }
        },
        "required": ["gene_name", "organism"]
    }
}

# Mutations
MUTATE_REPLACE_SCHEMA = {
    "name": "mutate_replace",
    "description": "Creates a point mutation by replacing an amino acid at a specific position in a protein sequence. Returns the path to the mutated FASTA file.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene": {
                "type": "string",
                "description": "Gene name to mutate"
            },
            "pos": {
                "type": "integer",
                "description": "Position of the amino acid to replace (1-based indexing)"
            },
            "new_aa": {
                "type": "string",
                "description": "Single letter code of the new amino acid (e.g., 'A', 'G', 'P')"
            }
        },
        "required": ["gene", "pos", "new_aa"]
    }
}

MUTATE_DELETE_SCHEMA = {
    "name": "mutate_delete",
    "description": "Deletes an amino acid at a specific position in a protein sequence. Returns the path to the mutated FASTA file.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene": {
                "type": "string",
                "description": "Gene name"
            },
            "pos": {
                "type": "integer",
                "description": "Position of the amino acid to delete (1-based indexing)"
            }
        },
        "required": ["gene", "pos"]
    }
}

MUTATE_INSERT_SCHEMA = {
    "name": "mutate_insert",
    "description": "Inserts one or more amino acids after a specific position in a protein sequence. Returns the path to the mutated FASTA file.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene": {
                "type": "string",
                "description": "Gene name"
            },
            "pos": {
                "type": "integer",
                "description": "Position after which to insert (1-based indexing)"
            },
            "ins_aa": {
                "type": "string",
                "description": "Amino acid sequence to insert (e.g., 'A', 'GGG', 'APPL')"
            }
        },
        "required": ["gene", "pos", "ins_aa"]
    }
}

MUTATE_TRUNCATE_SCHEMA = {
    "name": "mutate_truncate",
    "description": "Truncates a protein sequence at a specific position, keeping only the N-terminal portion. Returns the path to the truncated FASTA file.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene": {
                "type": "string",
                "description": "Gene name"
            },
            "pos": {
                "type": "integer",
                "description": "Position at which to truncate (keeps residues 1 to pos, inclusive)"
            }
        },
        "required": ["gene", "pos"]
    }
}

# Variants
GET_GENE_VARIANTS_SCHEMA = {
    "name": "get_gene_variants_excel",
    "description": "Retrieves all known protein variants for a human gene from UniProt and saves them to an Excel file. Includes SNPs, disease mutations, and functional variants with their effects, predictions, and disease associations.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Gene name or alias"
            },
            "output_excel": {
                "type": "string",
                "description": "Name of the output Excel file",
                "default": None
            }
        },
        "required": ["query"]
    }
}

# Phylogeny
PLOT_MAMMALIAN_TREE_SCHEMA = {
    "name": "plot_mammalian_tree",
    "description": "Creates a phylogenetic tree visualization for a list of mammalian species. Extracts a subtree from the full mammalian phylogeny and renders it with species names. Returns the path to the saved PNG image.",
    "parameters": {
        "type": "object",
        "properties": {
            "species_list": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of species names (e.g., ['Homo sapiens', 'Mus musculus', 'Loxodonta africana'])"
            },
            "output_png": {
                "type": "string",
                "description": "Name of the output PNG file",
                "default": "final_tree.png"
            },
            "layout": {
                "type": "string",
                "enum": ["r", "u"],
                "description": "Tree layout: 'r' for radial/circular, 'u' for rectangular/upward",
                "default": "r"
            }
        },
        "required": ["species_list"]
    }
}

# Aging Clocks
GENERATE_HORVATH_REPORT_SCHEMA = {
    "name": "generate_horvath_gene_report",
    "description": "Generates a report for a gene's role in the Horvath epigenetic aging clock. Shows which CpG sites are associated with the gene, their coefficients, and rankings among all 353 CpG sites in the model.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene_symbol": {
                "type": "string",
                "description": "Gene symbol (e.g., 'NPPB', 'REEP1')"
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save the report",
                "default": "."
            }
        },
        "required": ["gene_symbol"]
    }
}

GENERATE_PHENOAGE_REPORT_SCHEMA = {
    "name": "generate_phenoage_gene_report",
    "description": "Generates a report for a gene's role in the DNAm PhenoAge epigenetic aging clock. Shows which CpG sites are associated with the gene, their coefficients, and rankings among all 513 CpG sites in the model.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene_symbol": {
                "type": "string",
                "description": "Gene symbol (e.g., 'OXSM', 'SLC44A1')"
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save the report",
                "default": "."
            }
        },
        "required": ["gene_symbol"]
    }
}

# Mammal Data
GENERATE_MAMMAL_REPORT_SCHEMA = {
    "name": "generate_mammal_report",
    "description": "Generates a comprehensive longevity report for a mammal species, combining data from AnAge database (lifespan, weight, reproduction) and AROCM (aging rate). Returns phylogenetic classification, maximum longevity, body size, and metabolic data.",
    "parameters": {
        "type": "object",
        "properties": {
            "species_query": {
                "type": "string",
                "description": "Species name (e.g., 'Homo sapiens', 'Loxodonta africana', 'Mus musculus')"
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save the report",
                "default": "."
            }
        },
        "required": ["species_query"]
    }
}

# UniProt Parsers
GET_REACTOME_PATHWAYS_SCHEMA = {
    "name": "get_reactome_pathways",
    "description": "Retrieves all Reactome biological pathways associated with a human gene. Returns pathway IDs and names, useful for understanding gene function in biological processes.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Gene name or alias"
            },
            "save_report": {
                "type": "boolean",
                "description": "Whether to save pathways to a text file",
                "default": True
            }
        },
        "required": ["query"]
    }
}

GET_GO_ANNOTATION_SCHEMA = {
    "name": "get_go_annotation",
    "description": "Retrieves Gene Ontology (GO) annotations for a human gene from UniProt. Returns GO terms categorized by Molecular Function, Biological Process, and Cellular Component, with evidence codes.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Gene name or alias"
            }
        },
        "required": ["query"]
    }
}

GET_DRUG_INFO_SCHEMA = {
    "name": "get_drug_info",
    "description": "Retrieves DrugBank information for drugs that target a specific human gene/protein. Returns drug IDs and names for known therapeutic compounds.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Gene name or alias"
            }
        },
        "required": ["query"]
    }
}

# UniProt/HPA Utilities
GET_UNIPROT_FEATURES_SCHEMA = {
    "name": "get_uniprot_features",
    "description": "Retrieves UniProt feature annotations (chains, domains, regions, motifs, repeats, epitopes, etc.) for a gene.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene": {"type": "string", "description": "Gene symbol (e.g., 'TP53')"},
            "organism": {
                "type": "string",
                "description": "Organism shorthand: 'human', 'mouse', or 'rat'",
                "default": "human"
            }
        },
        "required": ["gene"]
    }
}

GET_PROTEIN_FUNCTION_SCHEMA = {
    "name": "get_protein_function",
    "description": "Fetches the UniProt FUNCTION annotation text for a gene's protein.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene": {"type": "string", "description": "Gene symbol (e.g., 'TP53')"},
            "organism": {
                "type": "string",
                "description": "Organism shorthand: 'human', 'mouse', or 'rat'",
                "default": "human"
            }
        },
        "required": ["gene"]
    }
}

GET_HPA_HTML_SCHEMA = {
    "name": "get_hpa_html",
    "description": "Downloads the Human Protein Atlas HTML page for a gene and returns the saved file path.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene": {"type": "string", "description": "Gene identifier suitable for proteinatlas.org (e.g., 'TP53' or 'ENSG00000141510-TP53')"},
            "output_dir": {"type": "string", "description": "Directory to save the HTML file", "default": "."}
        },
        "required": ["gene"]
    }
}

FETCH_AND_EXTRACT_HPA_SCHEMA = {
    "name": "fetch_and_extract_hpa",
    "description": "Downloads HPA HTML for a gene and extracts a concise expression/localization summary to a text file; returns the report path.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene": {"type": "string", "description": "Gene identifier (symbol or ENSEMBL-SYMBOL form)."},
            "output_dir": {"type": "string", "description": "Directory to save files", "default": "."}
        },
        "required": ["gene"]
    }
}

# Advanced phylogeny (from alignment)
BUILD_PHYLO_NJ_SCHEMA = {
    "name": "build_phylo_tree_nj",
    "description": "Builds a Neighbor-Joining phylogenetic tree PNG/Newick from an alignment FASTA.",
    "parameters": {
        "type": "object",
        "properties": {
            "alignment_fasta": {"type": "string", "description": "Input alignment FASTA file"},
            "output_prefix": {"type": "string", "description": "Output prefix for files", "default": "tree_nj"},
            "layout": {"type": "string", "enum": ["r", "u"], "default": "r"}
        },
        "required": ["alignment_fasta"]
    }
}

BUILD_PHYLO_ML_SCHEMA = {
    "name": "build_phylo_tree_ml",
    "description": "Builds a Maximum Likelihood phylogenetic tree via IQ-TREE; renders PNG/Newick.",
    "parameters": {
        "type": "object",
        "properties": {
            "alignment_fasta": {"type": "string", "description": "Input alignment FASTA file"},
            "output_prefix": {"type": "string", "description": "Output prefix for files", "default": "tree_ml"},
            "layout": {"type": "string", "enum": ["r", "u"], "default": "r"}
        },
        "required": ["alignment_fasta"]
    }
}

# Proteomics PDF report
GENERATE_PROTEOMICS_PDF_SCHEMA = {
    "name": "generate_gene_report_pdf",
    "description": "Generate a simple proteomics PDF report for a gene using Gene_to_Peptide and Peptide_to_Model Excel files.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene": {"type": "string", "description": "Gene symbol, e.g., TP53"},
            "output_file": {"type": "string", "description": "Output PDF filepath", "default": "gene_report.pdf"},
            "gene_to_peptide_path": {"type": "string", "description": "Path to Gene_to_Peptide.xlsx", "nullable": True},
            "peptide_to_model_path": {"type": "string", "description": "Path to Peptide_to_Model.xlsx", "nullable": True}
        },
        "required": ["gene"]
    }
}

# Brunet Clocks
GENERATE_BRUNET_REPORT_SCHEMA = {
    "name": "generate_brunet_gene_report",
    "description": "Generates a report for a gene's role in the Brunet aging clocks (Chronological and Biological models). Analyzes protein expression changes across 6 brain cell types: Oligodendrocytes, Microglia, Endothelial cells, Astrocytes & qNSC, aNSC & NPC, and Neuroblasts. Shows coefficients, rankings, and whether expression accelerates or decelerates aging.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene_query": {
                "type": "string",
                "description": "Gene name, alias, or Entrez ID (e.g., 'SPP1', 'APOE', 'p53')"
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save the report",
                "default": "."
            }
        },
        "required": ["gene_query"]
    }
}

# Hannum Clocks
GENERATE_HANNUM_REPORT_SCHEMA = {
    "name": "generate_hannum_gene_report",
    "description": "Generates a report for a gene's role in the Hannum epigenetic aging clocks. Analyzes DNA methylation patterns at CpG sites across 4 tissue types (Blood, Breast, Kidney, Lung) and gene expression changes (Transcription model). Shows which sites hypermethylate or hypomethylate with aging, identifies shared vs tissue-specific sites, and ranks coefficients.",
    "parameters": {
        "type": "object",
        "properties": {
            "gene_query": {
                "type": "string",
                "description": "Gene name, alias, or Entrez ID (e.g., 'ELOVL2', 'FHL2', 'NPPB')"
            },
            "output_dir": {
                "type": "string",
                "description": "Directory to save the report",
                "default": "."
            }
        },
        "required": ["gene_query"]
    }
}

# Collection of all schemas for easy import
ALL_SCHEMAS = [
    NORMALIZE_GENE_SCHEMA,
    FIND_UNIPROT_SCHEMA,
    DOWNLOAD_UNIPROT_FASTA_SCHEMA,
    MUTATE_REPLACE_SCHEMA,
    MUTATE_DELETE_SCHEMA,
    MUTATE_INSERT_SCHEMA,
    MUTATE_TRUNCATE_SCHEMA,
    GET_GENE_VARIANTS_SCHEMA,
    PLOT_MAMMALIAN_TREE_SCHEMA,
    GENERATE_HORVATH_REPORT_SCHEMA,
    GENERATE_PHENOAGE_REPORT_SCHEMA,
    GENERATE_MAMMAL_REPORT_SCHEMA,
    GET_REACTOME_PATHWAYS_SCHEMA,
    GET_GO_ANNOTATION_SCHEMA,
    GET_DRUG_INFO_SCHEMA,
    GET_UNIPROT_FEATURES_SCHEMA,
    GET_PROTEIN_FUNCTION_SCHEMA,
    GET_HPA_HTML_SCHEMA,
    FETCH_AND_EXTRACT_HPA_SCHEMA,
    BUILD_PHYLO_NJ_SCHEMA,
    BUILD_PHYLO_ML_SCHEMA,
    GENERATE_PROTEOMICS_PDF_SCHEMA,
    GENERATE_BRUNET_REPORT_SCHEMA,
    GENERATE_HANNUM_REPORT_SCHEMA,
]

# === Artifact helper schemas (exposed to the model) ===

ARTIFACTS_LIST_SCHEMA = {
    "name": "artifacts_list",
    "description": "List recorded artifacts in the current session (optionally filter by type).",
    "parameters": {
        "type": "object",
        "properties": {
            "artifact_type": {"type": ["string", "null"], "description": "Filter by type: e.g., fasta, png, xlsx"}
        },
        "required": []
    }
}

ARTIFACTS_RESOLVE_SCHEMA = {
    "name": "artifacts_resolve",
    "description": "Resolve an artifact id or label to its absolute file path.",
    "parameters": {
        "type": "object",
        "properties": {"id_or_label": {"type": "string"}},
        "required": ["id_or_label"]
    }
}

ARTIFACTS_SEARCH_SCHEMA = {
    "name": "artifacts_search",
    "description": "Search artifacts by filename substring (case-insensitive).",
    "parameters": {
        "type": "object",
        "properties": {"name_substring": {"type": "string"}},
        "required": ["name_substring"]
    }
}

ARTIFACTS_READ_TEXT_SCHEMA = {
    "name": "artifacts_read_text",
    "description": "Read a small text artifact under the session outputs for quoting/summarizing (returns up to max_bytes).",
    "parameters": {
        "type": "object",
        "properties": {
            "id_or_path": {"type": "string", "description": "Artifact id/label or a relative/absolute path"},
            "max_bytes": {"type": "integer", "default": 16384}
        },
        "required": ["id_or_path"]
    }
}

# Extend ALL_SCHEMAS with artifact helpers
ALL_SCHEMAS.extend([
    ARTIFACTS_LIST_SCHEMA,
    ARTIFACTS_RESOLVE_SCHEMA,
    ARTIFACTS_SEARCH_SCHEMA,
    ARTIFACTS_READ_TEXT_SCHEMA,
])

# === New advanced tool schemas ===

APPLY_PROTEIN_MUTATIONS_SCHEMA = {
    "name": "apply_protein_mutations",
    "description": "Apply blind mutations (rep/del/ins) to a protein sequence from a FASTA file; saves mutated FASTA and a text report.",
    "parameters": {
        "type": "object",
        "properties": {
            "fasta_file": {"type": "string", "description": "Input FASTA path"},
            "mutations": {"type": "array", "items": {"type": "string"}, "description": "List of mutation directives (e.g., rep123:V, del10-15, ins46:ISHKR)"},
            "output_file": {"type": "string", "description": "Output FASTA filename", "default": "mutated.fasta"},
            "report_file": {"type": "string", "description": "Output report filename", "default": "mutations_report.txt"}
        },
        "required": ["fasta_file", "mutations"]
    }
}

COMPARE_SOL_PI_SCHEMA = {
    "name": "compare_solubility_and_pI",
    "description": "Compare GRAVY (hydropathy) and isoelectric point between wild-type and mutant FASTA sequences and save a report.",
    "parameters": {
        "type": "object",
        "properties": {
            "wt_fasta": {"type": "string", "description": "Wild-type FASTA"},
            "mut_fasta": {"type": "string", "description": "Mutant FASTA"},
            "output_file": {"type": "string", "description": "Output report filename", "default": "solubility_pI_comparison.txt"}
        },
        "required": ["wt_fasta", "mut_fasta"]
    }
}

STRUCTURAL_ALIGNMENT_SCHEMA = {
    "name": "structural_alignment",
    "description": "Align two PDB structures by CA atoms; optionally save aligned PDBs and return RMSD.",
    "parameters": {
        "type": "object",
        "properties": {
            "pdb1_path": {"type": "string", "description": "Reference PDB path"},
            "pdb2_path": {"type": "string", "description": "Mobile PDB path"},
            "save_aligned": {"type": "boolean", "default": True},
            "out1": {"type": "string", "default": "aligned_ref.pdb"},
            "out2": {"type": "string", "default": "aligned_mob.pdb"}
        },
        "required": ["pdb1_path", "pdb2_path"]
    }
}

COMPARE_STABILITY_SIMPLE_SCHEMA = {
    "name": "compare_stability_simple",
    "description": "Crude thermodynamic stability comparison between WT and mutant PDBs; writes a plain-text report.",
    "parameters": {
        "type": "object",
        "properties": {
            "pdb_wt": {"type": "string"},
            "pdb_mut": {"type": "string"},
            "report_name": {"type": "string", "default": "stability_comparison.txt"}
        },
        "required": ["pdb_wt", "pdb_mut"]
    }
}

DOWNLOAD_PDBS_SCHEMA = {
    "name": "download_pdb_structures_for_protein",
    "description": "Download all experimental PDBs for a gene/protein (based on UniProt cross-references).",
    "parameters": {
        "type": "object",
        "properties": {
            "gene": {"type": "string", "description": "Gene/protein symbol"},
            "organism": {"type": "string", "default": "human"}
        },
        "required": ["gene"]
    }
}

SMART_VISUALIZE_SCHEMA = {
    "name": "smart_visualize",
    "description": "Generate a minimal 3Dmol viewer HTML for a PDB file.",
    "parameters": {
        "type": "object",
        "properties": {
            "pdb_file": {"type": "string"},
            "output_html": {"type": "string", "default": "viewer.html"},
            "background": {"type": "string", "default": "white"}
        },
        "required": ["pdb_file"]
    }
}

FETCH_ARTICLES_STRUCTURED_SCHEMA = {
    "name": "fetch_articles_structured",
    "description": "Search Semantic Scholar and save PDFs (when open access) plus metadata under an output folder.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "num_pdfs": {"type": "integer", "default": 5},
            "max_checked": {"type": "integer", "default": 300},
            "delay": {"type": "number", "default": 2.5}
        },
        "required": ["query"]
    }
}

FETCH_ARTICLES_DETAILED_SCHEMA = {
    "name": "fetch_articles_detailed_log",
    "description": "Semantic Scholar fetch with detailed logging; saves all TXT metadata and open-access PDFs.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "num_pdfs": {"type": "integer", "default": 5},
            "max_checked": {"type": "integer", "default": 300},
            "delay": {"type": "number", "default": 2.5}
        },
        "required": ["query"]
    }
}

GENERATE_COMPREHENSIVE_PREDICTION_SCHEMA = {
    "name": "generate_comprehensive_prediction",
    "description": "Run a minimal mutation impact pipeline: download FASTA, apply mutations, compare GRAVY/pI; writes a summary.",
    "parameters": {
        "type": "object",
        "properties": {
            "protein_name": {"type": "string"},
            "mutations": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["protein_name", "mutations"]
    }
}

# Alignment function schemas (missing earlier)
PAIRWISE_ALIGNMENT_SCHEMA = {
    "name": "pairwise_protein_alignment",
    "description": "Global pairwise alignment (Needleman–Wunsch) between two protein FASTA sequences; saves a text report.",
    "parameters": {
        "type": "object",
        "properties": {
            "fasta1": {"type": "string", "description": "First FASTA file path"},
            "fasta2": {"type": "string", "description": "Second FASTA file path"},
            "output_file": {"type": "string", "description": "Output alignment report filename", "default": "alignment.txt"}
        },
        "required": ["fasta1", "fasta2"]
    }
}

MSA_MAFFT_SCHEMA = {
    "name": "msa_mafft",
    "description": "Multiple sequence alignment using MAFFT; provide a list of FASTA files. Returns path to aligned FASTA.",
    "parameters": {
        "type": "object",
        "properties": {
            "fasta_files": {"type": "array", "items": {"type": "string"}, "description": "List of input FASTA paths"},
            "output_prefix": {"type": "string", "description": "Output file prefix (no extension)", "default": "msa"}
        },
        "required": ["fasta_files"]
    }
}

ALL_SCHEMAS.extend([
    APPLY_PROTEIN_MUTATIONS_SCHEMA,
    COMPARE_SOL_PI_SCHEMA,
    STRUCTURAL_ALIGNMENT_SCHEMA,
    COMPARE_STABILITY_SIMPLE_SCHEMA,
    DOWNLOAD_PDBS_SCHEMA,
    SMART_VISUALIZE_SCHEMA,
    FETCH_ARTICLES_STRUCTURED_SCHEMA,
    FETCH_ARTICLES_DETAILED_SCHEMA,
    GENERATE_COMPREHENSIVE_PREDICTION_SCHEMA,
    PAIRWISE_ALIGNMENT_SCHEMA,
    MSA_MAFFT_SCHEMA,
])

