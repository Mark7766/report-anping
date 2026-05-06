# report-anping 开发计划

> 本文档是面向人工 review 的开发计划，覆盖从零到可用的全部工作。
> 开发者（或 AI Agent）在开始编码前须先获得 review 通过。

---

## 背景

report-anping 是一个 Hermes Skill，为微信用户提供地震安全性评价报告（GB 17741-2025）的对话式生成服务。
核心交付物是 `SKILL.md` + 4 个确定性脚本 + `lib/` 领域库。

领域库（`lib/`）的代码源自 ajepro 项目的纯函数模块，已从 ajepro 迁移进本仓库自行维护，不再依赖 ajepro。

架构图：

```
WeChat → Hermes Agent (自己的 LLM)
  ├ bash: show_params.py          → 13 参数清单 + 章节结构
  ├ 多轮对话 → params.json
  ├ 逐章循环: bash build_chapter_prompt.py → Hermes LLM → chapters/NN.md
  ├ bash: render_docx.py          → exports/report.docx
  └ bash: check_compliance.py     → 合规报告 (stdout)
```

---

## 阶段划分

### Phase 1 — lib/ 领域库迁移与清理

**目标**：把 ajepro 的纯函数模块完整迁移进 `lib/`，去除所有外部依赖（Flask/SQLAlchemy/LLM client），通过独立单元测试。

**依赖**：无前置依赖，可直接开始。

#### 任务列表

| # | 任务 | 说明 | 预期产物 |
|---|------|------|--------|
| 1.1 | 复制 JSON 标准数据 | 从 ajepro `backend/data/standards/` 复制 10 个 JSON 文件到 `lib/data/standards/` | `lib/data/standards/*.json` |
| 1.2 | 迁移 `logger.py` | 复制 `backend/utils/logger.py`，**去除** `from flask import g, has_request_context, request`；改用纯 stdlib `threading.local()` 实现 request_id；`get_request_id()` 直接从线程本地存储取 | `lib/logger.py` |
| 1.3 | 迁移 `gb17741_knowledge.py` | 复制 `backend/utils/gb17741_knowledge.py`；将 `_DATA_DIR` 改为指向 `lib/data/standards/`（相对 `__file__`）；所有 import 改为 stdlib only | `lib/gb17741_knowledge.py` |
| 1.4 | 迁移 `docx_builder.py` | 复制 `backend/utils/docx_builder.py`；将 `from backend.utils.logger import get_logger` 改为 `from lib.logger import get_logger` | `lib/docx_builder.py` |
| 1.5 | 迁移 `table_renderer.py` | 复制 `backend/services/table_renderer.py`；同上修改 logger import | `lib/table_renderer.py` |
| 1.6 | 迁移 `figure_renderer.py` | 复制 `backend/services/figure_renderer.py`；同上修改 logger import | `lib/figure_renderer.py` |
| 1.7 | 迁移 `prompts/` | 复制 `backend/prompts/chapter_prompts.py` + `compliance_prompts.py`；将所有 `from backend.` 改为 `from lib.` | `lib/prompts/__init__.py` `lib/prompts/chapter_prompts.py` `lib/prompts/compliance_prompts.py` |
| 1.8 | 新增 `compliance.py` | 从 `backend/services/compliance_service.py` 提取**无 DB 依赖**的规则引擎部分，封装为纯函数 | `lib/compliance.py` |
| 1.9 | 补全 `lib/__init__.py` | 空文件，保证 `from lib.xxx import` 可用 | `lib/__init__.py` |
| 1.10 | 补全 `requirements.txt` | 列出 `python-docx`、`markdown` 及其他 lib/ 所需间接依赖；**禁止** Flask、requests、LLM client | `requirements.txt` |
| 1.11 | 补全 `params_example.json` | 包含 13 个参数字段的完整示例，用于测试 | `params_example.json` |
| 1.12 | 编写 Phase 1 单元测试 | 覆盖 gb17741_knowledge（参数/章节查询）、docx_builder（文档生成）、table_renderer、figure_renderer、compliance（规则检查）；目标覆盖率 ≥ 90% | `tests/test_lib_*.py` |

**验收条件**：
- `pip install -r requirements.txt` 成功，无 Flask/SQLAlchemy/LLM 包
- `pytest tests/test_lib_*.py` 全绿
- `python -c "from lib.gb17741_knowledge import get_chapters_by_level; print(get_chapters_by_level('II'))"` 有输出

