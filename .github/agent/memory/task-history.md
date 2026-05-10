# 📜 report-anping — Task History

> **Purpose**: record summaries of recent tasks to give the AI agent short-term context.
> Keep the most recent 30 tasks; archive older entries.

---

## Record Format

```markdown
### [TASK-{number}] {task-title}
- **Date**: YYYY-MM-DD
- **Type**: feat / fix / refactor / docs / chore
- **Summary**: one sentence about what was done
- **Changed files**: list the core changed files
- **Related issue**: #xxx (if any)
- **Notes**: things to watch out for later (if any)
```

---

## Task Records

### [TASK-017] 修复图片未渲染进 docx 的 Bug + SKILL.md 结构问题
- **Date**: 2026-05-09
- **Type**: fix
- **Summary**: 根因：`render_docx.py` 中 `MarkdownToDocxRenderer` 将章节 MD 内的相对图片路径（如 `assets/generated/xxx.png`）相对于 CWD（Hermes 技能根）解析，而实际图片在用户项目目录下，导致所有图片显示"图片未找到"；修复方法：传入 `base_dir = chapters_dir.resolve().parent`，非绝对路径先 join base_dir 再传给 figure_renderer。同时修复 SKILL.md 的重复 Step 0 标题（第二个有前置空格，被 Hermes 解析为两个独立步骤）并统一编号为 Step 0 / Step 0b / Step 0c。
- **Changed files**:
  - `scripts/render_docx.py`（MarkdownToDocxRenderer 增加 base_dir 参数，render() 传入 chapters_dir.resolve().parent）
  - `SKILL.md`（Step 0 标题去重；Step 0b→Step 0b 改初始化工作区；原 Step 0b→Step 0c 查询参数清单）

### [TASK-016] 代码质量审查与修复 — 补充 future annotations 及缺失 docstring
- **Date**: 2026-05-09
- **Type**: style
- **Summary**: 全面审查 lib/ + scripts/ + tests/ 代码质量：ruff lint/format 均通过；发现 5 个 lib 文件缺少 `from __future__ import annotations`（AGENTS.md 强制要求），3 个 `__init__` 方法缺少 docstring；逐一修复，161 条测试全绿，无其他问题。
- **Changed files**:
  - `lib/compliance.py`、`lib/docx_builder.py`、`lib/figure_renderer.py`、`lib/gb17741_knowledge.py`、`lib/table_renderer.py`（添加 future annotations + `__init__` docstring）
- **Notes**: 仍有多个函数超 50 行（chart_builder/compliance/docx_builder 中），属已有代码，不在本次范围内。type annotations 在 lib/ 各文件中仍不完整，属历史遗留，后续可按文件逐步补充。

### [TASK-015] 为纯 Python 渲染器辅助类新增 60 条单元测试，覆盖率 77%→79%
- **Date**: 2025-05-09
- **Type**: test
- **Summary**: 新建 `tests/test_renderers.py`（53 条）覆盖 `MarkdownTableParser`、`TableNumbering`（`lib/table_renderer.py`）、`FigureNumbering`、`ChapterNumberingTracker`（`lib/figure_renderer.py`）所有纯 Python 方法及无效章节号保护路径；在 `tests/test_scripts.py` 新增 8 条测试覆盖 `get_clause`、`get_appendix_b`、`get_full_standard_guidance_for_ai`（formula 分支）以及 `generate_figures_manifest` 的坐标回退（TypeError/ValueError 路径）和 `_DEFAULT_CATALOG` 自动检测路径；测试总数 101→161，全绿，覆盖率 77%→79%。
- **Changed files**:
  - `tests/test_renderers.py`（新建：53 条）
  - `tests/test_scripts.py`（修改：新增 TestGb17741KnowledgeExtra + TestGenerateFiguresExtra 共 8 条）

