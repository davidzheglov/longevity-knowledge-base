import pandas as pd
import os
import re
from ete3 import Tree
from typing import Optional

def _normalize_user_name(name: str) -> str:
    return re.sub(r'\s+', '_', name.strip())

def _extract_pretty_name(full_name: str) -> str:
    parts = full_name.split('_')
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    return full_name.replace('_', ' ')

def generate_mammal_report(
    species_query: str,
    anage_path: str = None,
    arocm_path: str = None,
    tree_path: str = None,
    output_dir: str = '.'
) -> Optional[str]:
    """
    Generates a comprehensive report for a mammal species combining AnAge and AROCM data.
    
    Args:
        species_query: Species name (e.g., "Homo sapiens", "Loxodonta africana")
        anage_path: Path to anage_mammals.csv
        arocm_path: Path to AROCM.csv
        tree_path: Path to Mammals_Tree.nwk
        output_dir: Directory to save the report
    
    Returns:
        Path to the saved report file
    """
    # Set default paths
    if anage_path is None:
        anage_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'anage_mammals.csv'))
    if arocm_path is None:
        arocm_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'AROCM.csv'))
    if tree_path is None:
        tree_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Mammals_Tree.nwk'))
    
    # Load data
    if not os.path.exists(anage_path):
        raise FileNotFoundError(f"AnAge file '{anage_path}' not found.")
    if not os.path.exists(arocm_path):
        raise FileNotFoundError(f"AROCM file '{arocm_path}' not found.")
    if not os.path.exists(tree_path):
        raise FileNotFoundError(f"Tree file '{tree_path}' not found.")

    # Load AnAge
    df_anage = pd.read_csv(anage_path)
    df_anage['species_key'] = (df_anage['Genus'].fillna('') + '_' + df_anage['Species'].fillna('')).str.lower()
    anage_dict = {row['species_key']: row for _, row in df_anage.iterrows()}

    # Load AROCM
    df_arocm = pd.read_csv(arocm_path, sep=';', decimal=',', header=0)
    name_col = 'SpeciesLatinName'
    val_col = 'AROCM'

    arocm_dict = {}
    for _, row in df_arocm.iterrows():
        raw_name = str(row[name_col]).strip()
        if not raw_name or raw_name.lower() in ('nan', 'none', ''):
            continue
        if ' ' not in raw_name:
            continue
        key = raw_name.replace(' ', '_').lower()
        try:
            arocm_dict[key] = float(row[val_col])
        except (ValueError, TypeError):
            continue

    # Parse tree
    t = Tree(tree_path, format=1)
    leaf_names = [leaf.name for leaf in t.get_leaves()]
    leaf_pretty_to_full = {}
    leaf_keys_in_tree = set()

    for full_name in leaf_names:
        pretty = _extract_pretty_name(full_name)
        key = pretty.replace(' ', '_').lower()
        leaf_pretty_to_full[key] = full_name
        leaf_keys_in_tree.add(key)

    # Normalize query
    query_pretty = re.sub(r'[_\s]+', ' ', species_query).strip()
    query_key = query_pretty.replace(' ', '_').lower()

    if query_key not in leaf_keys_in_tree:
        raise ValueError(f"Species '{query_pretty}' is NOT in the phylogeny (Mammals_Tree.nwk).")

    target_full = leaf_pretty_to_full[query_key]
    target_node = t & target_full

    # Find best AnAge match
    anage_match = None
    anage_dist = 0.0
    if query_key in anage_dict:
        anage_match = query_key
    else:
        best_d = float('inf')
        for leaf in t.get_leaves():
            leaf_pretty = _extract_pretty_name(leaf.name)
            leaf_key = leaf_pretty.replace(' ', '_').lower()
            if leaf_key in anage_dict:
                d = target_node.get_distance(leaf)
                if d < best_d:
                    best_d = d
                    anage_match = leaf_key
                    anage_dist = d
        if anage_match is None:
            raise ValueError(f"No AnAge data found for '{query_pretty}' or any relative.")

    # Find best AROCM match
    arocm_match = None
    arocm_dist = 0.0
    arocm_value = None
    if query_key in arocm_dict:
        arocm_match = query_key
        arocm_value = arocm_dict[query_key]
    else:
        best_d = float('inf')
        for leaf in t.get_leaves():
            leaf_pretty = _extract_pretty_name(leaf.name)
            leaf_key = leaf_pretty.replace(' ', '_').lower()
            if leaf_key in arocm_dict:
                d = target_node.get_distance(leaf)
                if d < best_d:
                    best_d = d
                    arocm_match = leaf_key
                    arocm_dist = d
                    arocm_value = arocm_dict[leaf_key]

    # Prepare report species names
    anage_record = anage_dict[anage_match]
    anage_species = f"{anage_record['Genus']} {anage_record['Species']}"
    anage_is_exact = (anage_match == query_key)

    arocm_species = None
    if arocm_match:
        parts = arocm_match.split('_')
        if len(parts) >= 2:
            arocm_species = f"{parts[0]} {parts[1]}"
        else:
            arocm_species = arocm_match.replace('_', ' ')
    arocm_is_exact = (arocm_match == query_key) if arocm_match else False

    # Format helper
    def fmt(val):
        if pd.isna(val):
            return "unknown"
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return str(val)

    # Build report
    lines = []
    lines.append(f"Report for query: '{query_pretty}'")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"AnAge data source: '{anage_species}' ({'exact' if anage_is_exact else f'closest relative, dist={anage_dist:.3f}'})")
    if arocm_species:
        lines.append(f"AROCM data source: '{arocm_species}' ({'exact' if arocm_is_exact else f'closest relative, dist={arocm_dist:.3f}'})")
    else:
        lines.append("AROCM data source: unknown")
    lines.append("")

    # PHYLOGENY
    lines.append("PHYLOGENY (AnAge)")
    lines.append("-" * 30)
    lines.append(f"Order: {fmt(anage_record['Order'])}")
    lines.append(f"Family: {fmt(anage_record['Family'])}")
    lines.append(f"Scientific name: {anage_species}")
    lines.append(f"Common name: {fmt(anage_record['Common name'])}")

    # LIFESPAN
    lines.append("\nLIFESPAN (AnAge)")
    lines.append("-" * 30)
    lines.append(f"Maximum longevity (years): {fmt(anage_record['Maximum longevity (yrs)'])}")

    # METADATA
    lines.append("\nMETADATA (AnAge)")
    lines.append("-" * 30)
    lines.append(f"Adult weight (g): {fmt(anage_record['Adult weight (g)'])}")
    lines.append(f"Gestation/Incubation (days): {fmt(anage_record['Gestation/Incubation (days)'])}")
    lines.append(f"Litter/Clutch size: {fmt(anage_record['Litter/Clutch size'])}")
    lines.append(f"Female maturity (days): {fmt(anage_record['Female maturity (days)'])}")
    lines.append(f"Male maturity (days): {fmt(anage_record['Male maturity (days)'])}")
    lines.append(f"Body mass (g): {fmt(anage_record['Body mass (g)'])}")

    # AROCM
    lines.append("\nAROCM (AROCM)")
    lines.append("-" * 30)
    lines.append(f"AROCM: {f'{arocm_value:.6f}' if arocm_value is not None else 'unknown'}")

    # Save
    safe_query = _normalize_user_name(query_pretty)
    filepath = os.path.join(output_dir, f"{safe_query}_report.txt")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return filepath
