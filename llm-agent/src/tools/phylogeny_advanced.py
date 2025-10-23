"""
Advanced phylogeny utilities:
- build_phylo_tree_nj: Neighbor-Joining tree from a protein MSA FASTA; renders PNG via toytree.
- build_phylo_tree_ml: Maximum Likelihood tree via IQ-TREE (external binary); renders PNG via toytree.

Both return a dict with file paths or an 'error' field on failure.
"""
from typing import Tuple, Dict, Optional
import os
import re
import shutil
import subprocess

from Bio import AlignIO, Phylo, SeqIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

import toytree  # type: ignore
import toyplot.png  # type: ignore


def _simplify_id(header: str) -> str:
    if '|' in header:
        candidate = header.split('|')[-1]
    else:
        candidate = header
    simple_id = candidate.split()[0]
    return re.sub(r"[^a-zA-Z0-9_]", "_", simple_id)


def _extract_pretty_name(full_name: str) -> str:
    parts = full_name.split('_')
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    return full_name.replace('_', ' ')


def build_phylo_tree_nj(
    alignment_fasta: str,
    output_prefix: str = "tree_nj",
    layout: str = 'r',  # 'r' radial, 'u' rectangular
) -> Dict:
    """
    Build a Neighbor-Joining tree from a protein alignment FASTA and render PNG.
    Returns {'newick_file': str, 'png_file': str} or {'error': str}.
    """
    if not os.path.exists(alignment_fasta):
        return {"error": f"Alignment file not found: {alignment_fasta}"}

    # Simplify record IDs (to avoid spaces/specials)
    simplified_records = []
    for record in SeqIO.parse(alignment_fasta, "fasta"):
        new_id = _simplify_id(record.id)
        simplified_records.append(SeqRecord(Seq(str(record.seq)), id=new_id, description=""))

    tmp_aln = f"{output_prefix}.tmp.fasta"
    SeqIO.write(simplified_records, tmp_aln, "fasta")
    try:
        alignment = AlignIO.read(tmp_aln, "fasta")
        calculator = DistanceCalculator('blosum62')
        dm = calculator.get_distance(alignment)
        constructor = DistanceTreeConstructor()
        tree = constructor.nj(dm)

        newick_file = f"{output_prefix}.nwk"
        Phylo.write(tree, newick_file, "newick")

        # Render with toytree and save PNG
        with open(newick_file, "r", encoding="utf-8") as fh:
            newick_str = fh.read().strip()
        tree_obj = toytree.tree(newick_str)
        original_names = tree_obj.get_tip_labels()
        pretty_labels = [_extract_pretty_name(name) for name in original_names]

        scale = 2
        width = 600 * scale
        height = (400 if layout == 'r' else 600) * scale
        canvas, axes, mark = tree_obj.draw(
            layout=layout,
            width=width,
            height=height,
            edge_colors="red",
            tip_labels=pretty_labels,
            tip_labels_colors="green",
            tip_labels_style={"font-size": f"{12 * scale}px"},
            scale_bar=True,
            padding=(20*scale, 20*scale, 60*scale, 60*scale),
            node_sizes=0,
        )
        png_file = f"{output_prefix}.png"
        toyplot.png.render(canvas, png_file)
        return {"newick_file": newick_file, "png_file": png_file}
    finally:
        if os.path.exists(tmp_aln):
            os.remove(tmp_aln)


def build_phylo_tree_ml(
    alignment_fasta: str,
    output_prefix: str = "tree_ml",
    layout: str = 'r',  # 'r' radial, 'u' rectangular
) -> Dict:
    """
    Build a Maximum Likelihood tree via IQ-TREE and render PNG (requires iqtree or iqtree2 in PATH).
    Returns {'newick_file': str, 'png_file': str} or {'error': str}.
    """
    if not os.path.exists(alignment_fasta):
        return {"error": f"Alignment file not found: {alignment_fasta}"}

    iqtree_bin = shutil.which("iqtree2") or shutil.which("iqtree")
    if not iqtree_bin:
        return {"error": "IQ-TREE not installed or not in PATH"}

    # Simplify IDs and write a temporary alignment
    simplified_records = []
    for record in SeqIO.parse(alignment_fasta, "fasta"):
        new_id = _simplify_id(record.id)
        simplified_records.append(SeqRecord(Seq(str(record.seq)), id=new_id, description=""))

    temp_aln = f"{output_prefix}.tmp.fasta"
    SeqIO.write(simplified_records, temp_aln, "fasta")
    try:
        cmd = [
            iqtree_bin,
            "-s", temp_aln,
            "-m", "MFP",
            "-bb", "1000",
            "-nt", "AUTO",
            "-pre", output_prefix,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {"error": f"IQ-TREE error: {result.stderr.strip()}"}

        newick_file = f"{output_prefix}.treefile"
        if not os.path.exists(newick_file):
            return {"error": f"Treefile not created: {newick_file}"}

        # Render with toytree
        with open(newick_file, "r", encoding="utf-8") as fh:
            newick_str = fh.read().strip()
        tree_obj = toytree.tree(newick_str)
        original_names = tree_obj.get_tip_labels()
        pretty_labels = [_extract_pretty_name(name) for name in original_names]

        scale = 2
        width = 600 * scale
        height = (400 if layout == 'r' else 600) * scale
        canvas, axes, mark = tree_obj.draw(
            layout=layout,
            width=width,
            height=height,
            edge_colors="red",
            tip_labels=pretty_labels,
            tip_labels_colors="green",
            tip_labels_style={"font-size": f"{12 * scale}px"},
            scale_bar=True,
            padding=(20*scale, 20*scale, 60*scale, 60*scale),
            node_sizes=0,
        )
        png_file = f"{output_prefix}.png"
        toyplot.png.render(canvas, png_file)
        return {"newick_file": newick_file, "png_file": png_file}
    finally:
        if os.path.exists(temp_aln):
            os.remove(temp_aln)
