from __future__ import annotations

import os
from typing import Dict, List, Tuple

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent import LongevityAgent


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
_agent: LongevityAgent | None = None


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


@app.on_event("startup")
async def _startup() -> None:
    # Initialize the agent once on startup
    global _agent
    _agent = LongevityAgent()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")

    if _agent is None:
        raise HTTPException(status_code=500, detail="agent_not_initialized")

    # Session handling and light memory
    session_id = req.session_id or "default"
    hist = _history.get(session_id, [])
    ctx = _format_history(hist)
    prompt = f"{ctx}{req.message}" if ctx else req.message

    try:
        output = _agent.chat(prompt) or ""
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"agent_failed: {e}")

    # Update memory
    hist.append((req.message, output))
    _history[session_id] = hist[-16:]

    # No artifact registry in this simplified server
    return ChatResponse(output=output, session_id=session_id, artifacts=None)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host=host, port=port, reload=False)
