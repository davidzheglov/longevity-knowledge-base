import requests
import sys
import json
from typing import List, Dict, Optional
from collections import defaultdict


def get_reactome_pathways(query: str, save_report: bool = True, verbose: bool = False) -> List[Dict[str, str]]:
    """
    Extracts Reactome pathways for a human gene and saves report to file.
    
    Args:
        query: Gene name (e.g., "SOX2", "Oct4")
        save_report: Whether to save report to file
        verbose: Enable detailed logging
    
    Returns:
        List of dictionaries with keys 'id', 'name'
    """
    def log(msg):
        if verbose:
            print(f"[Reactome] {msg}", file=sys.stderr)

    query = query.strip()
    if not query:
        return []

    # Import normalize_gene here to avoid circular import
    try:
        from .gene_normalization import normalize_gene
        normalized = normalize_gene(query)
        canonical_query = normalized["canonical_symbol"] if normalized else query
    except Exception:
        canonical_query = query

    # Search UniProt
    organism_filter = "organism_id:9606"
    search_url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"(gene_exact:{canonical_query} OR gene:{canonical_query}) AND {organism_filter} AND reviewed:true",
        "fields": "xref_reactome,accession",
        "format": "json",
        "size": 1
    }

    try:
        resp = requests.get(search_url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("results"):
            return []
        entry = data["results"][0]
    except Exception:
        return []

    # Extract Reactome
    xrefs = entry.get("uniProtKBCrossReferences", [])
    reactome_entries = [x for x in xrefs if x.get("database") == "Reactome"]
    pathways = []

    for xref in reactome_entries:
        pathway_id = xref.get("id")
        if not pathway_id:
            continue

        # Get name from UniProt
        name = ""
        props = xref.get("properties", [])
        if isinstance(props, dict):
            name = props.get("pathwayName", "")
        elif isinstance(props, list):
            for p in props:
                if isinstance(p, dict) and p.get("key") == "pathwayName":
                    name = p.get("value", "")
                    break

        # If no name, query Reactome API
        if not name.strip():
            try:
                r_resp = requests.get(
                    f"https://reactome.org/ContentService/data/query/{pathway_id}",
                    headers={"Accept": "application/json"},
                    timeout=10
                )
                if r_resp.status_code == 200:
                    r_data = r_resp.json()
                    name = r_data.get("displayName", "").strip()
            except Exception:
                pass

        pathways.append({"id": pathway_id, "name": name})

    # Save report
    if save_report and pathways:
        symbol = canonical_query
        report_file = f"{symbol}_Reactome.txt"
        try:
            with open(report_file, "w") as f:
                for p in pathways:
                    f.write(f"{p['id']}: {p['name']}\n")
            log(f"✅ Report saved: {report_file}")
        except Exception as e:
            log(f"⚠️ Failed to save report: {e}")

    return pathways


def get_go_annotation(query: str, verbose: bool = True) -> List[Dict[str, str]]:
    """
    Downloads UniProt JSON for a human gene and extracts GO annotations.
    Saves report as {symbol}_GO.txt.
    
    Args:
        query: Gene symbol, alias, or Entrez ID
        verbose: Enable detailed logging
    
    Returns:
        List of GO annotations with keys: category, go_id, term, evidence
    """
    def log(msg):
        if verbose:
            print(f"[GO] {msg}", file=sys.stderr)

    query = query.strip()
    if not query:
        log("❌ Empty query.")
        return []

    # Normalize gene name
    try:
        from .gene_normalization import normalize_gene
        normalized = normalize_gene(query)
        symbol = normalized["canonical_symbol"] if normalized else query
        log(f"✅ Normalized: '{query}' → '{symbol}'")
    except Exception as e:
        log(f"⚠️ Normalization error: {e}")
        symbol = query

    # Search UniProt accession
    search_url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"gene_exact:{symbol} AND organism_id:9606 AND reviewed:true",
        "fields": "accession",
        "format": "json",
        "size": 1
    }

    log(f"🔍 Searching UniProt accession for '{symbol}'...")
    try:
        resp = requests.get(search_url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log(f"❌ Failed to fetch accession: {e}")
        return []

    if not data.get("results"):
        log("❌ No reviewed UniProt entry found for this gene in human.")
        return []

    acc = data["results"][0]["primaryAccession"]
    log(f"🧬 Found accession: {acc}")

    # Download full JSON record
    json_url = f"https://rest.uniprot.org/uniprotkb/{acc}.json"
    log(f"📥 Fetching full record: {json_url}")
    try:
        full_resp = requests.get(json_url, timeout=15)
        full_resp.raise_for_status()
        full_data = full_resp.json()
    except Exception as e:
        log(f"❌ Failed to download JSON: {e}")
        return []

    # Extract GO annotations
    go_entries = []
    xrefs = full_data.get("uniProtKBCrossReferences", [])
    for ref in xrefs:
        if ref.get("database") == "GO":
            go_id = ref.get("id")
            properties = {prop["key"]: prop["value"] for prop in ref.get("properties", [])}
            go_term_full = properties.get("GoTerm")
            evidence = properties.get("GoEvidenceType", "N/A")

            if not go_id or not go_term_full or ":" not in go_term_full:
                continue

            prefix, term = go_term_full.split(":", 1)
            category = {
                "F": "Molecular Function",
                "P": "Biological Process",
                "C": "Cellular Component"
            }.get(prefix, "Other")

            go_entries.append({
                "category": category,
                "go_id": go_id,
                "term": term,
                "evidence": evidence
            })

    # Save GO report
    output_file = f"{symbol}_GO.txt"
    grouped = defaultdict(list)
    for entry in go_entries:
        grouped[entry["category"]].append(entry)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Gene: {symbol}\n")
            f.write(f"UniProt Accession: {full_data.get('primaryAccession', 'N/A')}\n")
            f.write("=" * 60 + "\n\n")

            for cat in ["Molecular Function", "Biological Process", "Cellular Component", "Other"]:
                if cat in grouped:
                    f.write(f"## {cat}\n")
                    for item in grouped[cat]:
                        f.write(f"{item['go_id']}: {item['term']}\n")
                    f.write("\n")

            if not go_entries:
                f.write("No GO annotations found.\n")

        log(f"✅ GO report saved to: {output_file}")
    except Exception as e:
        log(f"⚠️ Failed to write GO report: {e}")

    return go_entries


def get_drug_info(query: str, verbose: bool = True) -> List[Dict[str, str]]:
    """
    Fetches DrugBank drug annotations for a human gene from UniProt.
    Saves a report as {symbol}_Drugs.txt.
    
    Args:
        query: Gene symbol, alias, or Entrez ID
        verbose: Enable detailed logging
    
    Returns:
        List of drugs with keys: drugbank_id, drug_name
    """
    def log(msg):
        if verbose:
            print(f"[DRUG] {msg}", file=sys.stderr)

    query = query.strip()
    if not query:
        log("❌ Empty query.")
        return []

    # Normalize gene name
    try:
        from .gene_normalization import normalize_gene
        normalized = normalize_gene(query)
        symbol = normalized["canonical_symbol"] if normalized else query
        log(f"✅ Normalized: '{query}' → '{symbol}'")
    except Exception as e:
        log(f"⚠️ Normalization error: {e}")
        symbol = query

    # Search UniProt accession
    search_url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"gene_exact:{symbol} AND organism_id:9606 AND reviewed:true",
        "fields": "accession",
        "format": "json",
        "size": 1
    }

    log(f"🔍 Searching UniProt accession for '{symbol}'...")
    try:
        resp = requests.get(search_url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log(f"❌ Failed to fetch accession: {e}")
        return []

    if not data.get("results"):
        log("❌ No reviewed UniProt entry found for this gene in human.")
        return []

    acc = data["results"][0]["primaryAccession"]
    log(f"🧬 Found accession: {acc}")

    # Download full JSON record
    json_url = f"https://rest.uniprot.org/uniprotkb/{acc}.json"
    log(f"📥 Fetching full record: {json_url}")
    try:
        full_resp = requests.get(json_url, timeout=15)
        full_resp.raise_for_status()
        full_data = full_resp.json()
    except Exception as e:
        log(f"❌ Failed to download JSON: {e}")
        return []

    # Extract DrugBank entries
    drug_entries = []
    xrefs = full_data.get("uniProtKBCrossReferences", [])
    for ref in xrefs:
        if ref.get("database") == "DrugBank":
            drugbank_id = ref.get("id")
            if not drugbank_id:
                continue
            properties = {prop["key"]: prop["value"] for prop in ref.get("properties", [])}
            drug_name = properties.get("GenericName") or properties.get("BrandName") or "N/A"
            drug_entries.append({
                "drugbank_id": drugbank_id,
                "drug_name": drug_name
            })

    # Save drug report
    output_file = f"{symbol}_Drugs.txt"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Gene: {symbol}\n")
            f.write(f"UniProt Accession: {full_data.get('primaryAccession', 'N/A')}\n")
            f.write("=" * 60 + "\n\n")

            if drug_entries:
                f.write("## DrugBank Annotations\n")
                for drug in drug_entries:
                    f.write(f"{drug['drugbank_id']}: {drug['drug_name']}\n")
                f.write("\n")
            else:
                f.write("No DrugBank annotations found.\n")

        log(f"✅ Drug report saved to: {output_file}")
    except Exception as e:
        log(f"⚠️ Failed to write drug report: {e}")

    return drug_entries
