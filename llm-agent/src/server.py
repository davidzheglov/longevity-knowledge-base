from __future__ import annotations

import asyncio
import os
from typing import Dict, List, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from pathlib import Path
import sys

# Ensure src on path
SRC_DIR = Path(__file__).resolve().parents[0]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agents import Agent, Runner  # type: ignore
from integration.tools_wrapped import ALL_TOOLS, bootstrap_data  # type: ignore
from integration.artifacts import start_session as artifacts_start_session, list_artifacts  # type: ignore


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    output: str
    session_id: str
    artifacts: List[dict] | None = None


app = FastAPI(title="Longevity Agent API", version="0.1.0")


# Simple in-memory chat memory per session
_history: Dict[str, List[Tuple[str, str]]] = {}


def _format_history(history: List[Tuple[str, str]], max_turns: int = 8, max_chars: int = 4000) -> str:
    if not history:
        return ""
    hist = history[-max_turns:]
    lines: List[str] = ["Context (recent conversation):"]
    for u, a in hist:
        lines.append(f"You: {u}")
        lines.append(f"Agent: {a}")
    ctx = "\n".join(lines)
    if len(ctx) > max_chars:
        ctx = ctx[-max_chars:]
        ctx = "(context truncated)\n" + ctx
    return ctx + "\n\n"


# Global orchestrator
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


@app.on_event("startup")
async def _startup() -> None:
    # Bootstrap data and create a stable outputs root; do not overwrite existing session folders
    bootstrap_data()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")

    # Session
    session_id = req.session_id or "default"
    # Start or continue artifact session under a stable path
    out_root = Path(__file__).resolve().parents[1] / "outputs"
    run_dir = out_root / f"session_web_{session_id}"
    artifacts_start_session(str(run_dir), label=f"web_{session_id}")

    # Rolling context
    hist = _history.get(session_id, [])
    ctx = _format_history(hist)
    prompt = f"{ctx}{req.message}" if ctx else req.message

    # Run the agent
    try:
        result = await Runner.run(starting_agent=orchestrator, input=prompt)
        output = getattr(result, "final_output", "") or ""
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"agent_failed: {e}")

    # Update memory
    hist.append((req.message, output))
    _history[session_id] = hist[-16:]

    # Include current artifacts list for convenience
    arts = list_artifacts()
    return ChatResponse(output=output, session_id=session_id, artifacts=arts)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host=host, port=port, reload=False)
