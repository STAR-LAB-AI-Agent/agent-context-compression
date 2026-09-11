from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .models import CompressionResult, Message
from .tokenizer import count_tokens, tokenize_words

SENTENCE_RE = re.compile(r"(?<=[。！？!?；;])\s*|\n+")
STOPWORDS = {"的", "了", "是", "在", "和", "与", "或", "也", "就", "都", "而", "及", "to", "the", "a", "an", "is", "are", "and", "or"}


@dataclass
class CompressionConfig:
    target_ratio: float = 0.35
    max_tokens: int | None = None
    recent_messages: int = 2
    focus: str = ""
    backend: str = "extractive"

    def validate(self) -> None:
        if not 0.05 <= self.target_ratio <= 1.0:
            raise ValueError("target_ratio 必须在 0.05 到 1.0 之间")
        if self.max_tokens is not None and self.max_tokens < 20:
            raise ValueError("max_tokens 不能小于 20")
        if self.recent_messages < 0:
            raise ValueError("recent_messages 不能为负数")


class ContextCompressor:
    def __init__(self, config: CompressionConfig | None = None):
        self.config = config or CompressionConfig()
        self.config.validate()

    def compress(self, messages: list[Message]) -> CompressionResult:
        if not messages:
            raise ValueError("上下文为空，无法压缩")
        full_text = "\n".join(f"{m.role}: {m.content}" for m in messages)
        sentences = self._sentences(messages)
        recent = messages[-self.config.recent_messages :] if self.config.recent_messages else []
        recent_texts = {m.content for m in recent}
        historical = [(s, role, pos) for s, role, pos in sentences if s not in recent_texts]
        categories = self._classify(historical)
        categorized = {sentence for values in categories.values() for sentence in values}
        # Avoid repeating structured memories in the free-text summary.
        candidates = [(s, role, pos) for s, role, pos in historical if s not in categorized]
        target = max(1, math.ceil(len(candidates) * self.config.target_ratio))
        ranked = self._rank(candidates)
        selected = sorted(ranked[:target], key=lambda x: x[2])
        summary = " ".join(s for s, _, _, _ in selected)

        result = CompressionResult(
            summary=summary,
            facts=categories["facts"],
            decisions=categories["decisions"],
            todos=categories["todos"],
            constraints=categories["constraints"],
            open_questions=categories["open_questions"],
            recent_messages=[{"role": m.role, "content": m.content} for m in recent],
        )
        self._fit_budget(result)
        compact_text = json.dumps(result.to_dict(), ensure_ascii=False, separators=(",", ":"))
        before, method = count_tokens(full_text)
        after, _ = count_tokens(compact_text)
        kept_terms = self._keyword_recall(full_text, compact_text)
        result.metrics = {
            "tokens_before": before,
            "tokens_after": after,
            "tokens_saved": max(0, before - after),
            "compression_ratio": round(after / before, 4) if before else 0,
            "saving_rate": round(1 - after / before, 4) if before else 0,
            "keyword_recall_at_20": kept_terms,
            "tokenizer": method,
            "backend": self.config.backend,
        }
        return result

    def _sentences(self, messages: Iterable[Message]) -> list[tuple[str, str, int]]:
        output, pos = [], 0
        for message in messages:
            for part in SENTENCE_RE.split(message.content):
                sentence = part.strip()
                if len(sentence) >= 2:
                    output.append((sentence, message.role, pos))
                    pos += 1
        return output

    def _rank(self, candidates: list[tuple[str, str, int]]) -> list[tuple[str, str, int, float]]:
        if not candidates:
            return []
        docs = [tokenize_words(s) for s, _, _ in candidates]
        freq = Counter(w for doc in docs for w in doc if w not in STOPWORDS and len(w.strip()) > 0)
        focus_words = set(tokenize_words(self.config.focus))
        ranked = []
        total = len(candidates)
        for (sentence, role, pos), words in zip(candidates, docs):
            useful = [w for w in words if w not in STOPWORDS]
            lexical = sum(freq[w] for w in set(useful)) / max(1, len(useful))
            focus = 3.0 * len(set(useful) & focus_words)
            recency = 1.5 * (pos + 1) / total
            intent = 2.0 if re.search(r"必须|不要|需要|决定|TODO|待办|错误|失败|must|should", sentence, re.I) else 0
            role_bonus = 0.7 if role in {"user", "system"} else 0
            ranked.append((sentence, role, pos, lexical + focus + recency + intent + role_bonus))
        return sorted(ranked, key=lambda row: (-row[3], row[2]))

    def _classify(self, sentences: list[tuple[str, str, int]]) -> dict[str, list[str]]:
        patterns = {
            "decisions": r"决定|确定|采用|选择|结论|agreed|decided",
            "todos": r"待办|TODO|需要|下一步|请|应当|should|need to",
            "constraints": r"必须|不得|不能|限制|只允许|截止|must|never|only",
            "open_questions": r"[？?]$|待确认|不确定|是否|如何|why|how|what",
        }
        out = {"facts": [], "decisions": [], "todos": [], "constraints": [], "open_questions": []}
        for sentence, _, _ in sentences:
            assigned = False
            for name, pattern in patterns.items():
                if re.search(pattern, sentence, re.I):
                    out[name].append(sentence)
                    assigned = True
                    break
            if not assigned and re.search(r"\d|是|为|完成|已|has|was|were", sentence, re.I):
                out["facts"].append(sentence)
        # A small cap keeps the tool result useful as model context instead of becoming a second transcript.
        return {k: self._unique(v)[:3] for k, v in out.items()}

    @staticmethod
    def _unique(items: list[str]) -> list[str]:
        return list(dict.fromkeys(items))

    def _fit_budget(self, result: CompressionResult) -> None:
        if not self.config.max_tokens:
            return
        fields = ["open_questions", "facts", "todos", "decisions", "constraints"]
        while True:
            payload = json.dumps(result.to_dict(), ensure_ascii=False, separators=(",", ":"))
            tokens, _ = count_tokens(payload)
            if tokens <= self.config.max_tokens:
                return
            changed = False
            for field in fields:
                values = getattr(result, field)
                if values:
                    values.pop()
                    changed = True
                    break
            if not changed:
                words = result.summary.split()
                if len(words) <= 1:
                    return
                result.summary = " ".join(words[: max(1, len(words) * 3 // 4)])

    @staticmethod
    def _keyword_recall(source: str, compact: str) -> float:
        source_words = [w for w in tokenize_words(source) if w not in STOPWORDS and len(w) > 1]
        top = [word for word, _ in Counter(source_words).most_common(20)]
        if not top:
            return 1.0
        compact_words = set(tokenize_words(compact))
        return round(sum(w in compact_words for w in top) / len(top), 4)
