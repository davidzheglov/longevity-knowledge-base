import os
import re
import toytree
import toyplot
import toyplot.png
from ete3 import Tree
from typing import List

def _normalize_user_name(name: str) -> str:
    return re.sub(r'\s+', '_', name.strip())

def _extract_pretty_name(full_name: str) -> str:
    parts = full_name.split('_')
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    return full_name.replace('_', ' ')

def plot_mammalian_tree(species_list: List[str], output_png: str = "final_tree.png", layout: str = 'r', tree_path: str = None):
    """
    Visualizes a subtree from Mammals_Tree.nwk, preserving topology and displaying pretty names.
    """
    if tree_path is None:
        tree_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Mammals_Tree.nwk'))
    if not os.path.exists(tree_path):
        raise FileNotFoundError(f"File {tree_path} not found.")

    with open(tree_path, 'r') as f:
        newick_str = f.read().strip()

    t = Tree(newick_str, format=1)
    all_leaves = {leaf.name for leaf in t.get_leaves()}
    normalized_queries = [_normalize_user_name(sp) for sp in species_list]
    matched_full_names = set()
    for query in normalized_queries:
        for leaf in all_leaves:
            if query in leaf:
                matched_full_names.add(leaf)
    if not matched_full_names:
        raise ValueError("No species found.")
    t.prune(list(matched_full_names))
    subset_newick = t.write(format=1)
    tree = toytree.tree(subset_newick)
    original_leaf_names = tree.get_tip_labels()
    pretty_labels = [_extract_pretty_name(name) for name in original_leaf_names]
    scale = 2
    width = 600 * scale
    height = (400 if layout == 'r' else 600) * scale
    canvas, axes, mark = tree.draw(
        layout=layout,
        width=width,
        height=height,
        edge_colors="red",
        tip_labels=pretty_labels,
        tip_labels_colors="green",
        tip_labels_style={"font-size": f"{12*scale}px"},
        scale_bar=True,
        padding=(20*scale, 20*scale, 60*scale, 60*scale),
        node_sizes=0,
    )
    toyplot.png.render(canvas, output_png)
    return output_png
