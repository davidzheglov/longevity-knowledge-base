from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
import json as _json
import uuid as _uuid
import asyncio as _asyncio

# Ensure src path
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import integration.tools_wrapped as tw  # type: ignore
from agents.tool import ToolContext  # type: ignore
from integration.artifacts import (
    start_session,
    get_run_dir,
    list_artifacts,
)


def _extract_path_from_text(s: str) -> str | None:
    m = re.search(r"([A-Za-z]:\\[^\n]+\.[A-Za-z0-9]+)|(/[^\n]+\.[A-Za-z0-9]+)", s)
    return m.group(0) if m else None


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _call_tool(tool, **kwargs) -> str:
    args_json = _json.dumps(kwargs)
    ctx = ToolContext(context=None, tool_name=tool.name, tool_call_id=str(_uuid.uuid4()), tool_arguments=args_json)
    return _asyncio.run(tool.on_invoke_tool(ctx, args_json))


def main() -> int:
    try:
        # Start a fresh artifact session under outputs
        run_dir = start_session(label="files_only")
        tw.bootstrap_data()
        print(f"Session dir: {run_dir}")

        # Resolve local FASTA inputs (no network)
        # Repo root (three levels up from this file)
        repo_root = Path(__file__).resolve().parents[3]
        tp53 = (repo_root / "tp53.fasta" / "Homo_sapiens_TP53.fasta").resolve()
        brca1 = (repo_root / "brca1.fasta" / "Homo_sapiens_BRCA1.fasta").resolve()
        egfr = (repo_root / "EGFR.fasta" / "Homo_sapiens_EGFR.fasta").resolve()
        for p in (tp53, brca1, egfr):
            assert_true(p.exists(), f"Missing local FASTA: {p}")

        # 1) Truncate TP53 using local FASTA
        out1 = _call_tool(tw.mutate_truncate, fasta_file=str(tp53), position=100, output_file="TP53_trunc_local.fasta")
        print("mutate_truncate ->", out1)
        p1 = _extract_path_from_text(out1)
        assert_true(p1 is not None and Path(p1).exists(), "TP53_trunc_local.fasta was not saved")

        # 2) Pairwise alignment original vs truncated; ensure unique naming
        out2 = _call_tool(tw.pairwise_protein_alignment, fasta1=str(tp53), fasta2=p1, output_file="alignment_tp53_trunc_local.txt")
        print("pairwise_protein_alignment #1 ->", out2)
        p2 = _extract_path_from_text(out2)
        assert_true(p2 is not None and Path(p2).exists(), "alignment_tp53_trunc_local.txt was not saved")

        out3 = _call_tool(tw.pairwise_protein_alignment, fasta1=str(tp53), fasta2=p1, output_file="alignment_tp53_trunc_local.txt")
        print("pairwise_protein_alignment #2 ->", out3)
        p3 = _extract_path_from_text(out3)
        assert_true(p3 is not None and Path(p3).exists(), "second alignment file was not saved")
        assert_true(Path(p3).name != Path(p2).name, "ensure_unique_path did not create a unique filename")

        # 3) Pairwise alignment TP53 vs BRCA1
        out4 = _call_tool(tw.pairwise_protein_alignment, fasta1=str(tp53), fasta2=str(brca1), output_file="alignment_tp53_brca1_local.txt")
        print("pairwise_protein_alignment TP53-BRCA1 ->", out4)
        p4 = _extract_path_from_text(out4)
        assert_true(p4 is not None and Path(p4).exists(), "alignment_tp53_brca1_local.txt was not saved")

        # 4) Artifacts sanity
        arts = list_artifacts()
        kinds = {Path(a["path"]).suffix for a in arts}
        assert_true({".fasta", ".txt"}.issubset(kinds), "Expected FASTA and TXT artifacts to be present")

        print("\nFiles-only flow checks passed.")
        print(f"Artifacts recorded: {len(arts)} under {get_run_dir()}")
        return 0
    except Exception:
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
