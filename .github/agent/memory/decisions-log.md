# 📝 report-anping — Technical Decisions Log (ADR)

> **Purpose**: record every important technical decision so they remain traceable and understandable.
> Format reference: [Architecture Decision Records](https://adr.github.io/).

---

## ADR Template

Copy the template below to record a new decision:

```markdown
### ADR-{number}: {title}

- **Date**: YYYY-MM-DD
- **Status**: ✅ Adopted / ❌ Deprecated / 🔄 Superseded
- **Decision maker**: {person/agent}

#### Context
> Why is this decision needed? What problem are we facing?

#### Options

| Option | Pros | Cons |
|------|------|------|
| Option A | ... | ... |
| Option B | ... | ... |

#### Decision
> Which option did we pick?

#### Rationale
> Why this option?

#### Impact
> What will this decision affect?
```

---

## Decision Records

### ADR-001: 技术栈选型 — FastAPI + SQLite + uv + ruff

- **Date**: 2026-05-05
- **Status**: ❌ Deprecated — 被 ADR-003 取代
- **Decision maker**: 项目初始化阶段 (AI Agent)

#### Context
> report-anping 是个人/小团队工具，目标用户规模 1–10 人。需要一个部署简单、维护成本低的全栈方案。

#### Options

| Option | Pros | Cons |
|------|------|------|
| FastAPI + SQLite + uv | 异步 webhook、自动 OpenAPI、零运维、包管理快 | 适合个人工具规模 |
| Flask + Postgres + pip | 贴近 ajepro 旧栈 | 需要 Postgres 服务、pip 较慢 |
| FastAPI + Postgres + SQLAlchemy async | 生产级性能 | 运维复杂度过高，违背极简原则 |

#### Decision
> 选择 **FastAPI + SQLite + SQLAlchemy (sync) + uv + ruff**。

#### Rationale
> 1. FastAPI 原生支持 async，适合 Hermes webhook 异步处理，比 Flask 更合适。
> 2. SQLite 零运维，个人工具首选，无需独立数据库服务。
> 3. SQLAlchemy sync 比 async 简单，与 SQLite 配合更自然，避免过度抽象。
> 4. uv 比 pip 安装快，内置虚拟环境管理；ruff 一次解决 lint + format。

#### Impact
> - 所有模块使用 FastAPI Router，不再使用 Flask Blueprint
> - 数据库文件存于 `data/report_anping.db`，不需要 migration 工具（开发阶段用 `Base.metadata.create_all`）
> - CI 使用 `astral-sh/setup-uv` action

---

### ADR-002: 不重写 LLM prompt，复用 ajepro 提示词模式

- **Date**: 2026-05-05
- **Status**: ❌ Deprecated — 被 ADR-006 取代
- **Decision maker**: 项目初始化阶段 (AI Agent)

#### Context
> ajepro 已经包含经过验证的 GB 17741-2025 安评报告 prompt 模板。

#### Decision
> report-anping 的 `scripts/generate_report.py` 直接调用 ajepro 的脚本/引擎，而不重复实现。

#### Rationale
> 避免重复制造已验证的核心逻辑，减少维护成本。

#### Impact
> ajepro 小版本升级时需评估对 report-anping 的影响。

---

### ADR-003: Hermes Skill 架构——无服务器模型，Skill = SKILL.md + scripts

- **Date**: 2026-05-05
- **Status**: ✅ Adopted
- **Decision maker**: 架构受诞f后修正 (AI Agent)

#### Context
> ADR-001 错误地将 Skill 设计为一个完整的 FastAPI 服务，包含自己的对话管理、数据库、LLM 调用。但 Hermes 的 Skill 模型实际上是：全部对话由 Hermes LLM 处理，Skill 只提供领域知识（SKILL.md）和 helper scripts。

#### Options

| Option | Pros | Cons |
|------|------|------|
| 无服务器：Skill.md + scripts | 极简、无运维、符合 Hermes 设计哲学 | 不适合需要自己持久化状态的场景 |  
| 服务器模型：FastAPI + SQLite | 可自定义对话逻辑 | 重复建造 Hermes 已提供的能力，违背 Skill 定义 |

#### Decision
> 选择无服务器模型。

#### Rationale
> Hermes 已经提供对话管理、session 维护、LLM 调用。Skill 在此基础上只需贡献领域知识＋实现脚本，而不是重复造轮。

#### Impact
> - 删除所有 src/、数据库、FastAPI 设计
> - 核心交付物是 `SKILL.md` + `scripts/generate_report.py`
> - CI 只需运行 `pytest tests/`，无需部署服务

---

### ADR-004: ajepro 集成方式 — HTTP REST API 客户端

- **Date**: 2026-05-05
- **Status**: ❌ Deprecated — 被 ADR-005 取代
- **Decision maker**: 架构 review (AI Agent)

#### Context
> Review ajepro 源码后发现：ajepro 是 Flask Web 应用，没有独立的 CLI 命令，报告生成是多步异步流程（建项目 → 启动任务 → 轮询进度 → 导出 .docx），状态绑定 SQLite + 内存 task_manager。无法以"调用一个 CLI"的方式直接复用。

#### Options

| Option | Pros | Cons |
|------|------|------|
| HTTP REST API 客户端（用户预启动 ajepro 服务） | 完全解耦、ajepro 升级不影响 Skill、可远程部署 ajepro | 用户需提前启动 ajepro 服务 |
| Import ajepro 为 Python 模块 | 一进程内调用 | 强耦合 ajepro 内部 API、需共享 venv 与 SQLite、安装路径冲突 |
| subprocess 拉起 ajepro 临时服务 | 用户无感 | 启动慢、生命周期管理复杂、端口冲突风险 |

#### Decision
> **选择 HTTP REST API 客户端模型**。Skill 通过 `requests` 调用 ajepro 暴露的 `/api/projects`、`/api/reports/generate/<id>/async`、`/api/reports/task/<task_id>`、`/api/reports/<report_id>/export` 四个端点。BaseURL 由环境变量 `AJEPRO_BASE_URL` 提供，默认 `http://localhost:5000`。

#### Rationale
> 1. ajepro 已经把这些端点稳定地暴露出来，是它对外的"公开契约"
> 2. 完全解耦：ajepro 可独立升级、独立部署（甚至跑在远端服务器）
> 3. 测试简单：用 `responses` 库 mock HTTP 响应即可
> 4. Skill 自身保持极简（仅依赖 `requests` + `python-dotenv`）

#### Impact
> - SKILL.md 的 Prerequisites 段必须明确告知用户："使用前请确保 ajepro 服务已启动且 QWEN_API_KEY 已配置"
> - `scripts/check_ajepro.py` 在每次执行前做健康检查，给出友好提示
> - 异步轮询超时设为 600s（ajepro 多章节生成可能耗时数分钟）
> - 不依赖 ajepro 的 `.venv` 或数据库文件路径

---

### ADR-005: ajepro 集成方式 — 拆为多个无状态脚本，由 Hermes 编排

- **Date**: 2026-05-05
- **Status**: ✅ Adopted（取代 ADR-004）
- **Decision maker**: 用户提出疑问后修正 (AI Agent)

#### Context
> 用户指出 ADR-004 让 ajepro 作为独立 Flask 服务运行、自管 LLM，没有充分利用 Hermes Agent 的核心优势——Hermes 本身就是 LLM 编排者。正确做法应是 Hermes 直接基于 SKILL.md 调用一组无状态脚本。
>
> 阅读 ajepro 源码确认：`backend/prompts/`、`backend/utils/gb17741_knowledge.py`、`backend/utils/docx_builder.py`、`backend/services/table_renderer.py`、`backend/services/figure_renderer.py` 都是无状态、无 LLM 依赖、无 DB 依赖的纯逻辑模块，可以被脚本直接 import。

#### Options

| Option | Pros | Cons |
|------|------|------|
| 多脚本 + Hermes 编排（当前选择） | Hermes 主导 LLM、无服务器、零运维、最贴 Skill 范式 | 需为每个动作切一个脚本入口 |
| HTTP 客户端调 ajepro 服务（ADR-004） | 完全解耦 ajepro | 用户需先启动服务、Skill 重复 ajepro 已有的 LLM 调用逻辑、未利用 Hermes |
| import ajepro 全栈（含 Flask 上下文） | 一进程 | 需要 SQLite/Flask 环境，违背极简 |

#### Decision
> 采用 **Hermes 编排 × 多脚本** 模型。脚本只做四件事：
> 1. `show_params.py` — 打印参数清单与章节结构
> 2. `build_chapter_prompt.py` — 拼某章 prompt 到 stdout（**不调 LLM**）
> 3. `render_docx.py` — 把 chapters/*.md 渲染为 .docx
> 4. `check_compliance.py` — 跑 GB 17741 合规检查

#### Rationale
> 1. Hermes 是 LLM 编排引擎，重复实现 LLM 调用是浪费
> 2. 无服务器 = 零运维：用户不必启动 ajepro，也不必配置 QWEN_API_KEY
> 3. 脚本边界清晰，每个脚本可独立单元测试
> 4. 状态以 `params.json` + `chapters/*.md` 落盘，避免脚本间隐式耦合
> 5. 完全符合 hermes-agent skills 仓库中其他 skill 的范式（参考 `notion`、`ocr-and-documents`）

#### Impact
> - 删除 `scripts/generate_report.py`、`ajepro_client.py`、`check_ajepro.py` 设计
> - 不再需要 `requests` 依赖；不再需要 `AJEPRO_BASE_URL` 环境变量
> - SKILL.md `## Workflow` 段落需详细列出脚本调用顺序与中间产物路径
> - 新增 `lib/` 纯函数层，直接 import，无需 sys.path 适配（详见 ADR-006）
> - ajepro 仓库无需修改

---

### ADR-006: 领域代码自维护 — 拷贝 ajepro 纯函数模块，在本仓库独立维护

- **Date**: 2026-05-05
- **Status**: ✅ Adopted（取代 ADR-002、ADR-005 中"import ajepro"的表述）
- **Decision maker**: 用户明确要求 (AI Agent)

#### Context
> 用户明确指出 ajepro 项目将不再维护，不应再依赖它（无论是 import 还是 sys.path 注入方式）。需要把所需的纯函数模块完整拷贝进本仓库，作为本仓库代码自行维护。

#### Options

| Option | Pros | Cons |
|------|------|------|
| 拷贝代码到本仓库 `lib/` 自维护（当前选择） | 零外部依赖、代码可控、ajepro 废弃不影响本项目 | 初期需要一次性迁移与清理工作 |
| 继续 import ajepro（sys.path 方式） | 无需拷贝 | ajepro 停维护后代码腐烂；需要用户本地有 ajepro 仓库 |
| 重写全部领域逻辑 | 完全自主 | 工作量大，已有经过验证的代码无需重写 |

#### Decision
> **拷贝 ajepro 中以下纯函数模块到本仓库 `lib/` 目录，修改后独立维护**：
> - `backend/utils/logger.py` → `lib/logger.py`（去除 Flask 依赖）
> - `backend/utils/gb17741_knowledge.py` → `lib/gb17741_knowledge.py`（调整 `_DATA_DIR` 路径）
> - `backend/utils/docx_builder.py` → `lib/docx_builder.py`（import 路径改为 `lib.*`）
> - `backend/services/table_renderer.py` → `lib/table_renderer.py`（import 路径改为 `lib.*`）
> - `backend/services/figure_renderer.py` → `lib/figure_renderer.py`（import 路径改为 `lib.*`）
> - `backend/prompts/chapter_prompts.py` + `compliance_prompts.py` → `lib/prompts/`（import 路径改为 `lib.*`）
> - `backend/data/standards/*.json`（10 个文件）→ `lib/data/standards/`

#### Rationale
> 1. 外部依赖归零：本仓库完全独立，不需要用户安装 ajepro
> 2. 代码可控：可按本项目需求自由修改，不受 ajepro 历史包袱约束
> 3. 迁移成本低：ajepro 的纯函数模块本身无副作用，主要是 import 路径的批量替换
> 4. 符合极简主义原则：单一仓库，单一 pip install，直接 pytest

#### Impact
> - `lib/` 成为本仓库的一等公民（不再是 `scripts/lib/` 的适配层）
> - `requirements.txt` 只需 `python-docx`、`markdown`（无 ajepro 依赖）
> - 所有 `from backend.xxx import` 改为 `from lib.xxx import`
> - `lib/logger.py` 去除 `from flask import g, has_request_context, request` 相关代码
> - `lib/gb17741_knowledge.py` 中 `_DATA_DIR` 改为指向 `lib/data/standards/`
> - 开发时**不需要** ajepro 仓库存在于本地

---

### ADR-007: 图件能力实现策略 — 确定性图件引擎 + CEIC 导出目录输入

- **Date**: 2026-05-08
- **Status**: ✅ Adopted
- **Decision maker**: 功能增强阶段 (AI Agent)

#### Context
> 用户要求增强报告专业性，新增“基于数据自动生成图件”与“基于 CEIC 地震目录生成 M-T 图”能力。CEIC 页面在线抓取存在动态渲染/反爬不稳定因素，直接在线解析风险高。

#### Options

| Option | Pros | Cons |
|------|------|------|
| 在线抓取 CEIC 页面并实时解析 | 自动化程度高 | 稳定性差、易受前端改版影响、测试不可重复 |
| 读取 CEIC 导出的 CSV/JSON（当前选择） | 稳定、可测试、可离线复现 | 需要用户先导出目录文件 |
| 手工维护地震目录文本 | 最简单 | 不可规模化、易出错 |

#### Decision
> 采用“**确定性图件引擎 + CEIC 导出目录输入**”方案：
> - 在 `lib/chart_builder.py` 实现通用图件生成（M-T、反应谱、PGA 对比）
> - 提供 `scripts/generate_figures.py` 与 `scripts/build_mt_chart.py` 作为 CLI 入口
> - 在章节 prompt 中规范 Markdown 图片引用路径，由 `render_docx.py` 统一落版

#### Rationale
> 1. 保持 Skill 一贯的 deterministic 架构，不引入在线依赖脆弱点。
> 2. 测试可重复（fixture 目录可稳定覆盖）。
> 3. 用户真实业务流程通常已包含目录导出/整理环节，CSV/JSON 输入契合现状。

#### Impact
> - 新增依赖 `matplotlib>=3.8`
> - 新增图件脚本 `scripts/generate_figures.py`、`scripts/build_mt_chart.py`
> - SKILL.md/README Workflow 增加图件步骤
> - 报告可在 chapter markdown 中插入自动生成图件并渲染入 .docx
