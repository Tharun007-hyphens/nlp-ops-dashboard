"""FastAPI service exposing the redactor for the React dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from redactor import redact_string

app = FastAPI(title="NLP Redaction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RedactFlags(BaseModel):
    names: bool = False
    dates: bool = False
    phones: bool = False
    address: bool = False
    emails: bool = False


class RedactRequest(BaseModel):
    text: str = Field(default="", max_length=500_000)
    flags: RedactFlags = Field(default_factory=RedactFlags)
    concept: str | None = Field(default=None, max_length=200)


class RedactResponse(BaseModel):
    redacted_text: str
    stats: dict[str, int]
    original_length: int


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/redact", response_model=RedactResponse)
def redact(req: RedactRequest) -> RedactResponse:
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty.")
    active = req.flags.model_dump()
    if not any(active.values()) and not (req.concept and req.concept.strip()):
        raise HTTPException(
            status_code=400,
            detail="Enable at least one redaction flag or enter a concept.",
        )
    try:
        redacted, stats = redact_string(req.text, active, req.concept or None)
    except Exception as exc:  # noqa: BLE001 — surface model/pipeline errors to client
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return RedactResponse(
        redacted_text=redacted,
        stats=stats,
        original_length=len(req.text),
    )
