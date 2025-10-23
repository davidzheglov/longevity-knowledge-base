from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_SESSION: Dict[str, object] = {
    "run_dir": None,  # type: ignore
    "registry": [],   # type: ignore
}


@dataclass
class Artifact:
    id: str
    label: Optional[str]
    path: str
    type: Optional[str]
    created_at: float


def _now() -> float:
    return time.time()


def get_run_dir() -> Path:
    rd = _SESSION.get("run_dir")
    if rd is None:
        # Default to outputs/session_<timestamp>; prefer env var to stay consistent with server
        base_env = os.getenv("AGENT_OUTPUT_DIR")
        if base_env:
            base = Path(base_env)
        else:
            # Align with server default: parents[3] == /app when this file is under /app/llm-agent/src/integration
            base = Path(__file__).resolve().parents[3] / "outputs"
        base.mkdir(parents=True, exist_ok=True)
        rd = base / f"session_{int(_now())}"
        rd.mkdir(parents=True, exist_ok=True)
        _SESSION["run_dir"] = rd
        _save_registry()
    return rd  # type: ignore


def start_session(run_dir: Optional[str] = None, label: Optional[str] = None) -> Path:
    base_env = os.getenv("AGENT_OUTPUT_DIR")
    if base_env:
        base = Path(base_env)
    else:
        base = Path(__file__).resolve().parents[3] / "outputs"
    base.mkdir(parents=True, exist_ok=True)
    if run_dir:
        rd = Path(run_dir)
    else:
        rd = base / (
            f"session_{label}_{int(_now())}" if label else f"session_{int(_now())}"
        )
    rd.mkdir(parents=True, exist_ok=True)
    _SESSION["run_dir"] = rd
    _SESSION["registry"] = []
    _save_registry()
    return rd

def switch_session(run_dir: str) -> Path:
    """Switch the current artifact session directory without clearing registry.

    If the directory doesn't exist, it will be created. If an artifacts.json exists,
    it will be loaded; otherwise the registry will remain empty until artifacts are added.
    """
    rd = Path(run_dir)
    rd.mkdir(parents=True, exist_ok=True)
    _SESSION["run_dir"] = rd
    # Load existing registry if present (does not clear)
    _load_registry()
    return rd


def _registry_file() -> Path:
    return get_run_dir() / "artifacts.json"


def _save_registry() -> None:
    reg: List[Artifact] = _SESSION.get("registry", [])  # type: ignore
    data = [asdict(a) for a in reg]
    _registry_file().write_text(json.dumps(data, indent=2), encoding="utf-8")


def _load_registry() -> List[Artifact]:
    p = _registry_file()
    if p.exists():
        try:
            arr = json.loads(p.read_text(encoding="utf-8"))
            arts = [Artifact(**x) for x in arr]
            _SESSION["registry"] = arts
            return arts
        except Exception:
            pass
    _SESSION["registry"] = []
    return []


def ensure_unique_path(requested_path: str) -> Path:
    path = Path(requested_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 1
    while True:
        cand = parent / f"{stem}_{i}{suffix}"
        if not cand.exists():
            return cand
        i += 1


def register_artifact(path: str, type: Optional[str] = None, label: Optional[str] = None) -> str:
    rp = str(Path(path).resolve())
    artifact = Artifact(id=str(uuid.uuid4())[:8], label=label, path=rp, type=type, created_at=_now())
    arts: List[Artifact] = _SESSION.get("registry") or []  # type: ignore
    arts.append(artifact)
    _SESSION["registry"] = arts
    _save_registry()
    return artifact.id


def list_artifacts(artifact_type: Optional[str] = None) -> List[Dict[str, str]]:
    arts = _SESSION.get("registry")
    if not arts:
        arts = _load_registry()
    out: List[Dict[str, str]] = []
    for a in arts:  # type: ignore
        if artifact_type and a.type != artifact_type:
            continue
        out.append({
            "id": a.id,
            "label": a.label or "",
            "path": a.path,
            "type": a.type or "",
        })
    return out


def resolve_artifact(id_or_label: str) -> Optional[str]:
    arts = _SESSION.get("registry")
    if not arts:
        arts = _load_registry()
    for a in arts:  # type: ignore
        if a.id == id_or_label or (a.label and a.label == id_or_label):
            return a.path
    return None


def search_artifacts(name_substring: str) -> List[Dict[str, str]]:
    """Search artifacts by basename substring (case-insensitive)."""
    arts = _SESSION.get("registry")
    if not arts:
        arts = _load_registry()
    name_sub = name_substring.lower()
    results: List[Dict[str, str]] = []
    for a in arts:  # type: ignore
        base = os.path.basename(a.path).lower()
        if name_sub in base:
            results.append({
                "id": a.id,
                "label": a.label or "",
                "path": a.path,
                "type": a.type or "",
            })
    return results