### [TASK-014] 新增 init_project.py、填补测试覆盖、修正 project-memory.md 状态
- **Date**: 2026-05-09
- **Type**: feat + test + chore
- **Summary**: 新增工作区初始化脚本 `scripts/init_project.py`（创建 4 个标准子目录 + params.json 模板，幂等，支持 --force）；新增 24 条测试（TestInitProject/TestBuildMtChartCLI/TestCompliancePrompts/TestChapterPromptsAdditional），测试总数 77→101，全绿；覆盖率 71%→77%（compliance_prompts 0%→96%，chapter_prompts 68%→98%，gb17741 61%→79%）；修正 project-memory.md 中所有 ⬜ planned 状态、补充 init_project 入架构图；SKILL.md 新增 Step 0（init_project）。
- **Changed files**:
  - `scripts/init_project.py`（新建：工作区初始化脚本）
  - `tests/test_scripts.py`（修改：新增 24 条测试）
  - `SKILL.md`（修改：新增 Step 0 说明 init_project.py）
  - `.github/agent/memory/project-memory.md`（修改：状态表全部改为 ✅ implemented，架构图补 init_project）
- **Notes**: CLI main() 经 subprocess 调用的脚本（build_mt_chart.py、build_chapter_prompt.py）在 pytest-cov 下仍显示 0%/35%，属正常现象（subprocess 独立进程不计入父进程覆盖率）。

### [TASK-013] 图件扩展：震中分布图、震源深度图、烈度影响图；CEIC 目录自动检测
- **Date**: 2026-05-08
- **Type**: feat + test
- **Summary**: 新增三类专业地震图件（震中空间分布图、震源深度分布图、历史地震烈度影响条形图）；`generate_figures.py` 支持自动检测 `data/ceic_catalog.csv`（无需 --catalog 参数）；目录记录增加深度字段解析；params_example.json 补充 `historical_influences` 示例；新增 5 条测试，总测试数 77 全绿；推送 commit c9eeba8。
- **Changed files**:
  - `lib/chart_builder.py`（修改：新增 generate_epicenter_map / generate_focal_depth_distribution / generate_intensity_bar_chart；load_catalog_records 增加 depth 字段；增加 CJK 字体自动检测配置）
  - `scripts/generate_figures.py`（修改：自动检测 data/ceic_catalog.csv；调用新图件函数；传递坐标与历史地震参数）
  - `tests/fixtures/ceic_catalog_sample.csv`（修改：增加 depth 列）
  - `params_example.json`（修改：新增 historical_influences 字段示例）
  - `.gitignore`（修改：排除 /data/ceic_catalog.csv）
  - `SKILL.md`（修改：更新 Step 3 说明自动检测规则与全部 6 类图件）
  - `tests/test_scripts.py`（修改：新增 5 条图件测试）
- **Notes**: CJK 字体警告（DejaVu Sans 缺少汉字）在无 SimHei 等字体的环境下属正常现象，图片仍可正常生成，仅标签显示为方框。

### [TASK-012] 专业化增强：图件生成与 CEIC 目录 M-T 能力
- **Date**: 2026-05-08
- **Type**: feat + docs + test
- **Summary**: 基于旧国标安评报告样式完成技能增强：新增数据驱动图件生成能力（反应谱、PGA 对比）与 CEIC 目录驱动 M-T 图生成能力；升级章节 prompt 的专业表达与图件嵌入规范；改进 render_docx 正文段落格式（两端对齐、1.5 倍行距、首行缩进）；补充 SKILL/README 工作流与命令说明；新增集成测试，测试总数 72 全绿。
- **Changed files**:
  - `lib/chart_builder.py`（新建：目录解析、M-T 图、反应谱图、PGA 对比图）
  - `scripts/generate_figures.py`（新建：一键生成图件清单）
  - `scripts/build_mt_chart.py`（新建：CEIC 目录导出生成 M-T 图）
  - `scripts/render_docx.py`（修改：正文段落格式专业化）
  - `lib/prompts/chapter_prompts.py`（修改：增强专业写作与图片引用要求）
  - `requirements.txt`（修改：新增 `matplotlib>=3.8`）
  - `tests/fixtures/ceic_catalog_sample.csv`（新建）
  - `tests/test_scripts.py`（修改：新增图件脚本测试）
  - `SKILL.md`（修改：新增图件生成步骤与 CEIC M-T 工作流）
  - `README.md`（修改：新增图件能力说明与命令示例）
