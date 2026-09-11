from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Message:
    role: str
    content: str
    index: int = 0


@dataclass
class CompressionResult:
    summary: str
    facts: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    todos: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    recent_messages: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
