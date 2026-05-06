from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorkingMemoryItem:
    session_id: str
    turn_id: int
    role: str
    content: str
    created_at: str


@dataclass
class EpisodicMemoryItem:
    session_id: str
    topic: str
    summary: str
    raw_text: str
    source: str = "conversation"
    importance: float = 0.5
    created_at: str = ""


@dataclass
class SemanticMemoryItem:
    category: str
    key: str
    value: str
    source: str = "conversation"
    confidence: float = 0.8
    created_at: str = ""
    updated_at: str = ""


@dataclass
class ProceduralMemoryItem:
    rule_type: str
    rule_text: str
    priority: int = 5
    source: str = "conversation"
    created_at: str = ""
    updated_at: str = ""
    is_active: int = 1


@dataclass
class MemoryExtractionResult:
    episodic: list[EpisodicMemoryItem] = field(default_factory=list)
    semantic: list[SemanticMemoryItem] = field(default_factory=list)
    procedural: list[ProceduralMemoryItem] = field(default_factory=list)
    raw_response: str = ""
    meta: dict[str, Any] = field(default_factory=dict)
