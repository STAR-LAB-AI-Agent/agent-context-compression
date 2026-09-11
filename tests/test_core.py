import json
from pathlib import Path

import pytest

from context_compactor.agent import understand
from context_compactor.compressor import CompressionConfig, ContextCompressor
from context_compactor.models import Message
from context_compactor.parser import parse_input, parse_text
from context_compactor.security import resolve_safe_input


MESSAGES = [
    Message("user", "项目必须在周五完成。请使用 Python 实现上下文压缩。", 0),
    Message("assistant", "已决定采用结构化摘要，并保留最近消息。", 1),
    Message("user", "下一步需要编写测试。是否支持 Token 对比？", 2),
]


def test_empty_context_rejected():
    with pytest.raises(ValueError, match="为空"):
        ContextCompressor().compress([])


def test_invalid_ratio_rejected():
    with pytest.raises(ValueError, match="target_ratio"):
        ContextCompressor(CompressionConfig(target_ratio=0))


def test_structured_categories_and_metrics():
    result = ContextCompressor(CompressionConfig(recent_messages=1)).compress(MESSAGES)
    assert result.constraints
    assert result.decisions
    assert result.todos
    assert result.open_questions
    assert result.metrics["tokens_before"] > 0
    assert 0 <= result.metrics["keyword_recall_at_20"] <= 1


def test_recent_messages_preserved_exactly():
    result = ContextCompressor(CompressionConfig(recent_messages=1)).compress(MESSAGES)
    assert result.recent_messages == [{"role": "user", "content": MESSAGES[-1].content}]


def test_natural_language_intents():
    assert understand("请压缩这段对话").name == "compress"
    assert understand("对比压缩前后的 token").name == "evaluate"
    focused = understand("请围绕数据库迁移保留信息")
    assert focused.name == "focused_compress"
    assert focused.focus == "数据库迁移"


def test_parse_chinese_roles():
    rows = parse_text("用户：你好\n助手：你好，需要什么帮助？")
    assert [r.role for r in rows] == ["user", "assistant"]


def test_parse_json_messages(tmp_path: Path):
    path = tmp_path / "chat.json"
    path.write_text(json.dumps({"messages": [{"role": "user", "content": "测试"}]}), encoding="utf-8")
    assert parse_input(path)[0].content == "测试"


def test_directory_whitelist_blocks_escape(tmp_path: Path):
    inside = tmp_path / "safe"
    inside.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("x", encoding="utf-8")
    with pytest.raises(PermissionError):
        resolve_safe_input(str(outside), str(inside))


def test_unsupported_extension(tmp_path: Path):
    path = tmp_path / "data.csv"
    path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="仅支持"):
        resolve_safe_input(str(path), str(tmp_path))
