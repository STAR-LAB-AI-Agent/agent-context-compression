# AI Agent 上下文压缩

课程实验第 17 题的完整可运行实现：把较长的智能体对话压缩成结构化记忆，在保留事实、决定、待办、约束、未决问题和近期消息的同时，减少后续模型调用的 Token 消耗。项目默认离线运行，不需要 API Key。

完全没有 Python 或 AI Agent 基础时，请先阅读 `新手使用说明.md`，然后依次双击 `一键安装.bat` 和 `一键验证.bat`。

## Nanobot 集成

项目已适配教师提供的 `STAR-LAB-AI-Agent/Nanobot`。可直接把 `nanobot-workspace/skills/context-compactor` 复制到 Nanobot 工作区的 `skills/` 下。完整安装和验证步骤见 `NANOBOT_DEPLOYMENT.md`。

## 用户场景与三类意图

1. **通用压缩**：“把这段长对话压缩一下，保留最近两轮。”
2. **主题聚焦压缩**：“围绕数据库迁移保留关键信息。”
3. **压缩评估**：“对比压缩前后 Token 和质量。”

自然语言入口由确定性路由器识别意图，再调用独立 Script/CLI。这样无需联网即可稳定演示“自然语言 → 智能体 → Skill → CLI → 开源能力 → JSON 结果”的完整闭环。

## 架构

```text
自然语言指令 ─→ 意图路由 agent.py ─┐
                                    ├→ compressor.py ─→ 结构化 JSON
TXT/MD/JSON ─→ parser.py ───────────┘        │
      │                                      ├→ Token 对比
      └→ security.py 白名单/类型/大小校验    └→ 关键词保留率
```

压缩器先按角色解析消息、按句切分，使用词频、主题匹配、近期性、角色和任务信号进行抽取式排序；同时用规则抽取结构化记忆。最近 N 条消息原样保留，防止当前任务状态丢失。

## 安装

建议 Python 3.10～3.12：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

安装后会生成 `context-compactor` 命令。也可在项目目录执行：

```powershell
$env:PYTHONPATH = 'src'
python -m context_compactor examples/sample_chat.txt --root . --pretty
```

## 使用

通用压缩：

```powershell
context-compactor examples/sample_chat.txt -i "请压缩上下文" --root . --pretty
```

主题聚焦：

```powershell
context-compactor examples/sample_chat.txt -i "围绕安全约束保留信息" --ratio 0.3 --root . --pretty
```

评估并保存：

```powershell
context-compactor examples/sample_chat.json -i "对比压缩前后的 Token 和质量" --max-tokens 500 --root . --pretty -o outputs/result.json
```

输入文本的角色格式可用 `user:`、`assistant:`、`system:`，也支持“用户：”“助手：”“系统：”。JSON 可直接使用消息数组，或 `{"messages": [...]}`。

主要参数：

| 参数 | 说明 |
|---|---|
| `--instruction` | 自然语言指令 |
| `--ratio` | 摘要句子保留比例，0.05～1.0 |
| `--max-tokens` | 输出预算，最小 20 |
| `--recent` | 原样保留的最近消息数 |
| `--root` | 可读取文件的白名单根目录 |
| `--output` | 可选 JSON 输出路径 |

完整工具约定与示例见 `SKILL.md`。一键演示可运行 `demo.ps1`，讲稿见 `DEMO_SCRIPT.md`。

## 输出与指标

输出包含摘要和五类结构化记忆。`metrics` 给出：

- `tokens_before` / `tokens_after` / `tokens_saved`
- `compression_ratio` 与 `saving_rate`
- `keyword_recall_at_20`：源文本高频 Top-20 关键词在压缩结果中的保留比例
- `tokenizer`：实际计数方法

这实现了题目推荐的“压缩前后质量与 Token 对比”。指标是可复现的自动代理指标，并不等同于人工语义正确率。

## 测试

```powershell
pytest -q
```

共 9 个测试，覆盖：空输入、非法比例、结构化字段、近期消息保真、三类意图、中文角色解析、JSON 输入、目录越界和非法扩展名。

## 安全与日志

- 输入只能位于 `--root` 白名单目录内，仅接受 `.txt/.md/.json`，大小上限 5 MB。
- 默认无网络、无外部模型、无密钥；`.env.example` 不含真实凭据。
- 日志位于 `logs/app.jsonl`，只记录时间、事件、输入字节数、意图和指标，不记录上下文正文。
- 输出文件是显式参数；程序没有删除、移动或覆盖输入文件的能力。

## 开源依赖与许可证

| 项目 | 版本 | 许可证 | 实际用途 |
|---|---:|---|---|
| jieba | 0.42.1 | MIT | 中文分词，用于句子评分和关键词保留率 |
| tiktoken | ≥0.7,<1 | MIT | `cl100k_base` Token 统计 |
| pytest | ≥8,<10 | MIT | 自动化测试（开发依赖） |
程序在 jieba 或 tiktoken 缺失时分别使用字符/单词切分和正则估算降级，便于无网络现场演示；正式指标建议安装完整依赖。

## 已知问题

- 当前核心算法为抽取式压缩，不会改写或推理隐含信息；专业领域仍需人工抽查。
- 中文规则分类依赖显式关键词，含蓄表达可能归类不完整。
- `max_tokens` 是软预算：为保证最近消息与关键约束不被截断，极小预算可能无法严格达到。
- Top-20 关键词保留率是低成本代理指标，不能替代人工事实一致性评价。
