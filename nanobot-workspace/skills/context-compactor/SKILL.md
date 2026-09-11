---
name: context-compactor
description: 压缩长 AI Agent 对话或任务上下文，提取事实、决定、待办、约束、未决问题，并比较压缩前后的 Token 和关键词保留率。
---

# Context Compactor

## 何时使用

当用户要求压缩、整理或精简长对话，围绕指定主题保留上下文，或者评估压缩前后 Token 时使用。

## 操作步骤

1. 将用户提供的对话按 `用户：`、`助手：`、`系统：` 格式保存到工作区的 `inputs/context.txt`。
2. 根据用户原始要求组织自然语言指令，通过 shell 执行：

```powershell
python -m context_compactor inputs/context.txt -i "对比压缩前后的 Token 和质量" --root . --recent 2 --pretty -o outputs/context_result.json
```

3. 读取 `outputs/context_result.json`。
4. 返回摘要、决定、待办、约束和未决问题，并说明 `tokens_before`、`tokens_after`、`tokens_saved`、`saving_rate` 和 `keyword_recall_at_20`。

## 三类意图

- 普通压缩：指令写成“请压缩这段对话”。
- 主题聚焦：指令写成“围绕某个具体主题保留信息”。
- 效果评估：指令写成“对比压缩前后的 Token 和质量”。

## 安全要求

- 始终使用 `--root .`，不得访问工作区之外的输入文件。
- 不得记录或返回 API Key、密码等敏感信息。
- 不得删除或覆盖用户原文件，使用工作副本。
- 命令失败时如实返回错误，不得虚构结果。
- 很短的文本可能因为 JSON 字段开销而没有节省 Token，应如实说明。

## 输出格式

JSON 包含 `summary`、`facts`、`decisions`、`todos`、`constraints`、`open_questions`、`recent_messages` 和 `metrics`。
