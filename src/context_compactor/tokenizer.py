from __future__ import annotations

import re


def count_tokens(text: str) -> tuple[int, str]:
    """Return token count and method; tiktoken is preferred, deterministic fallback otherwise."""
    try:
        import tiktoken

        return len(tiktoken.get_encoding("cl100k_base").encode(text)), "tiktoken/cl100k_base"
    except (ImportError, ValueError):
        # Chinese characters are close to one token each; Latin words/punctuation are counted separately.
        pieces = re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+|[^\s\w]", text)
        return len(pieces), "regex-estimate"


def tokenize_words(text: str) -> list[str]:
    try:
        import jieba

        return [w.strip().lower() for w in jieba.cut(text) if w.strip()]
    except ImportError:
        return [w.lower() for w in re.findall(r"[\u4e00-\u9fff]|[A-Za-z0-9_]+", text)]
