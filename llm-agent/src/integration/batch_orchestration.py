from __future__ import annotations
import asyncio
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure src path (same pattern as smoke_orchestration.py)
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agents import Agent, Runner  # type: ignore
import integration.tools_wrapped as tw  # type: ignore
from integration.artifacts import start_session as artifacts_start_session


@dataclass
class RunRecord:
    idx: int
    prompt: str
    ok: bool
    output: Optional[str]
    error: Optional[str]
    started_at: str
    finished_at: str


def build_prompts() -> List[str]:
    """Curated prompts designed to exercise each tool at least once.

    Notes:
    - Some prompts chain multiple tools (e.g., download + pairwise alignment)
    - File outputs are directed into the repo's outputs/ folder
    """
    out_dir = Path(__file__).resolve().parents[2] / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    return [
        # Gene normalization
        "Normalize the gene alias 'p53' and list canonical IDs.",
        # UniProt search and FASTA
        "Find UniProt entries for gene TP53 in human.",
        f"Download UniProt FASTA for TP53 (human) and save to {out_dir / 'TP53.fasta'}.",
        # Protein function and features
        "Summarize the protein function of SIRT1 in human.",
        "Get UniProt features for MYC (concise).",
        # Reactome / GO / Drug info
        "List key Reactome pathways involving TP53 and save a brief report.",
        "Fetch Gene Ontology annotations for BRCA1.",
        "What drugs target EGFR? Provide key entries.",
        # HPA
        f"Fetch Human Protein Atlas data for SPP1 and save into {out_dir}.",
        # Variants and PDF report
        f"Export gene variants for TP53 to an Excel at {out_dir / 'variants_tp53.xlsx' }.",
        f"Generate a compact gene report PDF for TP53 at {out_dir / 'tp53_report.pdf' }.",
        # Aging clocks
        f"Run the Horvath gene report for ELOVL2 and save outputs under {out_dir}.",
        f"Run the Hannum gene report for ELOVL2 and save outputs under {out_dir}.",
        f"Run the Brunet gene report for SPP1 and save outputs under {out_dir}.",
        f"Run the PhenoAge gene report for GDF15 and save outputs under {out_dir}.",
        # Mammal data
        f"Generate a mammal longevity report for 'naked mole-rat' and save under {out_dir}.",
        # Pairwise alignment (assumes FASTAs can be downloaded as part of the task)
        f"Download FASTA for human TP53 and human BRCA1, then run a pairwise protein alignment and save the alignment to {out_dir / 'alignment_tp53_brca1.txt' }.",
        # MSA + NJ Tree
        f"Download protein FASTAs for TP53, BRCA1, and EGFR (human). Create a multiple sequence alignment with MAFFT saved to {out_dir / 'aligned_three.fasta' }. Then build a Neighbor-Joining phylogenetic tree image saved to {out_dir / 'tree_nj.png' }.",
        # ML Tree (use aligned from prior or redo)
        f"Using {out_dir / 'aligned_three.fasta'}, build a Maximum Likelihood phylogenetic tree and save to {out_dir / 'tree_ml.png' }.",
        # Mammalian tree plotting
        f"Plot a mammalian cladogram for these species: human, mouse, rat, cow, dog. Save to {out_dir / 'mammal_tree.png' }.",
        # Mutation tools (start from TP53.fasta)
        f"Using {out_dir / 'TP53.fasta'}, replace the amino acid at position 10 with A and save to {out_dir / 'TP53_mut_replace.fasta' }.",
        f"Using {out_dir / 'TP53.fasta'}, delete residues from positions 5 to 12 and save to {out_dir / 'TP53_mut_delete.fasta' }.",
        f"Using {out_dir / 'TP53.fasta'}, insert the sequence 'GGG' after position 20 and save to {out_dir / 'TP53_mut_insert.fasta' }.",
        f"Using {out_dir / 'TP53.fasta'}, truncate the protein at position 100 and save to {out_dir / 'TP53_mut_truncate.fasta' }.",
        # Pairwise alignment on mutated vs original
        f"Run pairwise protein alignment between {out_dir / 'TP53.fasta'} and {out_dir / 'TP53_mut_truncate.fasta'}; save to {out_dir / 'alignment_tp53_trunc.txt' }.",
    ]


def slice_prompts(prompts: List[str], start: Optional[int], end: Optional[int]) -> Tuple[List[str], Tuple[int, int]]:
    n = len(prompts)
    s = 0 if start is None else max(0, min(start, n))
    e = n if end is None else max(0, min(end, n))
    return prompts[s:e], (s, e)


async def run_batch(prompts: List[str]) -> List[RunRecord]:
    # Ensure data bootstrap so normalization works locally
    tw.bootstrap_data()

    records: List[RunRecord] = []
    for idx, prompt in enumerate(prompts):
        # Create a fresh agent per prompt to avoid cross-run attachments/state contamination
        orch = Agent(
            name="orchestrator",
            instructions=(
                "You have many bioinformatics tools. Choose the minimal set to satisfy the prompt. "
                "Return plain text only (no images or file attachments). If a tool saves a file, "
                "just state the absolute path. Keep responses short."
            ),
            tools=tw.ALL_TOOLS,
        )
        started = datetime.utcnow().isoformat() + "Z"
        try:
            res = await Runner.run(starting_agent=orch, input=prompt)
            output = getattr(res, "final_output", None)
            ok = output is not None
            err = None
        except Exception as e:
            ok = False
            output = None
            err = repr(e)
        finished = datetime.utcnow().isoformat() + "Z"
        records.append(RunRecord(idx=idx, prompt=prompt, ok=ok, output=output, error=err, started_at=started, finished_at=finished))
    return records


def save_results(records: List[RunRecord], run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    jsonl = run_dir / "results.jsonl"
    with jsonl.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    summary = {
        "total": len(records),
        "success": sum(1 for r in records if r.ok),
        "failed": [
            {"idx": r.idx, "prompt": r.prompt, "error": r.error}
            for r in records if not r.ok
        ],
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


async def main(argv: List[str]) -> int:
    # Where to store run artifacts
    out_root = Path(__file__).resolve().parents[2] / "outputs"
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = out_root / f"batch_run_{timestamp}"
    artifacts_start_session(str(run_dir), label="batch")

    # Args: optional --start N --end M to run a slice
    start = None
    end = None
    for i, a in enumerate(argv):
        if a == "--start" and i + 1 < len(argv):
            try:
                start = int(argv[i + 1])
            except ValueError:
                pass
        if a == "--end" and i + 1 < len(argv):
            try:
                end = int(argv[i + 1])
            except ValueError:
                pass

    prompts_all = build_prompts()
    prompts, (s, e) = slice_prompts(prompts_all, start, end)

    # Print quick header
    print(f"Running prompts slice [{s}:{e}] out of {len(prompts_all)} total…", flush=True)
    for i, p in enumerate(prompts, start=s):
        print(f"[{i}] {p}")

    # Basic environment checks
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("[W] No OPENAI_API_KEY or ANTHROPIC_API_KEY detected. Runs may fail.")

    records = await run_batch(prompts)
    save_results(records, run_dir)

    print(f"\nSaved run artifacts in: {run_dir}")
    print(f"Success: {sum(1 for r in records if r.ok)} / {len(records)}")

    # Print a few sample outputs
    for r in records[:3]:
        print("\n--- Sample Output ---")
        print(f"[{r.idx}] OK={r.ok}")
        if r.ok:
            print(r.output[:800] if r.output else "(no output)")
        else:
            print(f"ERROR: {r.error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main(sys.argv[1:])))