- **Notes**: 当前 CEIC 站点抓取受页面结构/反爬影响，脚本采用“先导出目录 CSV/JSON 再生成图件”的稳态方案；后续若 CEIC 提供稳定 API，可再加在线拉取模式。

### [TASK-011] Phase 4.5 — Hermes Skill 实装验证
- **Date**: 2026-05-06
- **Type**: fix + docs
- **Summary**: 将 report-anping 安装到 `~/.hermes/skills/domain/report-anping/`；`hermes skills list` 确认 status=enabled。发现 Hermes 使用自己 venv 的 Python（`hermes-agent/venv/bin/python3 3.11.15`），而非系统 python3，导致 `python-docx` 缺失。将依赖安装到 Hermes venv 后，全链路 4 脚本均通过（show_params → build_chapter_prompt → render_docx 产出 41,899-byte .docx → check_compliance）。更新 SKILL.md Common Pitfalls 章节补充首次安装说明。
- **Changed files**:
  - `SKILL.md`（修改：Common Pitfalls 新增 Pitfall 0 — 首次安装依赖）
- **Notes**: Hermes Python 路径可通过 `head -1 $(which hermes) | sed 's/#!//'` 获取。后续若要简化安装体验，可考虑在 SKILL.md Workflow 最前面加 Bootstrap 步骤让 Hermes 自动执行 `pip install -r requirements.txt`。

---

### [TASK-010] Phase 4 — 集成验证与收尾
- **Date**: 2026-05-06
- **Type**: feat + fix
- **Summary**: 端到端验证（show_params→build_chapter_prompt→render_docx→check_compliance 全链路跑通，产出 41,899-byte .docx）；修复 ruff 发现的 16 处真实代码缺陷（F401 unused imports、F841 unused vars、F541 bare f-strings、W293 trailing whitespace、E501 long line）；新增 ruff.toml（line-length=120，ignore E402）；更新 CI（lint/coverage 覆盖 lib/，SKILL.md frontmatter 用 pyyaml 验证）；编写 README.md。
- **Changed files**:
  - `ruff.toml`（新建：lint 配置，line-length=120，ignore E402）
  - `README.md`（新建：快速上手、目录结构、数据流、开发命令）
  - `.github/workflows/ci.yml`（修改：lint/coverage 加入 lib/；SKILL.md frontmatter 改用 pyyaml 验证；test job 安装 pyyaml）
  - `lib/compliance.py`（修复：移除 CHAPTER_STANDARD_MAPPING、STANDARD_INFO、get_all_terms 未用导入及 terms 变量）
  - `lib/figure_renderer.py`（修复：移除 caption_position 未用变量）
  - `lib/logger.py`（修复：移除 functools.wraps 未用导入）
  - `lib/prompts/chapter_prompts.py`（修复：移除多余 f 前缀；折行长行）
  - `lib/prompts/compliance_prompts.py`（修复：移除多余 f 前缀）
  - `lib/gb17741_knowledge.py`（修复：docstring 中的 trailing whitespace）
  - `scripts/render_docx.py`（修复：移除 logging 未用导入）
  - `tests/test_gb17741_knowledge.py`（修复：移除 6 个未用导入）
  - `tests/test_logger.py`（修复：移除 logging 未用导入）
  - `tests/test_scripts.py`（修复：移除 pytest 未用导入）
  - 全部 lib/ scripts/ tests/ 文件经 `ruff format` 格式化
- **Notes**: 70 条测试全部通过。ruff check + format --check 全绿。Phase 4.5（Hermes skill 实装验证）为手动步骤，需用户在实际 Hermes 环境中执行 `cp -r . ~/.hermes/skills/domain/report-anping/`。

---

### [TASK-009] Phase 3 — SKILL.md 编写
- **Date**: 2026-05-06
- **Type**: feat
- **Summary**: 按 Hermes 标准格式编写 `SKILL.md`（7 个章节：frontmatter、Overview、When to Use、Parameters、Workflow、Common Pitfalls、Verification Checklist）。验证：前3字节 `---`，文件 8474 bytes < 100000，description 219 chars < 1024，YAML 解析成功。
- **Changed files**:
  - `SKILL.md`（新建：Hermes Skill 总调度手册，描述参数收集→章节生成→docx 渲染→合规检查完整流程）
