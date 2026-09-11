# Nanobot 集成说明

本项目已按教师提供的 `STAR-LAB-AI-Agent/Nanobot` 验证。Nanobot 负责自然语言交互和 Skill 编排，`context-compactor` CLI 负责实际压缩。

## 安装

Python 3.11+ 环境中安装 Nanobot 和本项目：

```powershell
git clone https://github.com/STAR-LAB-AI-Agent/Nanobot.git
python -m pip install -e .\Nanobot
python -m pip install -e ".[dev]"
```

## 安装 Skill

将以下目录复制到 Nanobot 工作区：

```text
nanobot-workspace/skills/context-compactor
```

目标结构：

```text
<workspace>/skills/context-compactor/SKILL.md
```

在工作区中建立 `inputs/` 和 `outputs/`，把对话保存为 `inputs/context.txt`。

## 验证

启动 Nanobot WebUI，选择该工作区，然后输入：

```text
请使用 context-compactor 压缩 inputs/context.txt，并对比压缩前后的 Token。
```

本机验证环境位于 `E:\Nanobot`。实测 Nanobot v0.3.0 能发现此 Skill，项目 9 项测试全部通过，示例从 950 Token 压缩到 696 Token。
