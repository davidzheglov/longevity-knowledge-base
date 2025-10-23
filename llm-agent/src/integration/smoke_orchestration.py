from __future__ import annotations
import asyncio
import sys
from pathlib import Path

# Ensure src path
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agents import Agent, Runner
import integration.tools_wrapped as tw

tw.bootstrap_data()

orch = Agent(
    name="orchestrator",
    instructions="You can use the tools to normalize and answer succinctly.",
    tools=tw.ALL_TOOLS,
)

async def main() -> None:
    try:
        result = await Runner.run(
            starting_agent=orch,
            input="Normalize TP53",
        )
        print(result.final_output)
    except Exception as e:
        print(f"[E] Orchestration failed: {e!r}")

if __name__ == "__main__":
    asyncio.run(main())
