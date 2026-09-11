from __future__ import annotations

import json
import re
from pathlib import Path

from .models import Message

ROLE_RE = re.compile(r"^(user|assistant|system|tool|用户|助手|系统|工具)\s*[:：]\s*(.*)$", re.I)
ROLE_MAP = {"用户": "user", "助手": "assistant", "系统": "system", "工具": "tool"}


def parse_text(text: str) -> list[Message]:
    text = text.strip()
    if not text:
        return []
    messages: list[Message] = []
    current_role, buffer = "user", []
    for line in text.splitlines():
        match = ROLE_RE.match(line.strip())
        if match:
            if buffer:
                messages.append(Message(current_role, "\n".join(buffer).strip(), len(messages)))
            raw_role, first = match.groups()
            current_role = ROLE_MAP.get(raw_role, raw_role.lower())
            buffer = [first] if first else []
        else:
            buffer.append(line)
    if buffer:
        messages.append(Message(current_role, "\n".join(buffer).strip(), len(messages)))
    return [m for m in messages if m.content]


def parse_input(path: Path) -> list[Message]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        if isinstance(data, dict):
            data = data.get("messages", [])
        if not isinstance(data, list):
            raise ValueError("JSON 顶层必须是消息数组，或包含 messages 数组")
        result = []
        for i, item in enumerate(data):
            if not isinstance(item, dict) or not isinstance(item.get("content"), str):
                raise ValueError(f"第 {i + 1} 条消息缺少字符串 content")
            result.append(Message(str(item.get("role", "user")), item["content"], i))
        return result
    return parse_text(text)