- **Notes**: description 字段使用 YAML block scalar（`>-`）合法折行；5 个 Common Pitfalls 涵盖参数格式、章节命名、目录权限、等级不匹配、Python 版本等常见问题。Phase 4 下一步：端到端集成验证 + README.md。

---

### [TASK-008] Phase 2 — scripts/ CLI 入口
- **Date**: 2026-05-06
- **Type**: feat
- **Summary**: 实现 4 个 CLI 脚本：show_params（参数清单输出）、build_chapter_prompt（prompt 拼接，不调 LLM）、render_docx（Markdown→.docx 渲染）、check_compliance（GB 17741-2025 合规检查）；新增集成测试 20 条，全部通过（70 条测试全绿）。
- **Changed files**:
  - `scripts/show_params.py`（新建：PARAM_SPEC 13 字段、human/json 双格式输出）
  - `scripts/build_chapter_prompt.py`（新建：--chapter/--params/--list-chapters，stdout 输出 prompt）
  - `scripts/render_docx.py`（新建：MarkdownToDocxRenderer 解析 MD，调用 DocxBuilder/TableRenderer/FigureRenderer）
  - `scripts/check_compliance.py`（新建：逐章检查，human/json 双格式，error 状态退出码 2）
  - `tests/test_scripts.py`（新建：20 条集成测试）
  - `tests/fixtures/chapters/`（新建 3 个 fixture .md 文件）
- **Notes**: render_docx 支持 `#/##/###/####` 标题、段落、Markdown 表格、图片引用；章节排序按 CHAPTER_ORDER 列表而非文件名字母序。check_compliance 通过文件名 stem 正则提取 chapter_key，无法识别时跳过并 warning。Phase 3 下一步：编写 SKILL.md。

---

### [TASK-007] Phase 1 — lib/ 领域库迁移与清理
- **Date**: 2026-05-05
- **Type**: feat
- **Summary**: 将 ajepro 的纯函数模块全部拷入 `lib/`，修复所有 import 路径，去除 Flask 依赖，50 条单元测试全部通过。
- **Changed files**:
  - `lib/__init__.py`（新建）
  - `lib/logger.py`（从 ajepro 迁移，去除 Flask import，`get_request_id()` 改为纯 `threading.local()`）
  - `lib/gb17741_knowledge.py`（从 ajepro 迁移，`_DATA_DIR` 由 `../data/standards` 改为 `data/standards`）
  - `lib/docx_builder.py`（从 ajepro 迁移，logger import 修复）
  - `lib/table_renderer.py`（从 ajepro 迁移，logger import 修复，删除 render() 内重复 import）
  - `lib/figure_renderer.py`（从 ajepro 迁移，logger import 修复）
  - `lib/prompts/__init__.py`（新建）
  - `lib/prompts/chapter_prompts.py`（从 ajepro 迁移，gb17741_knowledge import 修复）
  - `lib/prompts/compliance_prompts.py`（从 ajepro 迁移，所有 backend.* import 修复）
  - `lib/compliance.py`（从 compliance_service.py 迁移，两处 import 修复）
  - `lib/data/standards/*.json`（10 个 GB 17741-2025 JSON 数据文件，cp 复制）
  - `requirements.txt`（新建：python-docx>=1.1.0, markdown>=3.5）
  - `params_example.json`（新建：13 字段安评参数示例）
  - `tests/test_logger.py`（新建，11 个测试）
  - `tests/test_gb17741_knowledge.py`（新建，27 个测试）
  - `tests/test_compliance.py`（新建，12 个测试）
- **Notes**: 全部 50 条测试通过（Python 3.13.2，pytest 9.0.3）。Phase 2 下一步：创建 scripts/ CLI（show_params.py、build_chapter_prompt.py、render_docx.py、check_compliance.py）。

---

