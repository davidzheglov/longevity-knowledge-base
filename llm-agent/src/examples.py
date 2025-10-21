"""
Example Usage of Longevity Research LLM Agent

This script demonstrates various ways to use the agent and its tools.
"""

import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

# Direct tool imports (without LLM agent)
from tools import (
    normalize_gene,
    initialize_gene_map,
    find_uniprot,
    get_reactome_pathways,
    generate_horvath_gene_report,
    plot_mammalian_tree,
    generate_mammal_report,
)

# LLM agent import
from agent import LongevityAgent

# Initialize gene map on module load with correct path
import os
gene_info_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'gene_info.txt')
initialize_gene_map(gene_info_path)


def example_1_direct_tool_usage():
    """Example 1: Using tools directly without LLM agent."""
    print("\n" + "=" * 80)
    print("Example 1: Direct Tool Usage (No LLM Agent)")
    print("=" * 80 + "\n")
    
    # Gene normalization
    print("1. Normalizing gene aliases:")
    for query in ["p53", "Oct4", "FOXO3A"]:
        result = normalize_gene(query)
        if result:
            symbol = result.get('symbol', 'N/A')
            entrez = result.get('entrez_id', 'N/A')
            print(f"  {query} -> {symbol} (Entrez: {entrez})")
        else:
            print(f"  {query} -> Not found")
    
    # Protein sequence
    print("\n2. Fetching protein sequence:")
    result = find_uniprot("TP53", organism="human")
    if result:
        uniprot_id = result.get('uniprot_id', 'N/A')
        print(f"  TP53 -> UniProt {uniprot_id}")
        fasta = result.get('fasta', '')
        if fasta:
            seq_len = len(fasta.split('\n', 1)[1].replace('\n', '')) if '\n' in fasta else 0
            print(f"  Sequence length: {seq_len} aa")
    else:
        print("  TP53 -> Not found")
    
    # Reactome pathways
    print("\n3. Getting Reactome pathways:")
    pathways = get_reactome_pathways("TP53", save_report=False)
    print(f"  TP53 is involved in {len(pathways)} Reactome pathways")
    if pathways:
        print(f"  Example: {pathways[0]['pathway_name']}")
    
    print("\n" + "=" * 80 + "\n")


def example_2_aging_clocks():
    """Example 2: Analyzing genes in epigenetic aging clocks."""
    print("\n" + "=" * 80)
    print("Example 2: Aging Clock Analysis")
    print("=" * 80 + "\n")
    
    # Horvath clock
    print("1. Horvath Clock (353 CpG sites):")
    genes = ["NPPB", "REEP1", "ELOVL2"]
    for gene in genes:
        try:
            result = generate_horvath_gene_report(gene, output_dir="outputs")
            if result.get("cpg_sites"):
                print(f"  {gene}: {len(result['cpg_sites'])} CpG sites associated")
            else:
                print(f"  {gene}: No associations found")
        except Exception as e:
            print(f"  {gene}: Error - {e}")
    
    print("\n" + "=" * 80 + "\n")


def example_3_phylogeny():
    """Example 3: Creating phylogenetic trees."""
    print("\n" + "=" * 80)
    print("Example 3: Phylogenetic Trees")
    print("=" * 80 + "\n")
    
    species_sets = [
        {
            "name": "Great Apes",
            "species": ["Homo sapiens", "Pan troglodytes", "Gorilla gorilla", "Pongo pygmaeus"]
        },
        {
            "name": "Long-lived vs Short-lived Mammals",
            "species": ["Homo sapiens", "Loxodonta africana", "Heterocephalus glaber", "Mus musculus"]
        }
    ]
    
    for spec_set in species_sets:
        print(f"Creating tree for: {spec_set['name']}")
        try:
            output_png = f"outputs/{spec_set['name'].replace(' ', '_').lower()}_tree.png"
            result = plot_mammalian_tree(
                spec_set['species'],
                output_png=output_png,
                layout='r'
            )
            print(f"  [OK] Saved to: {result}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 80 + "\n")


def example_4_mammal_longevity():
    """Example 4: Querying mammal longevity data."""
    print("\n" + "=" * 80)
    print("Example 4: Mammal Longevity Data")
    print("=" * 80 + "\n")
    
    interesting_mammals = [
        "Homo sapiens",
        "Loxodonta africana",  # African elephant
        "Heterocephalus glaber",  # Naked mole rat
        "Mus musculus",  # House mouse
        "Bowhead whale"
    ]
    
    print(f"{'Species':<30} {'Max Longevity (years)':<25} {'Body Mass (kg)':<15}")
    print("-" * 70)
    
    for species in interesting_mammals:
        try:
            result = generate_mammal_report(species, output_dir="outputs")
            if result:
                longevity = result.get('max_longevity_years', 'N/A')
                mass_kg = result.get('adult_weight_g', 0) / 1000 if result.get('adult_weight_g') else 'N/A'
                print(f"{species:<30} {str(longevity):<25} {str(mass_kg):<15}")
        except Exception as e:
            print(f"{species:<30} Error: {e}")
    
    print("\n" + "=" * 80 + "\n")


def example_5_llm_agent():
    """Example 5: Using the LLM agent (requires OpenAI API key)."""
    print("\n" + "=" * 80)
    print("Example 5: LLM Agent Conversational Interface")
    print("=" * 80 + "\n")
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("[WARNING] OPENAI_API_KEY not set - skipping LLM agent examples")
        print("   Set the API key to try conversational queries:")
        print("   PowerShell: $env:OPENAI_API_KEY = \"sk-...\"")
        print("\n" + "=" * 80 + "\n")
        return
    
    try:
        agent = LongevityAgent()
        
        queries = [
            "What pathways is TP53 involved in?",
            "Compare the longevity of elephants and mice",
            "Is FOXO3 part of any epigenetic aging clocks?",
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\nQuery {i}: {query}")
            print("-" * 80)
            response = agent.chat(query)
            print(f"Agent: {response}")
            print()
            
            # Reset between queries for clean examples
            agent.reset()
        
    except Exception as e:
        print(f"[WARNING] Error initializing agent: {e}")
    
    print("=" * 80 + "\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("LONGEVITY RESEARCH LLM AGENT - EXAMPLES".center(80))
    print("=" * 80)
    
    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)
    
    # Run examples
    example_1_direct_tool_usage()
    example_2_aging_clocks()
    example_3_phylogeny()
    example_4_mammal_longevity()
    example_5_llm_agent()
    
    print("\n[SUCCESS] All examples completed!")
    print("[INFO] Check the 'outputs/' directory for generated files\n")


if __name__ == "__main__":
    main()
