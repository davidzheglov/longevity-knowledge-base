from __future__ import annotations

import os
from typing import Dict, List, Tuple

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel

from agent import LongevityAgent
from integration.artifacts import (
    switch_session as artifacts_switch_session,
    list_artifacts as artifacts_list,
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    output: str
    session_id: str
    artifacts: List[dict] | None = None
    tools_used: List[str] | None = None


app = FastAPI(title="Longevity Agent API", version="0.1.0")

# Simple in-memory chat memory per session
_history: Dict[str, List[Tuple[str, str]]] = {}
_agent: LongevityAgent | None = None
_outputs_dir: Path | None = None


def _format_history(history: List[Tuple[str, str]], max_turns: int = 8, max_chars: int = 4000) -> str:
    """Legacy: produces a single text block from prior turns (kept for reference)."""
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


def _build_context_messages(history: List[Tuple[str, str]], max_turns: int = 8, max_chars: int = 8000) -> List[dict]:
    """Builds a structured chat history for the LLM from the last N turns.

    Trims to max_turns pairs, and soft-clamps total characters to avoid excessively long prompts.
    """
    if not history:
        return []
    hist = history[-max_turns:]
    msgs: List[dict] = []
    total = 0
    for u, a in hist:
        u_text = str(u or "")
        a_text = str(a or "")
        # Append and track length; if we exceed max_chars, truncate earliest content
        msgs.append({"role": "user", "content": u_text})
        msgs.append({"role": "assistant", "content": a_text})
        total += len(u_text) + len(a_text)
    # If over max_chars, drop from the start (oldest) until under budget
    if total > max_chars:
        # Remove oldest pairs while tracking remaining length
        cur = []
        cur_total = 0
        for m in reversed(msgs):  # start from newest
            cur.append(m)
            cur_total += len(m.get("content") or "")
            if cur_total >= max_chars:
                break
        msgs = list(reversed(cur))
    return msgs


@app.on_event("startup")
async def _startup() -> None:
    # Initialize the agent once on startup
    global _agent
    _agent = LongevityAgent()

    # Mount static serving for artifacts under /outputs
    global _outputs_dir
    # Prefer env override for consistency with artifacts module
    _outputs_dir = Path(os.getenv("AGENT_OUTPUT_DIR") or (Path(__file__).resolve().parents[2] / "outputs"))
    _outputs_dir.mkdir(parents=True, exist_ok=True)
    try:
        app.mount("/outputs", StaticFiles(directory=str(_outputs_dir), html=False), name="outputs")
    except Exception:
        # If already mounted (e.g., in reload scenarios), ignore
        pass


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")

    if _agent is None:
        raise HTTPException(status_code=500, detail="agent_not_initialized")

    # Session handling and light memory
    session_id = req.session_id or "default"
    hist = _history.get(session_id, [])
    # Build proper structured history for the agent instead of stuffing into a single user message
    pre_msgs = _build_context_messages(hist)

    # Ensure artifacts are isolated per session without clearing previous records
    # Sanitize session id to be filesystem-safe
    safe_session = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in str(session_id))
    outputs_root = _outputs_dir or Path(__file__).resolve().parents[2] / "outputs"
    session_dir = outputs_root / f"session_{safe_session}"
    artifacts_switch_session(str(session_dir))

    # Reset agent conversation so different sessions don't leak memory
    try:
        _agent.reset()
    except Exception:
        pass

    try:
        output = _agent.chat(req.message, pre_messages=pre_msgs) or ""
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"agent_failed: {e}")

    # Update memory
    hist.append((req.message, output))
    _history[session_id] = hist[-16:]

    # Collect artifacts for this session and include URLs
    artifacts = []
    base_url = str(request.base_url).rstrip("/")
    for a in artifacts_list():
        path = Path(a.get("path") or "")
        if not path.exists():
            continue
        try:
            rel = path.resolve().relative_to(outputs_root.resolve())
            url = f"{base_url}/outputs/{str(rel).replace('\\', '/')}"
        except Exception:
            # If not under outputs, fall back to no URL
            url = ""
        artifacts.append({
            "id": a.get("id", ""),
            "label": a.get("label", ""),
            "type": a.get("type", ""),
            "path": str(path),
            "name": path.name,
            "size": path.stat().st_size if path.exists() else 0,
            "url": url,
        })

    tools_used: List[str] = []
    try:
        tools_used = getattr(_agent, "get_tools_used", lambda: [])() or []
    except Exception:
        tools_used = []

    return ChatResponse(output=output, session_id=session_id, artifacts=artifacts, tools_used=tools_used)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host=host, port=port, reload=False)
