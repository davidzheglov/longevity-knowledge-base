from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# Ensure src path
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import json as _json
import asyncio as _asyncio
import uuid as _uuid
import integration.tools_wrapped as tw  # type: ignore
from agents.tool import ToolContext  # type: ignore
from integration.artifacts import (
    start_session,
    get_run_dir,
    list_artifacts,
    resolve_artifact,
)


def _extract_path_from_text(s: str) -> str | None:
    # Look for `C:\...` or `/...` sequences ending with an extension
    m = re.search(r"([A-Za-z]:\\[^\n]+\.[A-Za-z0-9]+)|(/[^\n]+\.[A-Za-z0-9]+)", s)
    return m.group(0) if m else None


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> int:
    try:
        # Start a fresh artifact session under outputs
        run_dir = start_session(label="artifacts_flow")
        tw.bootstrap_data()

        print(f"Session dir: {run_dir}")

        # Helper to call FunctionTool directly
        def call_tool(tool, **kwargs):
            args_json = _json.dumps(kwargs)
            ctx = ToolContext(context=None, tool_name=tool.name, tool_call_id=str(_uuid.uuid4()), tool_arguments=args_json)
            return _asyncio.run(tool.on_invoke_tool(ctx, args_json))

        # 1) Download FASTA for TP53
        out1 = call_tool(tw.download_uniprot_fasta, gene="TP53", species="human", output_file="TP53.fasta")
        print("download_uniprot_fasta ->", out1)
        p1 = _extract_path_from_text(out1)
        assert_true(p1 is not None and Path(p1).exists(), "TP53.fasta was not saved")

        # 2) Verify artifact registry contains the TP53 FASTA
        arts_1 = list_artifacts()
        print("artifacts after download:", json.dumps(arts_1, indent=2))
        assert_true(any(Path(a["path"]).name.endswith("TP53.fasta") for a in arts_1), "TP53.fasta not registered as artifact")

        # 3) Truncate the protein at position 100 using the downloaded FASTA
        out2 = call_tool(tw.mutate_truncate, fasta_file=p1, position=100, output_file="TP53_mut_truncate.fasta")
        print("mutate_truncate ->", out2)
        p2 = _extract_path_from_text(out2)
        assert_true(p2 is not None and Path(p2).exists(), "TP53_mut_truncate.fasta was not saved")

        # 4) Pairwise alignment between original and truncated; ensure unique naming reuse works
        out3 = call_tool(tw.pairwise_protein_alignment, fasta1=p1, fasta2=p2, output_file="alignment_tp53_trunc.txt")
        print("pairwise_protein_alignment #1 ->", out3)
        p3 = _extract_path_from_text(out3)
        assert_true(p3 is not None and Path(p3).exists(), "alignment_tp53_trunc.txt was not saved")

        # 4b) Repeat the same output filename to trigger ensure_unique_path (should create _1)
        out4 = call_tool(tw.pairwise_protein_alignment, fasta1=p1, fasta2=p2, output_file="alignment_tp53_trunc.txt")
        print("pairwise_protein_alignment #2 ->", out4)
        p4 = _extract_path_from_text(out4)
        assert_true(p4 is not None and Path(p4).exists(), "second alignment file was not saved")
        assert_true(Path(p4).name != Path(p3).name, "ensure_unique_path did not create a unique filename")

        # 5) Confirm artifacts.json includes at least these 3 kinds
        arts_final = list_artifacts()
        kinds = {Path(a["path"]).suffix for a in arts_final}
        assert_true({".fasta", ".txt"}.issubset(kinds), "Expected FASTA and TXT artifacts to be present")

        print("\nAll artifact flow checks passed.")
        print(f"Artifacts recorded: {len(arts_final)} under {get_run_dir()}")
        return 0
    except Exception as e:
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