### [TASK-006] 设计文档对齐 Hermes Skill 标准目录结构
- **Date**: 2026-05-05
- **Type**: chore
- **Summary**: 用户向 Hermes 核实标准 Skill 结构，发现文档有三处偏差：(1) SKILL.md 正文章节与 Hermes 标准不符；(2) 目录结构缺少 `references/`、未注明 `lib/`/`tests/` 为非标准目录；(3) AGENTS.md Conventions 含 FastAPI 残留条目。全部修正。
- **Changed files**:
  - `AGENTS.md`（Conventions：SKILL.md 正文结构改为 Hermes 标准 7 章节；删除"Async-first/Test database/Configuration"残留；lib/ 自维护说明保留）
  - `.github/copilot-instructions.md`（Directory Layout 新增根目录说明注释、`references/`、各目录 Hermes 标准/非标注记）
  - `.github/agent/memory/project-memory.md`（约束 5 新增 SKILL.md 正文章节列表；约束 8 新增 lib/ import 原理；约束 9/10 原 7/8 重新编号）
  - `.github/agent/memory/task-history.md`
- **Notes**: Hermes 四大标准子目录：`scripts/`、`references/`、`templates/`、`assets/`；`lib/` 不在其中但 cp-r 部署时完全可用，原因是 Hermes 运行 `python scripts/xxx.py` 时 cwd 是技能根目录，`from lib.xxx import` 自然可解析。

---

### [TASK-005] 设计文档更新 — ajepro 代码拷贝入本仓库自维护
- **Date**: 2026-05-05
- **Type**: chore
- **Summary**: 用户明确 ajepro 将不再维护，要求把所需纯函数模块拷贝进本仓库 `lib/` 自行维护，彻底切断对 ajepro 的依赖。更新全部设计文档以反映此决策。
- **Changed files**:
  - `AGENTS.md`（Project Overview、架构模块描述、Conventions 去"ajepro 复用方式"改"lib/ 自维护"、Important Constraints 填补占位符）
  - `.github/copilot-instructions.md`（Tech Stack 表去"ajepro 复用"行改"领域库 lib/"；Directory Layout 改为含 `lib/` 完整结构）
  - `.github/agent/memory/project-memory.md`（业务描述、架构特征、模块表扩展为 13 行、约束条款 6 改为"lib/ 自维护"、Pitfalls 更新为迁移注意事项）
  - `.github/agent/memory/decisions-log.md`（ADR-002 标 Deprecated；ADR-005 Impact 更正；新增 ADR-006）
  - `.github/agent/memory/task-history.md`
- **Notes**: 关键迁移要点：(1) logger.py 去 Flask 依赖；(2) 所有 `from backend.xxx` 改 `from lib.xxx`；(3) `_DATA_DIR` 指向 `lib/data/standards/`；(4) 10 个 JSON 数据文件一并拷入。

---

