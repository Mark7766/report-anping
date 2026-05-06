<!-- ai-coding-ok: v3.0.0 -->
# AGENTS.md — report-anping

## ⚠️ AI Agent Mandatory Spec (run on every task)

This project uses the [ai-coding-ok](https://github.com/Mark7766/ai-coding-ok) three-tier memory system. **You MUST complete the steps below before doing any task work:**

### Plan Phase (mandatory, before starting the task)
1. Read `.github/agent/memory/project-memory.md` — project facts and architectural constraints
2. Read `.github/agent/memory/decisions-log.md` — historical technical decisions
3. Read `.github/agent/memory/task-history.md` — recent task context

### Act Phase (mandatory, after finishing the task)
1. Update `.github/agent/memory/task-history.md` — record a summary of this task
2. If architectural decisions changed → update `.github/agent/memory/decisions-log.md`
3. If project facts changed → update `.github/agent/memory/project-memory.md`

> ⛔ These steps are not optional. If you are using superpowers brainstorming / writing-plans,
> complete the Plan phase **before** calling those skills, and the Act phase **after** they finish.

---

## Project Overview

report-anping 是一个 **Hermes Skill — 地震安全性评价报告生成技能包**。
以 `SKILL.md` + helper scripts 的形式交付，Hermes Agent（LLM）负责与微信用户多轮对话收集安评参数，调用本仓库的确定性脚本生成符合 GB 17741-2025 的 .docx 报告，最终把文件路径告知用户。

领域逻辑（GB 17741 知识库、docx 渲染、prompt 模板）位于本仓库 `lib/` 目录，源自 ajepro 项目的纯函数模块，**已独立拷入本仓库自行维护，不再依赖 ajepro**。

## System Architecture and Data Flow

```
WeChat user
    │
    ▼
Hermes Agent（用自己的 LLM 完成全部对话与生成）
    │  读 SKILL.md 获得领域知识与脚本调用顺序
    │
    ├─▶ bash: python scripts/show_params.py
    │           └→ 输出 13 个参数清单 + GB 17741-2025 章节结构
    │  Hermes 多轮问用户 → 写入 params.json
    │
    ├─▶ bash: python scripts/build_chapter_prompt.py --chapter N --params params.json
    │           └→ stdout 输出该章的 prompt【不调 LLM】
    │  Hermes 用自己的 LLM 生成 markdown → chapters/NN.md
    │  重复直到全部章节完成
    │
    ├─▶ bash: python scripts/render_docx.py --params params.json --chapters chapters/ --out exports/report.docx
    │           └→ 纯确定性渲染（调用本仓库 lib/docx_builder、lib/table_renderer、lib/figure_renderer）
    │
    └─▶ bash: python scripts/check_compliance.py --report exports/report.docx
                └→ 跑 GB 17741 合规检查，输出报告到 stdout
```

- **`SKILL.md`** — Hermes 读的总调度手册：何时触发、互动脚本顺序、错误恢复策略
- **`scripts/show_params.py`** — 打印参数清单与章节结构（调用 `lib/gb17741_knowledge.py`）
- **`scripts/build_chapter_prompt.py`** — 读参数 + 调用 `lib/prompts/` 拼 prompt，**不调 LLM**
- **`scripts/render_docx.py`** — 调用 `lib/docx_builder`、`lib/table_renderer`、`lib/figure_renderer` 拼 .docx
- **`scripts/check_compliance.py`** — 调用 `lib/compliance.py` 规则引擎（无 DB 依赖）
- **`lib/`** — 本仓库自维护的领域逻辑层（源自 ajepro 纯函数模块，去除 Flask/DB/LLM 依赖后独立维护）

## Common Commands

```bash
# 1. 安装依赖
pip install -r requirements.txt
# requirements.txt: python-docx, markdown（lib/ 自维护模块所需，无外部服务依赖）

# 2. 查看参数清单
python scripts/show_params.py

# 3. 手动跳过中间步骤，直接拼 .docx（需预先准备好 chapters/*.md）
python scripts/render_docx.py --params params_example.json --chapters chapters/ --out exports/demo.docx

# 4. Test
pytest tests/

# 5. 安装为 Hermes Skill（user-local）
mkdir -p ~/.hermes/skills/domain && cp -r . ~/.hermes/skills/domain/report-anping/
```

## Conventions and Patterns

- **All files** must start with `from __future__ import annotations`.
- **Logging**: use `logging.getLogger(__name__)`; `print()` is forbidden.
- **SKILL.md frontmatter**：前 3 字节必须是 `---`（不能有前置空行），结尾用 `\n---\n`。必填字段：name ≤ 64、description ≤ 1024、version、author、license、metadata.hermes.tags
- **SKILL.md 正文章节（Hermes 标准）**：
  | 章节 | 说明 |
  |---|---|
  | `# <标题>` | 技能名称 |
  | `## Overview` | 一两段：干什么 + 为什么 |
  | `## When to Use` | 何时触发 + 何时不用 |
  | `## Parameters` | 13 个收集参数说明 |
  | `## Workflow` | 脚本调用顺序与中间产物路径 |
  | `## Common Pitfalls` | 常见错误与解决方案 |
  | `## Verification Checklist` | 验证清单 |
- **Hermes 主导一切 LLM 调用**：脚本本身 **不包含任何 LLM 客户端**；脚本只出静态数据、prompt 文本、或纯渲染输出
- **参数交换格式**：脚本间通过 `params.json`（项目参数）与 `chapters/NN.md`（Hermes 产出的 markdown）交换状态，避免脚本间隐式耦合
- **lib/ 自维护原则**：`lib/` 中的代码是本仓库的一部分，与 ajepro 完全解耦，任何修改直接在本仓库进行；`lib/` 内部只允许 import stdlib 和 `requirements.txt` 中列出的第三方库，**禁止** import 任何 LLM 客户端、Flask、数据库模块
- **输出**：.docx 写入仓库本地 `exports/`，Hermes 读取路径后告知用户

## Test Patterns

```python
# lib/ 模块是纯函数，测试直接传入数据，无需 mock 数据库
def test_build_chapter_prompt():
    params = json.loads(Path('params_example.json').read_text())
    prompt = build_chapter_prompt(params, chapter_id='chapter4')
    assert '工程场地' in prompt
    assert len(prompt) > 100

# 测试 docx 渲染：验证文件生成，不验证内部 XML
def test_render_docx(tmp_path):
    out = tmp_path / 'report.docx'
    render(params=..., chapters_dir=..., out_path=out)
    assert out.exists() and out.stat().st_size > 0
```

## Important Constraints

- **No heavy dependencies** — 禁止引入 Flask、SQLAlchemy、httpx、LLM 客户端等重量依赖；允许：python-docx、markdown、ruff、pytest
- **Sensitive data** — 无密钥/密码；若将来需要签名 URL，通过环境变量注入，不写入代码或日志
- **No database** — 本仓库无数据库，状态全部以文件形式存储（params.json、chapters/*.md）
- **Code limits** — 行宽 120 字符；单函数 ≤ 50 行；单文件 ≤ 500 行
- **lib/ 与 scripts/ 分工**：`lib/` 是纯函数库（可单元测试）；`scripts/` 是 CLI 入口（负责 argparse + 调用 lib/）
