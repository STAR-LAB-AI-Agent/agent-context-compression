from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class AgentIntent:
    name: str
    explanation: str
    focus: str = ""


def understand(instruction: str) -> AgentIntent:
    """Small deterministic intent router: inspect, focused compression, or standard compression."""
    text = instruction.strip()
    if not text:
        return AgentIntent("compress", "未提供指令，执行默认结构化压缩")
    if re.search(r"统计|对比|评估|质量|token|指标|inspect|compare", text, re.I):
        return AgentIntent("evaluate", "压缩并展示 Token 与关键词保留指标")
    focus_match = re.search(
        r"(?:围绕|关注|关于|focus(?: on)?)\s*[“\"']?(.+?)(?=\s*(?:保留|压缩|并(?:对比|比较|展示)|[，。；;\"”']|$))",
        text,
        re.I,
    )
    if focus_match:
        return AgentIntent("focused_compress", "围绕指定主题压缩", focus_match.group(1).strip())
    return AgentIntent("compress", "执行通用结构化压缩")
