"""
Protein Sequence Module
Functions for fetching protein sequences from UniProt for human and other organisms.
"""

import requests
import os
import re
from typing import Dict, Any, Optional
from urllib.parse import quote


def find_uniprot(query: str, organism: str = "human", save_to_file: bool = True, 
                 output_dir: str = "outputs") -> Dict[str, Any]:
    """
    Find and download UniProt protein sequence for a gene.
    
    Args:
        query: Gene symbol or name
        organism: Target organism ("human" or taxon ID or organism name)
        save_to_file: Whether to save FASTA file
        output_dir: Directory to save output files
        
    Returns:
        Dictionary containing:
        - canonical_symbol: Gene symbol
        - canonical_name: Protein name
        - uniprot_id: UniProt accession
        - entrez_id: Entrez Gene ID (if available)
        - fasta: FASTA sequence string
        - all_known_names: List of all aliases
        - source: Data source description
        - fasta_file: Path to saved file (if save_to_file=True)
        - error: Error message (if failed)
    """
    from .gene_normalization import normalize_gene
    
    query = query.strip()
    if not query:
        return {"error": "Empty query"}
    
    # Normalize query
    normalized = normalize_gene(query)
    canonical_query = normalized["canonical_symbol"] if normalized else query
    
    # Determine organism filter
    if organism == "human":
        organism_filter = "organism_id:9606"
    elif organism.isdigit():
        organism_filter = f"organism_id:{organism}"
    else:
        organism_filter = f"organism_name:{organism}"
    
    # 1. Primary: UniProt (reviewed)
    uniprot_search_url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"(gene_exact:{canonical_query} OR gene:{canonical_query} OR protein_name:{canonical_query} OR alt_name:{canonical_query}) AND {organism_filter} AND reviewed:true",
        "fields": "accession,genes(PREFERRED,ALL),protein_name",
        "format": "json",
        "size": 1
    }
    
    try:
        resp = requests.get(uniprot_search_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("results"):
            entry = data["results"][0]
            acc = entry["primaryAccession"]
            
            # Get FASTA
            fasta_resp = requests.get(f"https://rest.uniprot.org/uniprotkb/{acc}.fasta", timeout=10)
            fasta_resp.raise_for_status()
            fasta = fasta_resp.text
            
            # Extract gene names
            gene_names = entry.get("genes", [])
            symbol = gene_names[0]["geneName"]["value"] if gene_names and "geneName" in gene_names[0] else canonical_query
            all_aliases = {symbol}
            
            for g in gene_names:
                if "synonyms" in g:
                    for s in g["synonyms"]:
                        all_aliases.add(s["value"])
            
            # Get protein name
            full_name = (
                entry.get("proteinDescription", {})
                .get("recommendedName", {})
                .get("fullName", {})
                .get("value", "N/A")
            )
            all_aliases.update([full_name, query])
            
            result = {
                "canonical_symbol": symbol,
                "canonical_name": full_name,
                "uniprot_id": acc,
                "entrez_id": None,
                "fasta": fasta,
                "all_known_names": sorted([x for x in all_aliases if isinstance(x, str) and x != "N/A"]),
                "source": f"UniProt (Swiss-Prot, reviewed {organism})"
            }
            
            if save_to_file:
                os.makedirs(output_dir, exist_ok=True)
                filename = os.path.join(output_dir, f"{symbol}.fasta")
                with open(filename, "w") as f:
                    f.write(fasta)
                result["fasta_file"] = filename
            
            return result
            
    except Exception as e:
        pass
    
    # 2. Fallback: MyGene.info (only for human)
    if organism == "human":
        try:
            mg_url = "https://mygene.info/v3/query"
            mg_params = {
                "q": canonical_query,
                "species": "human",
                "fields": "symbol,name,alias,uniprot,entrezgene",
                "size": 5
            }
            
            resp = requests.get(mg_url, params=mg_params, timeout=10)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
            
            for hit in hits:
                uniprot_id = hit.get("uniprot", {}).get("Swiss-Prot")
                if uniprot_id:
                    fasta_resp = requests.get(f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta", timeout=10)
                    fasta_resp.raise_for_status()
                    fasta = fasta_resp.text
                    
                    symbol = hit.get("symbol", "N/A")
                    name = hit.get("name", "N/A")
                    aliases = hit.get("alias", [])
                    if isinstance(aliases, str):
                        aliases = [aliases]
                    all_names = set([symbol, name, query] + aliases)
                    
                    result = {
                        "canonical_symbol": symbol,
                        "canonical_name": name,
                        "uniprot_id": uniprot_id,
                        "entrez_id": hit.get("entrezgene"),
                        "fasta": fasta,
                        "all_known_names": sorted([x for x in all_names if isinstance(x, str) and x != "N/A"]),
                        "source": "MyGene.info (Swiss-Prot filtered)"
                    }
                    
                    if save_to_file:
                        os.makedirs(output_dir, exist_ok=True)
                        filename = os.path.join(output_dir, f"{symbol}.fasta")
                        with open(filename, "w") as f:
                            f.write(fasta)
                        result["fasta_file"] = filename
                    
                    return result
                    
        except Exception:
            pass
    
    return {"error": f"No reviewed UniProt entry found for '{query}' (normalized to '{canonical_query}') in organism '{organism}'"}


def download_uniprot_fasta(
    gene_name: str,
    organism: str,
    output_dir: str = "outputs",
    allow_unreviewed: bool = True
) -> Optional[str]:
    """
    Smart FASTA download from UniProt with fallback to text search.
    
    Args:
        gene_name: Gene symbol
        organism: Scientific name (e.g., "Homo sapiens", "Mus musculus")
        output_dir: Directory to save output
        allow_unreviewed: Allow unreviewed (TrEMBL) entries if reviewed not found
        
    Returns:
        Path to saved FASTA file, or None if failed
    """
    def _get_species_taxid(organism: str) -> Optional[int]:
        """Get NCBI taxonomy ID for organism."""
        query = quote(organism)
        url = f"https://rest.uniprot.org/taxonomy/search?query={query}&format=json&size=10"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            for entry in data.get("results", []):
                if entry.get("rank") == "species" and entry.get("scientificName", "").lower() == organism.lower():
                    return entry["taxonId"]
            for entry in data.get("results", []):
                if entry.get("rank") == "species":
                    return entry["taxonId"]
        except Exception as e:
            print(f"Error getting taxid for '{organism}': {e}")
        return None

    def _get_all_organism_taxids(organism: str) -> Optional[list]:
        """Get main taxid and all subspecies taxids."""
        main_taxid = _get_species_taxid(organism)
        if main_taxid is None:
            return None
        taxids = {main_taxid}
        try:
            url = f"https://rest.uniprot.org/taxonomy/search?query=parent_id:{main_taxid}&include_children:true&format=json&size=200"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for entry in data.get("results", []):
                    taxids.add(entry["taxonId"])
        except Exception as e:
            print(f"Warning: Could not load subspecies for '{organism}': {e}")
        return sorted(taxids)

    def _parse_fasta_entries(fasta_text: str):
        """Parse FASTA text into (sequence, header) tuples."""
        entries = []
        lines = fasta_text.strip().splitlines()
        if not lines or not lines[0].startswith(">"):
            return entries
        current_header = lines[0]
        current_seq = []
        for line in lines[1:]:
            if line.startswith(">"):
                entries.append(("".join(current_seq), current_header))
                current_header = line
                current_seq = []
            else:
                current_seq.append(line.strip())
        entries.append(("".join(current_seq), current_header))
        return entries

    def _is_relevant_entry(header: str, gene_name: str, organism_query: str) -> bool:
        """Check if entry matches gene and organism."""
        header_lower = header.lower()
        gene_ok = f"gn={gene_name.lower()}" in header_lower
        org_ok = organism_query.lower() in header_lower
        return gene_ok and org_ok

    # Step 1: Strict search by gene + organism_id
    taxids = _get_all_organism_taxids(organism)
    if taxids:
        organism_part = " OR ".join([f"organism_id:{tid}" for tid in taxids])
        base_query = f"gene:{gene_name} AND ({organism_part})"
        queries = [f"{base_query} AND reviewed:true"]
        if allow_unreviewed:
            queries.append(base_query)

        for query in queries:
            encoded = quote(query, safe='')
            url = f"https://rest.uniprot.org/uniprotkb/search?query={encoded}&format=fasta&size=500"
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200 and resp.text.strip() and not resp.text.startswith("<?xml"):
                    entries = _parse_fasta_entries(resp.text)
                    if entries:
                        # Select best entry (longest sequence)
                        best = None
                        best_len = -1
                        is_reviewed = "reviewed:true" in query
                        for seq, hdr in entries:
                            clean_seq = re.sub(r'[^A-Z]', '', seq.upper())
                            if best is None or len(clean_seq) > best_len:
                                best = (clean_seq, hdr)
                                best_len = len(clean_seq)
                        if best:
                            seq, hdr = best
                            fasta_content = f"{hdr}\n{seq}"
                            match = re.search(r'\|([A-Za-z0-9_]+)\s+.*OS=([^=]+?)\s+OX=', hdr)
                            org_name = match.group(2).strip() if match else organism
                            gene_clean = re.sub(r'[^a-zA-Z0-9_]', '', gene_name)
                            org_clean = re.sub(r'[^a-zA-Z0-9\s]', '', org_name).replace(" ", "_")
                            filename = f"{org_clean}_{gene_clean}.fasta"
                            filepath = os.path.join(output_dir, filename)
                            os.makedirs(output_dir, exist_ok=True)
                            with open(filepath, "w") as f:
                                f.write(fasta_content)
                            status = "reviewed" if is_reviewed else "unreviewed"
                            print(f"[OK] Found by strict search ({status}, length={best_len}) -> {filepath}")
                            return filepath
            except Exception as e:
                print(f"[WARN] Error in strict search: {e}")

    # Step 2: Fallback - text search
    print("[INFO] Strict search returned no results. Trying text search...")
    text_query = f"{gene_name} {organism}"
    encoded_text = quote(text_query)
    url = f"https://rest.uniprot.org/uniprotkb/search?query={encoded_text}&format=fasta&size=100"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200 and resp.text.strip() and not resp.text.startswith("<?xml"):
            entries = _parse_fasta_entries(resp.text)
            candidates = []
            for seq, hdr in entries:
                if _is_relevant_entry(hdr, gene_name, organism):
                    clean_seq = re.sub(r'[^A-Z]', '', seq.upper())
                    is_rev = hdr.startswith(">sp|")
                    candidates.append((len(clean_seq), is_rev, clean_seq, hdr))

            if candidates:
                # Sort: reviewed first, then by length (descending)
                candidates.sort(key=lambda x: (-x[1], -x[0]))
                _, _, best_seq, best_hdr = candidates[0]

                match = re.search(r'\|([A-Za-z0-9_]+)\s+.*OS=([^=]+?)\s+OX=', best_hdr)
                org_name = match.group(2).strip() if match else organism
                gene_clean = re.sub(r'[^a-zA-Z0-9_]', '', gene_name)
                org_clean = re.sub(r'[^a-zA-Z0-9\s]', '', org_name).replace(" ", "_")
                filename = f"{org_clean}_{gene_clean}.fasta"
                filepath = os.path.join(output_dir, filename)
                os.makedirs(output_dir, exist_ok=True)
                with open(filepath, "w") as f:
                    f.write(f"{best_hdr}\n{best_seq}")
                status = "reviewed" if candidates[0][1] else "unreviewed"
                print(f"[OK] Found by text search ({status}, length={candidates[0][0]}) -> {filepath}")
                return filepath
    except Exception as e:
        print(f"[WARN] Error in text search: {e}")

    print(f"[ERR] No entries found for '{gene_name}' in '{organism}' even with text search.")
    return None