### [TASK-004] 架构再修正 — Hermes 编排多脚本模型
- **Date**: 2026-05-05
- **Type**: chore
- **Summary**: 用户指出 ADR-004 让 ajepro 作为独立 Flask 服务运行没有充分利用 Hermes Agent 的编排能力。改为：Hermes 直接基于 SKILL.md 调用 4 个无状态脚本（show_params / build_chapter_prompt / render_docx / check_compliance），脚本只 import ajepro 的纯函数模块（prompts/docx_builder/gb17741_knowledge/table_renderer/figure_renderer），**不调 LLM**，全部 LLM 生成由 Hermes 完成；脚本间用 params.json + chapters/*.md 交换状态。
- **Changed files**:
  - `AGENTS.md`（架构图、Common Commands、Conventions 全面改写）
  - `.github/copilot-instructions.md`（技术栈表移除 requests/responses，改为 ajepro 纯函数 import；目录结构改为 4 个脚本 + chapters/ + exports/）
  - `.github/agent/memory/project-memory.md`（架构图、模块表、约束、pitfalls、startup 全部重写）
  - `.github/agent/memory/decisions-log.md`（ADR-004 标 Deprecated；新增 ADR-005）
  - `.github/agent/memory/task-history.md`
- **Notes**: 关键洞察 — ajepro 含一批可独立 import 的纯函数模块；Hermes 是 LLM 编排引擎，让 Skill 自己实现 LLM 调用是反模式。脚本必须避免 import `backend.routes.*`、`task_manager`、`*_client.py`、`backend.utils.database`。

---

### [TASK-003] 设计 review — ajepro 集成方式与 Skill 约束细化
- **Date**: 2026-05-05
- **Type**: chore
- **Summary**: 阅读 ajepro 全部源码（routes/services/models）确认其为 Flask Web 服务无 CLI；阅读 hermes-agent skill 范例确认 Skill 的真实约束。修正集成方式为 HTTP REST 客户端，补全 13 个项目参数表、Skill frontmatter 硬限制、安装路径、健康检查脚本。
- **Changed files**:
  - `AGENTS.md` (架构图改为 HTTP 集成 + 列出 4 个 REST 端点)
  - `.github/copilot-instructions.md` (技术栈加 requests + responses，目录结构含 ajepro_client/check_ajepro)
  - `.github/agent/memory/project-memory.md` (架构图、13 参数表、Skill frontmatter 硬限制、健康检查 pitfall、env vars)
  - `.github/agent/memory/decisions-log.md` (新增 ADR-004 ajepro HTTP 集成)
  - `.github/agent/memory/task-history.md`
  - `.github/workflows/ci.yml` (移除 mypy/uv，改为 pip + ruff + pytest，新增 SKILL.md frontmatter 校验)
  - `.github/workflows/memory-check.yml` (监控路径改为 SKILL.md/scripts/**)
- **Notes**: 关键洞察 — ajepro 是 Flask Web app 不是 CLI，直接复用必须走 HTTP；同时 Hermes Skill 的 SKILL.md 有硬约束（name ≤64, description ≤1024, total ≤100k chars）。

---

### [TASK-002] 架构纠正 — Hermes Skill 无服务器模型
- **Date**: 2026-05-05
- **Type**: chore
- **Summary**: 用户指出 TASK-001 中错误地将 Skill 设计为独立 FastAPI 服务（含数据库和 LLM 调用）；阅读 hermes-agent 源码后确认 Skill 正确模型为 SKILL.md + helper scripts，Hermes LLM 负责全部对话与 LLM 调用。修正全套配置文件。
- **Changed files**:
  - `AGENTS.md`
  - `.github/copilot-instructions.md`
  - `.github/project-metadata.yml`
  - `.github/agent/memory/project-memory.md`
  - `.github/agent/memory/decisions-log.md` (ADR-001 废弃，新增 ADR-003)
  - `.github/agent/memory/task-history.md`
- **Notes**: 核心教训 — 初始化前应先读懂目标平台（hermes-agent/skills/）的真实 Skill 结构，再填写技术栈，避免错误方向。

---

### [TASK-001] 项目初始化 — 定制化所有 {{...}} 占位符文件
- **Date**: 2026-05-05
- **Type**: chore
- **Summary**: 基于用户一句话说明，自动推断并完成 13 个模板文件的定制化：项目名称、技术栈、目录结构、核心流程、ADR、CI 流水线等全部填充完毕。
- **Changed files**:
  - `AGENTS.md`
  - `.github/copilot-instructions.md`
  - `.github/project-metadata.yml`
  - `.github/PULL_REQUEST_TEMPLATE.md` (无占位符，无需修改)
  - `.github/ISSUE_TEMPLATE/config.yml`
  - `.github/workflows/ci.yml`
  - `.github/workflows/memory-check.yml` (无项目内占位符，路径已匹配)
  - `.github/agent/system-prompt.md`
  - `.github/agent/coding-standards.md`
  - `.github/agent/workflows.md`
  - `.github/agent/prompt-templates.md`
  - `.github/agent/memory/project-memory.md`
  - `.github/agent/memory/decisions-log.md`
  - `.github/agent/memory/task-history.md`
- **Related issue**: N/A
- **Notes**: 技术栈决策 FastAPI + SQLite + uv + ruff 记录在 ADR-001。LLM prompt 复用策略记录在 ADR-002。后续需要创建实际源码目录结构（src/、tests/、pyproject.toml、.env.example）。
