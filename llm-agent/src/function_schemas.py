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

