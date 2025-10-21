import os
import sys
import shutil
import tempfile
from pathlib import Path

import pytest

# Ensure 'tools' package is importable like other tests do
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools import build_phylo_tree_nj, build_phylo_tree_ml


ALIGNMENT_CONTENT = ">A\nACGTACGT\n>B\nACGTTCGT\n>C\nACGTTTGT\n"


def _write_alignment(tmpdir: str) -> str:
    p = Path(tmpdir) / "tiny.fasta"
    p.write_text(ALIGNMENT_CONTENT)
    return str(p)


def test_build_phylo_tree_nj_creates_files():
    with tempfile.TemporaryDirectory() as tmp:
        aln = _write_alignment(tmp)
        out = build_phylo_tree_nj(aln, output_prefix=os.path.join(tmp, "nj_tree"))
        assert "error" not in out
        assert os.path.exists(out["newick_file"]) and os.path.getsize(out["newick_file"]) > 0
        assert os.path.exists(out["png_file"]) and os.path.getsize(out["png_file"]) > 0


@pytest.mark.skipif(shutil.which("iqtree2") is None and shutil.which("iqtree") is None, reason="IQ-TREE not installed")
def test_build_phylo_tree_ml_creates_files():
    with tempfile.TemporaryDirectory() as tmp:
        aln = _write_alignment(tmp)
        out = build_phylo_tree_ml(aln, output_prefix=os.path.join(tmp, "ml_tree"))
        assert "error" not in out
        # IQ-TREE default output is .treefile; our function should render png and capture newick
        assert os.path.exists(out["newick_file"]) and os.path.getsize(out["newick_file"]) > 0
        assert os.path.exists(out["png_file"]) and os.path.getsize(out["png_file"]) > 0
