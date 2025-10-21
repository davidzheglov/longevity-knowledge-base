"""
OpenAI LLM Agent Orchestrator for Longevity Research Tools

This module provides a conversational AI agent that can call various longevity research tools
through OpenAI's function calling API. The agent can:
- Normalize gene names
- Fetch protein sequences
- Create protein mutations
- Analyze phylogenetic relationships
- Query aging clocks (Horvath, PhenoAge)
- Retrieve mammalian longevity data
- Parse UniProt annotations (pathways, GO, drugs)

Usage:
    from agent import LongevityAgent
    
    agent = LongevityAgent(api_key="your-openai-api-key")
    response = agent.chat("What is the role of TP53 in the Horvath aging clock?")
    print(response)
"""

import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Import all tool functions
from tools import (
    normalize_gene,
    find_uniprot,
    download_uniprot_fasta,
    mutate_replace,
    mutate_delete,
    mutate_insert,
    mutate_truncate,
    get_gene_variants_excel,
    plot_mammalian_tree,
    generate_horvath_gene_report,
    generate_phenoage_gene_report,
    generate_brunet_gene_report,
    generate_hannum_gene_report,
    generate_mammal_report,
    get_reactome_pathways,
    get_go_annotation,
    get_drug_info,
    get_uniprot_features,
    get_protein_function,
    get_hpa_html,
    fetch_and_extract_hpa,
    build_phylo_tree_nj,
    build_phylo_tree_ml,
    generate_gene_report_pdf,
)

# Import function schemas
from function_schemas import ALL_SCHEMAS


class LongevityAgent:
    """
    LLM Agent for longevity research that can call specialized bioinformatics tools.
    
    This agent uses OpenAI's function calling to intelligently decide when to use
    each tool based on the user's query.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """
        Initialize the agent with OpenAI API key and model.
        
        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4-turbo-preview)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Map function names to actual Python functions
        self.function_map = {
            "normalize_gene": normalize_gene,
            "find_uniprot": find_uniprot,
            "download_uniprot_fasta": download_uniprot_fasta,
            "mutate_replace": mutate_replace,
            "mutate_delete": mutate_delete,
            "mutate_insert": mutate_insert,
            "mutate_truncate": mutate_truncate,
            "get_gene_variants_excel": get_gene_variants_excel,
            "plot_mammalian_tree": plot_mammalian_tree,
            "generate_horvath_gene_report": generate_horvath_gene_report,
            "generate_phenoage_gene_report": generate_phenoage_gene_report,
            "generate_brunet_gene_report": generate_brunet_gene_report,
            "generate_hannum_gene_report": generate_hannum_gene_report,
            "generate_mammal_report": generate_mammal_report,
            "get_reactome_pathways": get_reactome_pathways,
            "get_go_annotation": get_go_annotation,
            "get_drug_info": get_drug_info,
            "get_uniprot_features": get_uniprot_features,
            "get_protein_function": get_protein_function,
            "get_hpa_html": get_hpa_html,
            "fetch_and_extract_hpa": fetch_and_extract_hpa,
            "build_phylo_tree_nj": build_phylo_tree_nj,
            "build_phylo_tree_ml": build_phylo_tree_ml,
            "generate_gene_report_pdf": generate_gene_report_pdf,
        }
        
        # System prompt defining agent personality and capabilities
        self.system_prompt = """You are a specialized AI assistant for longevity research and bioinformatics.

You have access to powerful tools for:
- Gene name normalization and alias resolution
- Protein sequence retrieval from UniProt
- Protein mutation generation (point mutations, insertions, deletions, truncations)
- Phylogenetic tree visualization for mammals
- Epigenetic aging clock analysis (Horvath, PhenoAge, Brunet, Hannum)
- Mammalian longevity data from AnAge and AROCM
- Biological pathway, Gene Ontology, and drug information from UniProt

When a user asks about genes, proteins, aging, longevity, or evolutionary biology:
1. Use the appropriate tool(s) to gather accurate information
2. Interpret the results in a clear, scientifically accurate manner
3. Provide context and explain biological significance
4. Suggest follow-up analyses if relevant

Always normalize gene names first if the user provides an alias or common name.
Be conversational but scientifically rigorous."""
        
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool function with the given arguments.
        
        Args:
            function_name: Name of the function to call
            arguments: Dictionary of arguments to pass to the function
            
        Returns:
            Result from the function call
        """
        if function_name not in self.function_map:
            return {"error": f"Unknown function: {function_name}"}
        
        try:
            func = self.function_map[function_name]
            result = func(**arguments)
            return result
        except Exception as e:
            return {"error": f"Error executing {function_name}: {str(e)}"}
    
    def chat(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Send a message to the agent and get a response.
        
        The agent may make multiple function calls to answer the query.
        
        Args:
            user_message: User's question or request
            max_iterations: Maximum number of function calling iterations
            
        Returns:
            Agent's text response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                functions=ALL_SCHEMAS,
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            # If no function call, we have the final answer
            if not message.function_call:
                assistant_message = message.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                return assistant_message
            
            # Execute the requested function
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)
            
            print(f"[Agent] Calling {function_name} with args: {function_args}")
            
            function_result = self._execute_function(function_name, function_args)
            
            # Add function call and result to history
            self.conversation_history.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": message.function_call.arguments
                }
            })
            
            self.conversation_history.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(function_result, default=str)
            })
        
        # If we hit max iterations, return a message
        return "I apologize, but I've reached my maximum number of tool calls. Please try breaking your request into smaller parts."
    
    def reset(self):
        """Reset conversation history."""
        self.conversation_history = [{
            "role": "system",
            "content": self.system_prompt
        }]


def main():
    """Example usage of the LongevityAgent."""
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Initialize agent
    agent = LongevityAgent()
    
    # Example queries
    queries = [
        "What pathways is the p53 gene involved in?",
        "Can you show me the phylogenetic tree for human, mouse, and elephant?",
        "What is the role of NPPB in the Horvath aging clock?",
        "Get me the protein sequence for Oct4 in mouse",
    ]
    
    print("=" * 80)
    print("Longevity Research Agent - Interactive Demo")
    print("=" * 80)
    
    for query in queries:
        print(f"\n[User] {query}")
        print("-" * 80)
        response = agent.chat(query)
        print(f"\n[Agent] {response}")
        print("=" * 80)
        
        # Reset between queries for clean demo
        agent.reset()


if __name__ == "__main__":
    main()
