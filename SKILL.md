---
name: context-compactor
description: 压缩长智能体对话或任务上下文，提取事实、决定、待办、约束和未决问题，并比较压缩前后 Token 与质量指标。
---

# Context Compactor Skill

## 何时使用

- 对话过长，需要在继续任务前压缩上下文。
- 用户要求只保留某个主题相关的信息。
- 用户要求评估压缩率、Token 节省量或关键词保留率。

不要用于需要逐字保真的法律文本、合同或代码文件；这类内容应保留原文或专用摘要。

## 参数

- `input`：白名单目录内的 UTF-8 `.txt`、`.md` 或消息数组 `.json`。
- `instruction`：自然语言指令，支持通用压缩、主题聚焦、指标评估三类意图。
- `ratio`：摘要句子保留比例，范围 0.05～1.0，默认 0.35。
- `max_tokens`：可选的压缩结果 Token 上限，最小 20。
- `recent`：原样保留的最近消息数，默认 2。
- `root`：输入文件白名单根目录。

## 调用

```powershell
context-compactor examples/sample_chat.txt --root . --pretty
```

智能体应先解析用户指令，再组织参数调用 CLI。CLI 非零退出时，将简短错误反馈给用户，不要绕过目录白名单。

## 结果格式

JSON 包含：`intent`、`summary`、`facts`、`decisions`、`todos`、`constraints`、`open_questions`、`recent_messages`、`metrics`。其中 `metrics` 含压缩前后 Token、节省量、压缩率、节省率、Top-20 关键词保留率和计数方法。

## 示例

1. “压缩这段对话，保留最近 2 条消息”：

```powershell
context-compactor examples/sample_chat.txt -i "请压缩这段对话" --recent 2 --root . --pretty
```

2. “围绕安全约束压缩，并比较 Token”：

```powershell
context-compactor examples/sample_chat.txt -i "围绕安全约束保留信息并对比 Token" --ratio 0.3 --root . --pretty
```
