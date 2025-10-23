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
from integration.tools_wrapped import (
    bootstrap_data,
    normalize_gene,
    find_uniprot,
    download_uniprot_fasta,
    mutate_replace,
    mutate_delete,
    mutate_insert,
    mutate_truncate,
    get_gene_variants_excel,
    plot_mammalian_tree,
    pairwise_protein_alignment,
    msa_mafft,
    build_phylo_tree_nj,
    build_phylo_tree_ml,
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
    fetch_and_extract_hpa,
    get_gene_variants_excel as _get_gene_variants_excel_alias_for_type,
    generate_gene_report_pdf,
    artifacts_list,
    artifacts_resolve,
    artifacts_search,
    artifacts_read_text,
    apply_protein_mutations,
    compare_solubility_and_pI,
    structural_alignment,
    compare_stability_simple,
    download_pdb_structures_for_protein,
    smart_visualize,
    fetch_articles_structured,
    fetch_articles_detailed_log,
    generate_comprehensive_prediction,
)

# Import function schemas
from function_schemas import ALL_SCHEMAS


class LongevityAgent:
    """
    LLM Agent for longevity research that can call specialized bioinformatics tools.
    
    This agent uses OpenAI's function calling to intelligently decide when to use
    each tool based on the user's query.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5-mini"):
        """
        Initialize the agent with OpenAI API key and model.
        
        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-5-mini)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        # Allow overriding the model via environment variables
        self.model = os.environ.get("OPENAI_MODEL") or os.environ.get("LLM_MODEL") or model
        self.conversation_history: List[Dict[str, Any]] = []
        # Max tool-call rounds (can be overridden via env)
        try:
            # Default higher ceiling; can still be overridden via env LLM_MAX_TOOL_ITERATIONS
            self.max_iterations_default = int(os.environ.get("LLM_MAX_TOOL_ITERATIONS", "30"))
        except Exception:
            self.max_iterations_default = 30
        
        # Map function names to actual Python functions
        self.function_map = {
            "normalize_gene": normalize_gene,
            "find_uniprot": find_uniprot,
            "download_uniprot_fasta": download_uniprot_fasta,
            "mutate_replace": mutate_replace,
            "mutate_delete": mutate_delete,
            "mutate_insert": mutate_insert,
            "mutate_truncate": mutate_truncate,
            "pairwise_protein_alignment": pairwise_protein_alignment,
            "msa_mafft": msa_mafft,
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
            "get_hpa_html": (lambda **kwargs: fetch_and_extract_hpa(kwargs.get("gene") or kwargs.get("query") or "", kwargs.get("output_dir") or ".")),
            "fetch_and_extract_hpa": fetch_and_extract_hpa,
            "build_phylo_tree_nj": build_phylo_tree_nj,
            "build_phylo_tree_ml": build_phylo_tree_ml,
            "generate_gene_report_pdf": generate_gene_report_pdf,
            # Artifacts helpers
            "artifacts_list": artifacts_list,
            "artifacts_resolve": artifacts_resolve,
            "artifacts_search": artifacts_search,
            "artifacts_read_text": artifacts_read_text,
            # Advanced mutations & analysis
            "apply_protein_mutations": apply_protein_mutations,
            "compare_solubility_and_pI": compare_solubility_and_pI,
            # Structural
            "structural_alignment": structural_alignment,
            "compare_stability_simple": compare_stability_simple,
            "download_pdb_structures_for_protein": download_pdb_structures_for_protein,
            "smart_visualize": smart_visualize,
            # Literature
            "fetch_articles_structured": fetch_articles_structured,
            "fetch_articles_detailed_log": fetch_articles_detailed_log,
            # Pipeline
            "generate_comprehensive_prediction": generate_comprehensive_prediction,
        }

        # Ensure tool prerequisites and a run directory exist
        try:
            bootstrap_data()
        except Exception:
            pass
        
        # System prompt defining agent personality, capabilities, tool usage policy, and output format
        self.system_prompt = (
            "You are LongevityLLM, a model developed by the Elephant Labs team—an AI agent designed to optimize protein bioinformatics tasks and accelerate aging research.\n\n"
            "### Discussion Module\n"
            "For general questions such as ‘What is aging?’ or ‘Why is it important to combat aging?’, respond in alignment with the manifesto (when provided). Searching the literature is encouraged, but the core logic must remain consistent with the manifesto text.\n\n"
            "### Database Parser Module\n"
            "When the user asks for general information about a protein: first call normalize_gene to obtain its canonical symbol. Then call get_protein_function and read the resulting text output to summarize the functional description.\n"
            "You may also call: find_uniprot (FASTA), get_uniprot_features (domains, Excel), get_gene_variants_excel (isoforms/variants, Excel), get_go_annotation (GO text), get_reactome_pathways (Reactome text), get_drug_info (DrugBank text), fetch_and_extract_hpa (HPA expression). Save files and reference their names in your answer.\n\n"
            "### Phylogenetic Analysis Module\n"
            "For non-human proteins, use download_uniprot_fasta(gene, Latin species).\n"
            "For comparing two proteins: download both FASTA files (find_uniprot for human; download_uniprot_fasta for non‑human), then run pairwise_protein_alignment(fasta1, fasta2).\n"
            "For three or more proteins: download all sequences, run msa_mafft([fasta_paths]) to produce an aligned FASTA, then build_phylo_tree_nj(aligned_fasta, output_prefix). Save the resulting PNG tree and include it.\n\n"
            "### Mammalian Lifespan Evolution Module\n"
            "For mammalian phylogeny, call plot_mammalian_tree with either a list of Latin species names or an ALL‑CAPS higher taxon. Save the PNG and include it.\n"
            "For lifespan or life‑history traits, call generate_mammal_report; read and summarize the report, and note AROCM (Average Rate of Change in Methylation) is inversely related to maximum lifespan.\n\n"
            "### Aging Clocks Module\n"
            "When asked about a gene across aging clocks, call: generate_horvath_gene_report, generate_hannum_gene_report (5 models), generate_phenoage_gene_report, generate_brunet_gene_report (mouse‑specific; warn against extrapolating to humans), and generate_gene_report_pdf (Wyss‑Coray). If the user says ‘any/all/some clocks’, invoke all five and synthesize.\n\n"
            "### Structural Bioinformatics Module\n"
            "For structures, call download_pdb_structures_for_protein(gene). Visualize with smart_visualize(pdb_file, …). Align with structural_alignment(pdb1, pdb2); estimate stability with compare_stability_simple(pdb_wt, pdb_mut).\n"
            "smart_visualize supports options: color_mode (monochrome/charge/hydrophobicity/lddt), style (cartoon/stick/line/sphere), show_sidechains, sidechain_style, show_surface (vdw/sas with opacity/color), chain selection, zoom, and viewer dimensions. Default: hydrophobicity coloring, show_sidechains, cartoon backbone, gray vdw surface at 0.7 opacity.\n\n"
            "### Mutation Impact Prediction\n"
            "For ‘How will this mutation affect the protein?’: run generate_comprehensive_prediction(protein_name, mutations) to automate: find_uniprot → apply_protein_mutations → compare_solubility_and_pI. Additionally, always check functional domains (get_uniprot_features) and existing human variation (get_gene_variants_excel). Summarize all outputs and clearly state this is a preliminary computational assessment, not a definitive biological conclusion.\n\n"
            "### Literature\n"
            "When making factual claims or drawing conclusions, attempt to cite 1–3 relevant primary papers. Use fetch_articles_structured or fetch_articles_detailed_log to gather PDFs and metadata when needed. Prefer concise in‑text citations like (Author et al., YEAR) with a short 'References' section listing title and a URL. Use artifacts_read_text to quote short excerpts from downloaded metadata or PDFs.\n\n"
            "### Operational constraints\n"
            "Heavy steps like full AlphaFold structure prediction may be unavailable by default in this environment. If a heavy step is not configured, gracefully skip it and explicitly note that it was skipped. smart_visualize relies on a CDN for 3Dmol.js.\n\n"
            "### Output requirements (strict)\n"
            "Respond in Markdown only; begin with a TL;DR (2–4 bullets). Use clear section headers (## Key findings, ## Evidence, ## What I did, ## References, ## Next steps). Prefer short paragraphs and bullet lists. If tools ran, list them with their output filenames. Don’t dump entire files—use artifacts_read_text to quote small excerpts. Where possible, include direct references to papers (title + URL) and cite them inline. Be concise, correct, and avoid redundancy."
        )

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
            norm_args = self._normalize_args(function_name, arguments)
            result = func(**norm_args)
            return result
        except Exception as e:
            return {"error": f"Error executing {function_name}: {str(e)}"}

    def _normalize_args(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Map legacy schema argument names to wrapper-friendly names.

        This allows us to use existing function_schemas while executing the
        artifact-registering wrappers which have slightly different signatures.
        """
        a = dict(args or {})

        def pick(keys, default=None):
            for k in keys:
                if k in a and a[k] is not None:
                    return a[k]
            return default

        if name == "find_uniprot":
            return {
                "gene": pick(["gene", "query", "gene_name"]) or "",
                "species": pick(["species", "organism"], "human"),
            }
        if name == "download_uniprot_fasta":
            return {
                "gene": pick(["gene", "gene_name", "query"]) or "",
                "species": pick(["species", "organism"], "human"),
                "output_file": pick(["output_file", "filename", "output", "output_excel", "output_png"], "protein.fasta"),
            }
        if name == "mutate_replace":
            return {
                "fasta_file": pick(["fasta_file", "gene", "input", "file"]) or "",
                "position": pick(["position", "pos"], 1),
                "new_aa": pick(["new_aa", "aa", "aa_new"]) or "A",
                "output_file": pick(["output_file", "output", "filename"], "mutated.fasta"),
            }
        if name == "mutate_delete":
            return {
                "fasta_file": pick(["fasta_file", "gene", "input", "file"]) or "",
                "start": pick(["start", "from", "pos"], 1),
                "end": pick(["end", "to"], pick(["start", "from", "pos"], 1)),
                "output_file": pick(["output_file", "output", "filename"], "mutated.fasta"),
            }
        if name == "mutate_insert":
            return {
                "fasta_file": pick(["fasta_file", "gene", "input", "file"]) or "",
                "position": pick(["position", "pos"], 1),
                "insert_seq": pick(["insert_seq", "ins_aa", "seq", "insert"]) or "G",
                "output_file": pick(["output_file", "output", "filename"], "mutated.fasta"),
            }
        if name == "mutate_truncate":
            return {
                "fasta_file": pick(["fasta_file", "gene", "input", "file"]) or "",
                "position": pick(["position", "pos"], 1),
                "output_file": pick(["output_file", "output", "filename"], "mutated.fasta"),
            }
        if name == "get_gene_variants_excel":
            return {
                "gene": pick(["gene", "query"]) or "",
                "output_file": pick(["output_file", "output_excel", "filename"], "variants.xlsx"),
            }
        if name == "plot_mammalian_tree":
            return {
                "species_list": pick(["species_list", "species", "list"], []) or [],
                "output_file": pick(["output_file", "output_png", "filename"], "mammal_tree.png"),
            }
        if name == "build_phylo_tree_nj":
            return {
                "aligned_fasta": pick(["aligned_fasta", "alignment_fasta", "input", "fasta"]) or "",
                "output_file": pick(["output_file", "output_prefix", "filename"], "tree_nj.png"),
            }
        if name == "build_phylo_tree_ml":
            return {
                "aligned_fasta": pick(["aligned_fasta", "alignment_fasta", "input", "fasta"]) or "",
                "output_file": pick(["output_file", "output_prefix", "filename"], "tree_ml.png"),
            }
        if name in {"generate_horvath_gene_report", "generate_phenoage_gene_report", "generate_brunet_gene_report", "generate_hannum_gene_report"}:
            return {
                "gene_query": pick(["gene_query", "gene", "gene_symbol", "query"]) or "",
                "output_dir": pick(["output_dir"], "."),
            }
        if name == "generate_mammal_report":
            return {
                "query": pick(["species_query", "query"]) or "",
                "output_dir": pick(["output_dir"], "."),
            }
        if name == "get_reactome_pathways":
            return {"query": pick(["query", "gene", "gene_symbol"]) or "", "save_report": bool(pick(["save_report"], True))}
        if name == "get_go_annotation":
            return {"query": pick(["query", "gene", "gene_symbol"]) or ""}
        if name == "get_drug_info":
            return {"query": pick(["query", "gene", "gene_symbol"]) or ""}
        if name == "get_uniprot_features":
            return {"gene": pick(["gene", "query", "gene_symbol"]) or "", "organism": pick(["organism", "species"], "human")}
        if name == "get_protein_function":
            return {"gene": pick(["gene", "query", "gene_symbol"]) or "", "organism": pick(["organism", "species"], "human")}
        if name == "generate_gene_report_pdf":
            return {
                "gene": pick(["gene", "query", "gene_symbol"]) or "",
                "output_file": pick(["output_file", "filename", "output"], "gene_report.pdf"),
            }
        if name in {"get_hpa_html", "fetch_and_extract_hpa"}:
            return {
                "gene": pick(["gene", "query", "gene_symbol"]) or "",
                "output_dir": pick(["output_dir"], "."),
            }
        if name == "apply_protein_mutations":
            muts = pick(["mutations"]) or []
            if isinstance(muts, str):
                # allow comma-separated string
                muts = [m.strip() for m in muts.split(",") if m.strip()]
            return {
                "fasta_file": pick(["fasta_file", "input", "file"]) or "",
                "mutations": muts,
                "output_file": pick(["output_file", "filename", "output"], "mutated.fasta"),
                "report_file": pick(["report_file", "report", "log"], "mutations_report.txt"),
            }
        if name == "compare_solubility_and_pI":
            return {
                "wt_fasta": pick(["wt_fasta", "wt", "wildtype", "wild_type"]) or "",
                "mut_fasta": pick(["mut_fasta", "mut", "mutant"]) or "",
                "output_file": pick(["output_file", "filename", "output"], "solubility_pI_comparison.txt"),
            }
        if name == "structural_alignment":
            return {
                "pdb1_path": pick(["pdb1_path", "pdb_ref", "ref"]) or "",
                "pdb2_path": pick(["pdb2_path", "pdb_mob", "mob"]) or "",
                "save_aligned": bool(pick(["save_aligned"], True)),
                "out1": pick(["out1", "aligned_ref"], "aligned_ref.pdb"),
                "out2": pick(["out2", "aligned_mob"], "aligned_mob.pdb"),
            }
        if name == "compare_stability_simple":
            return {
                "pdb_wt": pick(["pdb_wt", "wt", "ref"]) or "",
                "pdb_mut": pick(["pdb_mut", "mut", "mob"]) or "",
                "report_name": pick(["report_name", "output", "filename"], "stability_comparison.txt"),
            }
        if name == "download_pdb_structures_for_protein":
            return {
                "gene": pick(["gene", "protein_name", "query"]) or "",
                "organism": pick(["organism", "species"], "human"),
            }
        if name == "smart_visualize":
            return {
                "pdb_file": pick(["pdb_file", "pdb", "input"]) or "",
                "output_html": pick(["output_html", "output", "filename"], "viewer.html"),
                "background": pick(["background", "bg"], "white"),
            }
        if name in {"fetch_articles_structured", "fetch_articles_detailed_log"}:
            return {
                "query": pick(["query", "q"]) or "",
                "num_pdfs": int(pick(["num_pdfs", "pdfs"], 5)),
                "max_checked": int(pick(["max_checked", "max"], 300)),
                "delay": float(pick(["delay", "sleep"], 2.5)),
            }
        if name == "generate_comprehensive_prediction":
            muts = pick(["mutations"]) or []
            if isinstance(muts, str):
                muts = [m.strip() for m in muts.split(",") if m.strip()]
            return {
                "protein_name": pick(["protein_name", "gene", "query"]) or "",
                "mutations": muts,
            }
        # Default: pass through
        return a
    
    def chat(self, user_message: str, max_iterations: Optional[int] = None, pre_messages: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Send a message to the agent and get a response.
        
        The agent may make multiple function calls to answer the query.
        
        Args:
            user_message: User's question or request
            max_iterations: Maximum number of function calling iterations
            
        Returns:
            Agent's text response
        """
        # If upstream provided prior turns, seed them explicitly (avoids stuffing context into one user message)
        if pre_messages and isinstance(pre_messages, list):
            # Reset to system prompt only; server typically calls reset() per HTTP request, but be explicit here
            self.conversation_history = [{
                "role": "system",
                "content": self.system_prompt
            }]
            for m in pre_messages:
                try:
                    role = m.get("role")  # type: ignore[assignment]
                    content = m.get("content")  # type: ignore[assignment]
                except Exception:
                    continue
                if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                    self.conversation_history.append({"role": role, "content": content})

        # Add current user message at the end
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        limit = max_iterations if isinstance(max_iterations, int) and max_iterations > 0 else self.max_iterations_default
        iteration = 0
        while iteration < limit:
            iteration += 1
            
            # Prepare tool schemas (new-style tools API for GPT-5 and later)
            tools = [{"type": "function", "function": schema} for schema in ALL_SCHEMAS]

            # Call OpenAI API using tools API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=tools,
                tool_choice="auto",
            )
            
            message = response.choices[0].message
            
            # Handle tool/function calls
            tool_calls = getattr(message, "tool_calls", None)
            function_call = getattr(message, "function_call", None)

            # If neither tool calls nor function_call, we have the final answer
            if not tool_calls and not function_call:
                assistant_message = message.content or ""
                # Optional post-format if content is a single block
                if not self._looks_well_formatted(assistant_message):
                    try:
                        assistant_message = self._format_markdown(assistant_message)
                    except Exception:
                        pass
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                return assistant_message
            
            # New tools API path: may include multiple tool calls
            if tool_calls:
                # Record assistant message with tool_calls (content may be None)
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                        }
                        for tc in tool_calls
                    ],
                })

                # Execute each tool call and append tool results
                for tc in tool_calls:
                    fn_name = tc.function.name
                    try:
                        fn_args = json.loads(tc.function.arguments or "{}")
                    except Exception:
                        fn_args = {}
                    result = self._execute_function(fn_name, fn_args)
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, default=str),
                    })
                # Continue next iteration so the model can see tool outputs
                continue

            # Legacy function_call path (for older models)
            if function_call:
                function_name = function_call.name
                function_args = json.loads(function_call.arguments)
                
                # Record assistant call
                self.conversation_history.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": function_call.arguments,
                    },
                })
                
                function_result = self._execute_function(function_name, function_args)
                
                # Provide function result back (legacy requires role=function)
                self.conversation_history.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result, default=str),
                })
                continue
        
        # If we hit max iterations, return a message
        return "I apologize, but I've reached my maximum number of tool calls. Please try breaking your request into smaller parts or increase LLM_MAX_TOOL_ITERATIONS."
    
    def reset(self):
        """Reset conversation history."""
        self.conversation_history = [{
            "role": "system",
            "content": self.system_prompt
        }]

    def get_tools_used(self) -> List[str]:
        """Return a de-duplicated, in-order list of tool/function names used in the last chat run.

        This inspects conversation_history entries recorded during the most recent chat call,
        collecting names from both the new tools API (tool_calls) and legacy function_call path.
        """
        names: List[str] = []
        for m in self.conversation_history:
            try:
                # New tools API structure
                if isinstance(m, dict) and isinstance(m.get("tool_calls"), list):
                    for tc in m["tool_calls"]:
                        fn = None
                        if isinstance(tc, dict):
                            f = tc.get("function")
                            if isinstance(f, dict):
                                fn = f.get("name")
                        if fn and fn not in names:
                            names.append(fn)
                # Legacy function_call
                fc = m.get("function_call") if isinstance(m, dict) else None
                if isinstance(fc, dict):
                    fn = fc.get("name")
                    if fn and fn not in names:
                        names.append(fn)
            except Exception:
                continue
        return names

    def _looks_well_formatted(self, text: str) -> bool:
        """Heuristic: check for TL;DR bullets or section headers to decide if reformat is needed."""
        if not text:
            return False
        has_header = "\n## " in text or text.startswith("## ")
        has_bullets = "\n- " in text or "\n* " in text
        return has_header and has_bullets

    def _format_markdown(self, text: str) -> str:
        """Ask the model to restructure a block of text into concise Markdown.

        Keeps content, adds TL;DR bullets, section headers, and short paragraphs.
        """
        prompt = (
            "Rewrite the following answer into concise Markdown with: a TL;DR (2–4 bullets), "
            "clear section headers (## Key findings, ## Evidence, ## What I did, ## Next steps), "
            "short paragraphs and bullet lists; do not invent facts; do not remove any file names; keep links if present."
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise editor that formats content only."},
                {"role": "user", "content": prompt + "\n\n---\n\n" + (text or "")}],
            temperature=0.2,
        )
        return resp.choices[0].message.content or text


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