---

### Phase 2 — scripts/ CLI 入口

**目标**：编写 4 个 CLI 脚本，每个脚本负责 argparse + 调用 lib/，输出到 stdout 或文件。

**依赖**：Phase 1 完成。

#### 任务列表

| # | 任务 | 说明 | 预期产物 |
|---|------|------|--------|
| 2.1 | `scripts/show_params.py` | `python scripts/show_params.py` 输出 13 个参数字段说明（JSON 或人类可读格式）+ 当前安评级别对应的章节列表；调用 `lib/gb17741_knowledge` | `scripts/show_params.py` |
| 2.2 | `scripts/build_chapter_prompt.py` | `python scripts/build_chapter_prompt.py --chapter <id> --params params.json`；从 params.json 读取项目参数，调用 `lib/prompts/chapter_prompts.py` 拼 prompt，**仅输出到 stdout**，不调 LLM | `scripts/build_chapter_prompt.py` |
| 2.3 | `scripts/render_docx.py` | `python scripts/render_docx.py --params params.json --chapters chapters/ --out exports/report.docx`；遍历 chapters/ 下所有 .md 文件，调用 `lib/docx_builder`、`lib/table_renderer`、`lib/figure_renderer` 渲染为 .docx | `scripts/render_docx.py` |
| 2.4 | `scripts/check_compliance.py` | `python scripts/check_compliance.py --report exports/report.docx`；调用 `lib/compliance` 规则引擎，输出合规检查报告到 stdout（JSON 或人类可读格式） | `scripts/check_compliance.py` |
| 2.5 | 编写 Phase 2 集成测试 | 用 tmp_path 创建临时 chapters/*.md、params_example.json，跑完整 render_docx 流程，验证 .docx 存在且 > 0 字节；用 mock chapters 验证 check_compliance 返回无错误 | `tests/test_scripts_*.py` |

**验收条件**：
- `python scripts/show_params.py` 输出 13 字段列表和章节结构，无报错
- `python scripts/build_chapter_prompt.py --chapter chapter4 --params params_example.json` 输出 > 100 字符的 prompt 文本
- `python scripts/render_docx.py --params params_example.json --chapters tests/fixtures/chapters/ --out /tmp/demo.docx` 生成可打开的 .docx
- `pytest tests/test_scripts_*.py` 全绿

---

### Phase 3 — SKILL.md 编写

**目标**：按 Hermes 标准格式编写 `SKILL.md`，作为 Hermes Agent 的调度手册。

**依赖**：Phase 2 完成（需要明确脚本的实际 CLI 参数）。

#### 任务列表

| # | 任务 | 说明 | 预期产物 |
|---|------|------|--------|
| 3.1 | 编写 SKILL.md frontmatter | name、description（≤ 1024）、version、author、license、metadata.hermes.tags；前 3 字节必须是 `---` | `SKILL.md` frontmatter |
| 3.2 | 编写 `## Overview` | 1–2 段：本 skill 干什么、为什么用它而非其他方式 | — |
| 3.3 | 编写 `## When to Use` | 触发条件（用户发起安评报告生成请求）+ 不用场景（非安评、非 GB 17741） | — |
| 3.4 | 编写 `## Parameters` | 列出 13 个参数、每个的含义、示例值、是否必填 | — |
| 3.5 | 编写 `## Workflow` | 逐步列出 Hermes 的操作流程：脚本调用顺序、预期输入/输出、中间文件路径（params.json、chapters/NN.md）、最终产物路径（exports/*.docx）| — |
| 3.6 | 编写 `## Common Pitfalls` | 参数收集不完整、chapters/ 为空、docx 路径权限问题等 | — |
| 3.7 | 编写 `## Verification Checklist` | Hermes 完成后的自检清单：exports/*.docx 存在、合规检查通过、路径告知用户 | — |
| 3.8 | 校验 SKILL.md 合规 | 验证：`wc -c SKILL.md` ≤ 100,000；description 长度 ≤ 1024；前 3 字节是 `---` | — |

**验收条件**：
- `python -c "import yaml, pathlib; fm = pathlib.Path('SKILL.md').read_text().split('---')[1]; yaml.safe_load(fm)"` 解析成功
- `wc -c SKILL.md` 输出 ≤ 100000
- Hermes 加载后能看到 skill 描述（新 session 测试）

---

### Phase 4 — 集成验证与收尾

**目标**：端到端跑通完整流程，补全 README，准备发布。

**依赖**：Phase 1–3 全部完成。

#### 任务列表

| # | 任务 | 说明 | 预期产物 |
|---|------|------|--------|
| 4.1 | 准备测试 fixtures | 创建 `tests/fixtures/chapters/` 下的 mock .md 章节文件，用于集成测试 | `tests/fixtures/` |
| 4.2 | 端到端脚本联调 | 手动按 SKILL.md Workflow 顺序跑一遍：show_params → 手写 params.json → 逐章 build_chapter_prompt → 手写 chapters/ → render_docx → check_compliance | 可用的 exports/demo.docx |
| 4.3 | CI 配置验证 | 确认 `.github/workflows/ci.yml` 能跑通：pip install、ruff check、pytest；SKILL.md frontmatter 校验步骤可用 | CI 全绿 |
| 4.4 | 编写 README.md | 快速上手（安装 + 最小示例）、目录结构说明、如何安装为 Hermes Skill | `README.md` |
| 4.5 | 安装为 Hermes Skill 验证 | `cp -r . ~/.hermes/skills/domain/report-anping/`；新开 Hermes session，触发 skill，确认能加载 SKILL.md | — |

**验收条件**：
- CI 全绿（ruff + pytest）
- Hermes 新 session 里输入触发词，skill 正常响应并调用 show_params.py
- 完整流程产出 exports/demo.docx，可用 Word 打开

---

## 文件交付清单

```
report-anping/
├── SKILL.md                        Phase 3
├── scripts/
│   ├── show_params.py              Phase 2.1
│   ├── build_chapter_prompt.py     Phase 2.2
│   ├── render_docx.py              Phase 2.3
│   └── check_compliance.py         Phase 2.4
├── lib/
│   ├── __init__.py                 Phase 1.9
│   ├── logger.py                   Phase 1.2
│   ├── gb17741_knowledge.py        Phase 1.3
│   ├── docx_builder.py             Phase 1.4
│   ├── table_renderer.py           Phase 1.5
│   ├── figure_renderer.py          Phase 1.6
│   ├── compliance.py               Phase 1.8
│   ├── prompts/
│   │   ├── __init__.py             Phase 1.7
│   │   ├── chapter_prompts.py      Phase 1.7
│   │   └── compliance_prompts.py   Phase 1.7
│   └── data/
│       └── standards/              Phase 1.1（10 个 JSON）
├── references/                     Phase 4（可选，放 GB 17741 摘要）
├── tests/
│   ├── fixtures/
│   │   └── chapters/               Phase 4.1
│   ├── test_lib_gb17741.py         Phase 1.12
│   ├── test_lib_docx.py            Phase 1.12
│   ├── test_lib_compliance.py      Phase 1.12
│   ├── test_scripts_show_params.py Phase 2.5
│   ├── test_scripts_build_prompt.py Phase 2.5
│   └── test_scripts_render_docx.py Phase 2.5
├── params_example.json             Phase 1.11
├── requirements.txt                Phase 1.10
└── README.md                       Phase 4.4
```

---

## 关键约束（编码时必须遵守）

1. 所有 `.py` 文件第一行：`from __future__ import annotations`
2. 单函数 ≤ 50 行，单文件 ≤ 500 行，行宽 120 字符
3. `lib/` 内只允许 import stdlib 和 `requirements.txt` 中的库，**禁止** import Flask、SQLAlchemy、任何 LLM client
4. `scripts/` 内禁止 LLM 调用；所有逻辑下沉到 `lib/`
5. 日志用 `logging.getLogger(__name__)`，禁止 `print()`
6. 不硬编任何密钥或路径（路径用 `pathlib.Path(__file__).parent` 计算相对路径）

---

## 参考

- 源码参考（只读，不依赖）：`/Users/mark/work/gitspace/opensource/ajepro/backend/`
- Hermes Skill 标准：`~/.hermes/skills/` 下其他 skill 的 SKILL.md 结构
- GB 17741-2025：见 `lib/data/standards/` 迁移后的 JSON 文件
