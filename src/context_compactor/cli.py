from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from .agent import understand
from .compressor import CompressionConfig, ContextCompressor
from .parser import parse_input
from .security import resolve_safe_input


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Agent 上下文结构化压缩")
    parser.add_argument("input", help="UTF-8 .txt/.md/.json 文件")
    parser.add_argument("-i", "--instruction", default="请压缩上下文", help="自然语言任务指令")
    parser.add_argument("--ratio", type=float, default=0.35, help="摘要句子保留比例 (0.05~1.0)")
    parser.add_argument("--max-tokens", type=int, help="压缩结果 Token 上限（最小 20）")
    parser.add_argument("--recent", type=int, default=2, help="原样保留的最近消息数")
    parser.add_argument("--root", default=".", help="允许读取的根目录（默认当前目录）")
    parser.add_argument("-o", "--output", help="输出 JSON 文件；不指定则输出到终端")
    parser.add_argument("--pretty", action="store_true", help="格式化 JSON")
    return parser


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("context_compactor")
    try:
        Path("logs").mkdir(exist_ok=True)
        logging.basicConfig(filename="logs/app.jsonl", level=logging.INFO, format="%(message)s", encoding="utf-8")
    except OSError:
        # Compression must remain usable in a read-only or restricted agent workspace.
        logger.addHandler(logging.NullHandler())
    return logger


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log = configure_logging()
    try:
        path = resolve_safe_input(args.input, args.root)
        intent = understand(args.instruction)
        config = CompressionConfig(
            target_ratio=args.ratio,
            max_tokens=args.max_tokens,
            recent_messages=args.recent,
            focus=intent.focus,
        )
        result = ContextCompressor(config).compress(parse_input(path))
        payload = {"intent": intent.name, "intent_explanation": intent.explanation, **result.to_dict()}
        rendered = json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None)
        if args.output:
            output = Path(args.output).resolve()
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(rendered + "\n", encoding="utf-8")
            print(f"完成：{output}")
        else:
            print(rendered)
        log.info(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "event": "compress", "input_bytes": path.stat().st_size, "intent": intent.name, "metrics": result.metrics}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, PermissionError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        log.error(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "event": "error", "type": type(exc).__name__}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
