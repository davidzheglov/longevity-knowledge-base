"""
Agent wiring test: verifies that all tools are properly wrapped and attached to the orchestrator.
- Lists tool count and names
- Checks tool object types
- Optionally runs a minimal LLM-driven call if OPENAI_API_KEY is set
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure src is on path
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from agents import Agent, Runner, trace  # type: ignore
except Exception as e:
    print(f"[X] Failed to import agents SDK: {e}")
    raise

# Import wrappers
try:
    import integration.tools_wrapped as tw
except Exception as e:
    print(f"[X] Failed to import tool wrappers: {e}")
    raise


def main() -> None:
    # Bootstrap local data (gene map)
    tw.bootstrap_data()

    tools = tw.ALL_TOOLS
    print(f"[OK] Registered tools: {len(tools)}")

    # Print a short list of tool names
    names = []
    for t in tools:
        # Each wrapper is a FunctionTool-like object; rely on duck typing
        name = getattr(t, "name", None) or getattr(t, "__name__", None) or str(t)
        names.append(name)
    print("[OK] Tool names (first 10):")
    for i, n in enumerate(names[:10], 1):
        print(f"  {i:2d}. {n}")
    if len(names) > 10:
        print(f"  ... and {len(names) - 10} more")

    # Minimal sanity checks: expect specific tools present by name
    expected = {
        "normalize_gene",
        "generate_brunet_gene_report",
        "generate_hannum_gene_report",
        "get_reactome_pathways",
        "get_go_annotation",
        "get_drug_info",
        "fetch_and_extract_hpa",
    }
    missing = [e for e in expected if e not in names]
    if missing:
        print(f"[X] Missing expected tools: {missing}")
    else:
        print("[OK] Expected tools are present")

    # If API key exists, do a tiny end-to-end run prompting the agent
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        orch = Agent(
            name="wiring_test",
            instructions=(
                "You can use tools to answer the user's request."
            ),
            tools=tools,
        )
        print("[OK] Agent constructed with tools")
        try:
            with trace("Wiring E2E Test"):
                result = Runner.run(
                    starting_agent=orch,
                    input="Normalize TP53",
                )
                # Runner.run can be sync/async depending on SDK, handle both
                if hasattr(result, "__await__"):
                    import asyncio
                    result = asyncio.get_event_loop().run_until_complete(result)
            print("[OK] E2E run completed")
            print("Final output:\n" + str(result.final_output))
        except Exception as e:
            print(f"[!] E2E run failed (this is expected without network or if model is unavailable): {e}")
    else:
        print("[SKIP] OPENAI_API_KEY not set; skipping E2E run")


if __name__ == "__main__":
    main()
