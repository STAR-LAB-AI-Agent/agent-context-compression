from __future__ import annotations

import os
from pathlib import Path


def resolve_safe_input(raw_path: str, allowed_root: str | None = None) -> Path:
    path = Path(raw_path).expanduser().resolve()
    root = Path(allowed_root or os.getenv("CONTEXT_COMPACTOR_ROOT", ".")).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise PermissionError(f"拒绝访问白名单目录之外的文件：{path}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"输入文件不存在：{path}")
    if path.suffix.lower() not in {".txt", ".md", ".json"}:
        raise ValueError("仅支持 .txt、.md、.json 输入")
    if path.stat().st_size > 5 * 1024 * 1024:
        raise ValueError("输入文件超过 5 MB 安全上限")
    return path
