"""
Interactive CLI for the Agents SDK orchestrator using llm-agent tools.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from agents import Agent, Runner, trace

# Ensure src is on path
SRC_DIR = Path(__file__).resolve().parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from integration.tools_wrapped import ALL_TOOLS, bootstrap_data
from integration.artifacts import start_session as artifacts_start_session


orchestrator = Agent(
    name="longevity_researcher",
    instructions=(
        "You are a specialized AI assistant for longevity research and bioinformatics.\n\n"
        "You have tools for gene normalization, UniProt queries, protein mutations, alignments,\n"
        "phylogeny, epigenetic aging clocks (Horvath, PhenoAge, Brunet, Hannum),\n"
        "mammalian longevity, Reactome/GO/DrugBank annotations, UniProt features, HPA expression,\n"
        "variants, and proteomics PDF reports.\n\n"
        "When a user asks a question, select and call the appropriate tools, explain results clearly,\n"
        "and suggest relevant next analyses. Return plain text only (no images or file attachments).\n"
        "When tools save artifacts (images, FASTA, Excel, PDF), just list the absolute file paths."
    ),
    tools=ALL_TOOLS,
)


def _format_history(history: list[tuple[str, str]], max_turns: int = 8, max_chars: int = 4000) -> str:
    if not history:
        return ""
    # Keep only the most recent turns
    hist = history[-max_turns:]
    lines: list[str] = ["Context (recent conversation):"]
    for u, a in hist:
        lines.append(f"You: {u}")
        lines.append(f"Agent: {a}")
    ctx = "\n".join(lines)
    # Trim if too long
    if len(ctx) > max_chars:
        ctx = ctx[-max_chars:]
        ctx = "(context truncated)\n" + ctx
    return ctx + "\n\n"


async def interactive() -> None:
    # Ensure data dir is available
    data_dir = Path(__file__).resolve().parents[2] / "data"
    if data_dir.exists():
        os.environ.setdefault("DATA_DIR", str(data_dir))
    bootstrap_data()
    # Start a local artifact session per interactive run
    session_dir = Path(__file__).resolve().parents[2] / "outputs" / f"session_interactive"
    artifacts_start_session(str(session_dir), label="interactive")

    print("\n" + "=" * 80)
    print("LONGEVITY RESEARCH LLM AGENT (Agents SDK)".center(80))
    print("=" * 80)
    print("Type 'quit' to exit.\n")
    print("Notes: Files you request will be saved under the current session directory and catalogued as artifacts.")
    print("Type 'reset' to clear chat memory. Type 'history' to show recent context.\n")

    # Rolling in-memory chat history for this process
    history: list[tuple[str, str]] = []

    while True:
        try:
            user_request = input("You: ").strip()
            if not user_request:
                continue
            low = user_request.lower()
            if low in {"quit", "exit", "q"}:
                print("\n👋 Goodbye!\n")
                break
            if low == "reset":
                history.clear()
                print("\n(Chat memory cleared)\n")
                continue
            if low == "history":
                print()
                print(_format_history(history, max_turns=12, max_chars=6000))
                continue

            print("\nAgent: ", end="", flush=True)
            # Prepend recent context so the agent can reference prior turns
            ctx = _format_history(history)
            prompt = f"{ctx}{user_request}" if ctx else user_request
            with trace("Longevity research"):
                result = await Runner.run(
                    starting_agent=orchestrator,
                    input=prompt,
                )
            output = result.final_output
            print(output)
            # Save to rolling history
            history.append((user_request, output))
            print()
        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


def main() -> None:
    asyncio.run(interactive())


if __name__ == "__main__":
    main()
