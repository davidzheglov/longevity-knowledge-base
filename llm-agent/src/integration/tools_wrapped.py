"""
Agents SDK wrappers for llm-agent tools.
Each wrapper is decorated with @function_tool so it can be called by an Agent.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Dict, List, Optional

from agents import function_tool

# Ensure we can import llm-agent tools when running from repo root
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tools import (
    initialize_gene_map,
    normalize_gene as _normalize_gene,
    find_uniprot as _find_uniprot,
    download_uniprot_fasta as _download_uniprot_fasta,
    mutate_replace as _mutate_replace,
    mutate_delete as _mutate_delete,
    mutate_insert as _mutate_insert,
    mutate_truncate as _mutate_truncate,
    get_gene_variants_excel as _get_gene_variants_excel,
    pairwise_protein_alignment as _pairwise_protein_alignment,
    msa_mafft as _msa_mafft,
    plot_mammalian_tree as _plot_mammalian_tree,
    build_phylo_tree_nj as _build_phylo_tree_nj,
    build_phylo_tree_ml as _build_phylo_tree_ml,
    generate_horvath_gene_report as _generate_horvath_gene_report,
    generate_phenoage_gene_report as _generate_phenoage_gene_report,
    generate_brunet_gene_report as _generate_brunet_gene_report,
    generate_hannum_gene_report as _generate_hannum_gene_report,
    generate_mammal_report as _generate_mammal_report,
    get_reactome_pathways as _get_reactome_pathways,
    get_go_annotation as _get_go_annotation,
    get_drug_info as _get_drug_info,
    get_uniprot_features as _get_uniprot_features,
    get_protein_function as _get_protein_function,
    fetch_and_extract_hpa as _fetch_and_extract_hpa,
    generate_gene_report_pdf as _generate_gene_report_pdf,
)

# Artifacts registry utilities
from integration.artifacts import (
    start_session as _start_artifact_session,
    get_run_dir as _get_run_dir,
    register_artifact as _register_artifact,
    list_artifacts as _list_artifacts,
    resolve_artifact as _resolve_artifact,
    search_artifacts as _search_artifacts,
    ensure_unique_path as _ensure_unique_path,
)

# Convenience bootstrap to make sure gene map is loaded by default

def bootstrap_data():
    data_dir = Path(__file__).resolve().parents[2] / "data"
    gene_file = data_dir / "gene_info.txt"
    try:
        initialize_gene_map(str(gene_file))
    except Exception:
        # Fallback to default inside tools if available
        try:
            initialize_gene_map()
        except Exception:
            pass
    # Ensure a session run dir exists for this process without resetting any existing session
    # Touch current run dir so helpers work, but do NOT start a new session here.
    _get_run_dir()


# ============== Gene and Protein Tools ==============

@function_tool
def normalize_gene(query: Annotated[str, "Gene name, symbol, alias, or Entrez ID"] ) -> str:
    """Normalize a gene query to a canonical symbol and IDs. Returns plain text only."""
    d = _normalize_gene(query)
    if not d:
        return f"No match for '{query}'."
    aliases = d.get("other_names", []) or []
    alias_str = ", ".join(aliases[:6])
    return (
        f"Canonical: {d.get('canonical_symbol')}\n"
        f"Entrez: {d.get('entrez_id')} | HGNC: {d.get('hgnc_id')} | Ensembl: {d.get('ensembl_id')}\n"
        f"Aliases: {alias_str}"
    )


@function_tool
def find_uniprot(gene: Annotated[str, "Gene symbol"], species: Annotated[str, "Species name"] = "human") -> str:
    """Search UniProt for protein entries by gene and species and return a brief text summary."""
    data = _find_uniprot(gene, species, save_to_file=False)
    if not data or data.get("error"):
        return f"No reviewed UniProt entry found for {gene} in {species}."
    aliases = ", ".join(data.get("all_known_names", [])[:5])
    return (
        f"Gene: {data.get('canonical_symbol')} | UniProt: {data.get('uniprot_id')}\n"
        f"Protein: {data.get('canonical_name')}\n"
        f"Aliases: {aliases}"
    )


@function_tool
def download_uniprot_fasta(gene: Annotated[str, "Gene symbol"], species: Annotated[str, "Species name"] = "human", output_file: Annotated[str, "Output FASTA filename"] = "protein.fasta") -> str:
    """Download protein FASTA from UniProt and save to file. Returns the saved path as text."""
    # Normalize to run_dir and ensure unique filename
    run_dir = _get_run_dir()
    desired = run_dir / Path(output_file).name
    safe_path = _ensure_unique_path(str(desired))
    # Underlying tool may accept directory; pass parent directory if needed
    path = _download_uniprot_fasta(gene, species, str(Path(safe_path).parent))
    final_path = path if path else None
    if final_path and Path(final_path).exists():
        _register_artifact(final_path, type="fasta", label=f"{gene}_fasta")
        return f"Saved FASTA to: {final_path}"
    return "FASTA download failed."


# ============== Mutation Tools ==============

@function_tool
def mutate_replace(fasta_file: Annotated[str, "Input FASTA file"], position: Annotated[int, "1-indexed position"], new_aa: Annotated[str, "New amino acid"], output_file: Annotated[str, "Output FASTA file"] = "mutated.fasta") -> str:
    # If path exists, modify in-place from file contents; otherwise treat as gene symbol
    run_dir = _get_run_dir()
    out = run_dir / Path(output_file).name
    out = _ensure_unique_path(str(out))
    p = Path(fasta_file)
    if p.exists():
        seq = p.read_text(encoding="utf-8")
        lines = [l.strip() for l in seq.splitlines() if l.strip()]
        if not lines or not lines[0].startswith(">"):
            return f"Invalid FASTA file: {fasta_file}"
        header = lines[0]
        seqs = "".join(lines[1:])
        idx = position - 1
        if idx < 0 or idx >= len(seqs):
            return f"Position {position} out of range (len={len(seqs)})"
        new_seq = seqs[:idx] + new_aa + seqs[idx+1:]
        Path(out).write_text(f"{header} | REPL {position}{seqs[idx]}>{new_aa}\n{new_seq}", encoding="utf-8")
        _register_artifact(str(out), type="fasta", label=f"mut_replace_{position}")
        return f"Saved mutated FASTA to: {out}"
    # Fallback to gene-based
    saved = _mutate_replace(fasta_file, position, new_aa, str(run_dir))
    _register_artifact(saved, type="fasta", label=f"mut_replace_{position}")
    return f"Saved mutated FASTA to: {saved}"


@function_tool
def mutate_delete(fasta_file: Annotated[str, "Input FASTA file"], start: Annotated[int, "Start position (1-indexed)"], end: Annotated[int, "End position (inclusive)"], output_file: Annotated[str, "Output FASTA file"] = "mutated.fasta") -> str:
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(run_dir / Path(output_file).name))
    p = Path(fasta_file)
    if p.exists():
        lines = [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lines or not lines[0].startswith(">"):
            return f"Invalid FASTA file: {fasta_file}"
        header = lines[0]
        seqs = "".join(lines[1:])
        s = start - 1
        e = end - 1
        if s < 0 or e >= len(seqs) or s > e:
            return f"Invalid range {start}-{end} for len={len(seqs)}"
        deleted = seqs[s:e+1]
        new_seq = seqs[:s] + seqs[e+1:]
        Path(out).write_text(f"{header} | DEL {start}-{end}:{deleted}\n{new_seq}", encoding="utf-8")
        _register_artifact(str(out), type="fasta", label=f"mut_delete_{start}_{end}")
        return f"Saved mutated FASTA to: {out}"
    saved = _mutate_delete(fasta_file, start, str(run_dir))  # type: ignore[arg-type]
    _register_artifact(saved, type="fasta", label=f"mut_delete_{start}_{end}")
    return f"Saved mutated FASTA to: {saved}"


@function_tool
def mutate_insert(fasta_file: Annotated[str, "Input FASTA file"], position: Annotated[int, "Insert after position (1-indexed)"], insert_seq: Annotated[str, "Sequence to insert"], output_file: Annotated[str, "Output FASTA file"] = "mutated.fasta") -> str:
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(run_dir / Path(output_file).name))
    p = Path(fasta_file)
    if p.exists():
        lines = [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lines or not lines[0].startswith(">"):
            return f"Invalid FASTA file: {fasta_file}"
        header = lines[0]
        seqs = "".join(lines[1:])
        idx = position
        if idx < 0 or idx > len(seqs):
            return f"Insert position {position} invalid for len={len(seqs)}"
        new_seq = seqs[:idx] + insert_seq + seqs[idx:]
        Path(out).write_text(f"{header} | INS after {position}:{insert_seq}\n{new_seq}", encoding="utf-8")
        _register_artifact(str(out), type="fasta", label=f"mut_insert_{position}")
        return f"Saved mutated FASTA to: {out}"
    saved = _mutate_insert(fasta_file, position, insert_seq, str(run_dir))
    _register_artifact(saved, type="fasta", label=f"mut_insert_{position}")
    return f"Saved mutated FASTA to: {saved}"


@function_tool
def mutate_truncate(fasta_file: Annotated[str, "Input FASTA file"], position: Annotated[int, "Truncate at position (1-indexed)"], output_file: Annotated[str, "Output FASTA file"] = "mutated.fasta") -> str:
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(run_dir / Path(output_file).name))
    p = Path(fasta_file)
    if p.exists():
        lines = [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lines or not lines[0].startswith(">"):
            return f"Invalid FASTA file: {fasta_file}"
        header = lines[0]
        seqs = "".join(lines[1:])
        if position < 1 or position > len(seqs):
            return f"Position {position} out of range (len={len(seqs)})"
        new_seq = seqs[:position]
        Path(out).write_text(f"{header} | TRUNCATED after {position}\n{new_seq}", encoding="utf-8")
        _register_artifact(str(out), type="fasta", label=f"mut_truncate_{position}")
        return f"Saved mutated FASTA to: {out}"
    saved = _mutate_truncate(fasta_file, position, str(run_dir))
    _register_artifact(saved, type="fasta", label=f"mut_truncate_{position}")
    return f"Saved mutated FASTA to: {saved}"


# ============== Alignment and Phylogeny ==============

@function_tool
def pairwise_protein_alignment(fasta1: Annotated[str, "First FASTA"], fasta2: Annotated[str, "Second FASTA"], output_file: Annotated[str, "Output file"] = "alignment.txt") -> str:
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(run_dir / Path(output_file).name))
    d = _pairwise_protein_alignment(fasta1, fasta2, str(out))
    if not isinstance(d, dict):
        _register_artifact(str(out), type="txt", label="pairwise_alignment")
        return f"Pairwise alignment complete. Saved to: {out}"
    if d.get("error"):
        return f"Pairwise alignment failed: {d.get('error')}"
    score = d.get("score")
    _register_artifact(str(out), type="txt", label="pairwise_alignment")
    return f"Pairwise alignment complete. Score: {score}. Saved to: {out}"


@function_tool
def msa_mafft(input_fasta: Annotated[str, "Input multi-FASTA"], output_file: Annotated[str, "Output aligned FASTA"] = "aligned.fasta") -> str:
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(run_dir / Path(output_file).name))
    res = _msa_mafft(input_fasta, str(out))
    if isinstance(res, str) and Path(res).exists():
        _register_artifact(res, type="fasta", label="msa_mafft")
    return res


@function_tool
def build_phylo_tree_nj(aligned_fasta: Annotated[str, "Aligned FASTA"], output_file: Annotated[str, "Output image"] = "tree_nj.png") -> str:
    run_dir = _get_run_dir()
    p = Path(aligned_fasta)
    if not p.exists():
        return f"Aligned FASTA not found: {aligned_fasta}. Please run MSA first."
    out = _ensure_unique_path(str(run_dir / Path(output_file).name))
    res = _build_phylo_tree_nj(aligned_fasta, str(out))
    if isinstance(res, str) and Path(res).exists():
        _register_artifact(res, type="png", label="tree_nj")
    return res


@function_tool
def build_phylo_tree_ml(aligned_fasta: Annotated[str, "Aligned FASTA"], output_file: Annotated[str, "Output image"] = "tree_ml.png") -> str:
    run_dir = _get_run_dir()
    p = Path(aligned_fasta)
    if not p.exists():
        return f"Aligned FASTA not found: {aligned_fasta}. Please run MSA first."
    out = _ensure_unique_path(str(run_dir / Path(output_file).name))
    res = _build_phylo_tree_ml(aligned_fasta, str(out))
    if isinstance(res, str) and Path(res).exists():
        _register_artifact(res, type="png", label="tree_ml")
    return res


@function_tool
def plot_mammalian_tree(species_list: Annotated[List[str], "Species list"], output_file: Annotated[str, "Output image"] = "mammal_tree.png") -> str:
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(run_dir / Path(output_file).name))
    res = _plot_mammalian_tree(species_list, str(out))
    if isinstance(res, str) and Path(res).exists():
        _register_artifact(res, type="png", label="mammal_tree")
    return res


# ============== Aging Clocks ==============

@function_tool
def generate_horvath_gene_report(gene_query: Annotated[str, "Gene"], output_dir: Annotated[str, "Output dir"] = ".") -> str:
    run_dir = _get_run_dir()
    # Always save into session directory
    path = _generate_horvath_gene_report(gene_query, output_dir=str(run_dir))
    if not path or not Path(path).exists():
        return f"Horvath report failed for {gene_query}."
    _register_artifact(path, type="txt", label=f"Horvath_{gene_query}")
    return f"Horvath report saved to: {path}"


@function_tool
def generate_phenoage_gene_report(gene_query: Annotated[str, "Gene"], output_dir: Annotated[str, "Output dir"] = ".") -> str:
    run_dir = _get_run_dir()
    path = _generate_phenoage_gene_report(gene_query, output_dir=str(run_dir))
    if not path or not Path(path).exists():
        return f"PhenoAge report failed for {gene_query}."
    _register_artifact(path, type="txt", label=f"PhenoAge_{gene_query}")
    return f"PhenoAge report saved to: {path}"


@function_tool
def generate_brunet_gene_report(gene_query: Annotated[str, "Gene"], output_dir: Annotated[str, "Output dir"] = ".") -> str:
    run_dir = _get_run_dir()
    path = _generate_brunet_gene_report(gene_query, output_dir=str(run_dir))
    # Underlying function returns a dict or a path depending on implementation; register any file it created.
    if isinstance(path, str) and Path(path).exists():
        _register_artifact(path, type="txt", label=f"Brunet_{gene_query}")
        return f"Brunet report saved to: {path}"
    # If dict returned, attempt to save a compact report into run_dir
    if isinstance(path, dict):
        out = Path(run_dir) / f"Brunet_Report_{gene_query}.txt"
        out = _ensure_unique_path(str(out))
        lines = [f"Brunet report for {gene_query}"]
        tops = path.get("top_hits", []) if isinstance(path, dict) else []
        for hit in tops[:20]:
            lines.append(str(hit))
        Path(out).write_text("\n".join(lines), encoding="utf-8")
        _register_artifact(str(out), type="txt", label=f"Brunet_{gene_query}")
        return f"Brunet report saved to: {out}"
    return f"Brunet report failed for {gene_query}."


@function_tool
def generate_hannum_gene_report(gene_query: Annotated[str, "Gene"], output_dir: Annotated[str, "Output dir"] = ".") -> str:
    run_dir = _get_run_dir()
    path = _generate_hannum_gene_report(gene_query, output_dir=str(run_dir))
    if not path or not Path(path).exists():
        return f"Hannum report failed for {gene_query}."
    _register_artifact(path, type="txt", label=f"Hannum_{gene_query}")
    return f"Hannum report saved to: {path}"


# ============== Longevity and Mammal Data ==============

@function_tool
def generate_mammal_report(query: Annotated[str, "Species name"], output_dir: Annotated[str, "Output dir"] = ".") -> str:
    run_dir = _get_run_dir()
    path = _generate_mammal_report(query, output_dir=str(run_dir))
    if not path or not Path(path).exists():
        return f"Mammal report failed for '{query}'."
    _register_artifact(path, type="txt", label=f"mammal_{query}")
    return f"Mammal report saved to: {path}"


# ============== UniProt and HPA ==============

@function_tool
def get_reactome_pathways(query: Annotated[str, "Gene"], save_report: Annotated[bool, "Save report"] = True, verbose: Annotated[bool, "Verbose"] = False) -> str:
    # Generate rows without letting the underlying util write to CWD
    rows = _get_reactome_pathways(query, save_report=False, verbose=verbose)
    if not rows:
        return f"No Reactome pathways found for {query}."
    # Save a succinct report into the session directory
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(Path(run_dir) / f"{query}_Reactome.txt"))
    with Path(out).open("w", encoding="utf-8") as f:
        for r in rows:
            pid = r.get('id') or r.get('pathway_id') or '?'
            name = r.get('name') or r.get('pathway_name') or ''
            f.write(f"{pid}: {name}\n")
    _register_artifact(str(out), type="txt", label=f"Reactome_{query}")
    return f"Reactome report saved to: {out}"


@function_tool
def get_go_annotation(query: Annotated[str, "Gene"], verbose: Annotated[bool, "Verbose"] = True) -> str:
    rows = _get_go_annotation(query, verbose)
    if not rows:
        return f"No GO annotations found for {query}."
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(Path(run_dir) / f"{query}_GO.txt"))
    with Path(out).open("w", encoding="utf-8") as f:
        f.write(f"Gene: {query}\n")
        for r in rows:
            cat = r.get('category') or r.get('type') or ''
            gid = r.get('go_id') or r.get('id') or ''
            term = r.get('term') or r.get('name') or ''
            f.write(f"{cat}\t{gid}\t{term}\n")
    _register_artifact(str(out), type="txt", label=f"GO_{query}")
    return f"GO report saved to: {out}"


@function_tool
def get_drug_info(query: Annotated[str, "Gene"], verbose: Annotated[bool, "Verbose"] = True) -> str:
    rows = _get_drug_info(query, verbose)
    if not rows:
        return f"No drug info found for {query}."
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(Path(run_dir) / f"{query}_Drugs.txt"))
    with Path(out).open("w", encoding="utf-8") as f:
        f.write(f"Gene: {query}\n")
        for r in rows:
            did = r.get('drugbank_id') or r.get('id') or ''
            name = r.get('drug_name') or r.get('name') or 'Unknown'
            f.write(f"{did}: {name}\n")
    _register_artifact(str(out), type="txt", label=f"Drugs_{query}")
    return f"Drug report saved to: {out}"


@function_tool
def get_uniprot_features(query: Annotated[str, "Gene"], verbose: Annotated[bool, "Verbose"] = True) -> str:
    d = _get_uniprot_features(query, verbose)
    if not d or (isinstance(d, dict) and d.get("error")):
        return f"Could not fetch UniProt features for {query}."
    feats = d.get("features", []) if isinstance(d, dict) else []
    return f"Found {len(feats)} UniProt features for {query}."


@function_tool
def get_protein_function(gene: Annotated[str, "Gene"], organism: Annotated[str, "Organism"] = "human") -> str:
    data = _get_protein_function(gene, organism)
    if not data or data.get("error"):
        return f"Could not retrieve protein function for {gene} ({organism})."
    fn = data.get("function") or data.get("summary") or "(no function text)"
    return f"{gene} ({organism}) protein function:\n{fn}"


@function_tool
def fetch_and_extract_hpa(query: Annotated[str, "Gene"], output_dir: Annotated[str, "Output dir"] = ".") -> str:
    run_dir = _get_run_dir()
    path = _fetch_and_extract_hpa(query, str(run_dir))
    if path:
        _register_artifact(path, type="txt", label=f"HPA_{query}")
        return f"HPA data saved to: {path}"
    return "HPA fetch failed."


# ============== Variants & Proteomics ==============

@function_tool
def get_gene_variants_excel(gene: Annotated[str, "Gene"], output_file: Annotated[str, "Output Excel"] = "variants.xlsx") -> str:
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(run_dir / Path(output_file).name))
    res = _get_gene_variants_excel(gene, str(out))
    if isinstance(res, str) and Path(res).exists():
        _register_artifact(res, type="xlsx", label=f"variants_{gene}")
    return res


@function_tool
def generate_gene_report_pdf(gene: Annotated[str, "Gene"], output_file: Annotated[str, "Output PDF"] = "gene_report.pdf") -> str:
    run_dir = _get_run_dir()
    out = _ensure_unique_path(str(run_dir / Path(output_file).name))
    data = _generate_gene_report_pdf(gene, str(out))
    if isinstance(data, dict) and data.get("error"):
        return f"PDF gene report failed for {gene}."
    _register_artifact(str(out), type="pdf", label=f"pdf_{gene}")
    return f"PDF gene report saved to {out}."


ALL_TOOLS = [
    normalize_gene,
    find_uniprot,
    download_uniprot_fasta,
    mutate_replace,
    mutate_delete,
    mutate_insert,
    mutate_truncate,
    pairwise_protein_alignment,
    msa_mafft,
    build_phylo_tree_nj,
    build_phylo_tree_ml,
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
    fetch_and_extract_hpa,
    get_gene_variants_excel,
    generate_gene_report_pdf,
]


# ============== Artifact helper tools ==============

@function_tool
def artifacts_list(artifact_type: Annotated[Optional[str], "Filter by type (e.g., fasta, png, xlsx)" ] = None) -> str:
    items = _list_artifacts(artifact_type)
    if not items:
        return "No artifacts recorded."
    lines = ["Artifacts:"]
    for it in items:
        lines.append(f"- {it['id']} [{it['type']}] {it['path']} {('('+it['label']+')') if it.get('label') else ''}")
    return "\n".join(lines)


@function_tool
def artifacts_resolve(id_or_label: Annotated[str, "Artifact id or label"]) -> str:
    p = _resolve_artifact(id_or_label)
    return p or "Artifact not found."


@function_tool
def artifacts_search(name_substring: Annotated[str, "Case-insensitive substring of filename"]) -> str:
    items = _search_artifacts(name_substring)
    if not items:
        return "No matching artifacts."
    lines = ["Matches:"]
    for it in items:
        lines.append(f"- {it['id']} [{it['type']}] {it['path']} {('('+it['label']+')') if it.get('label') else ''}")
    return "\n".join(lines)
