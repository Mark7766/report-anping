# 🧠 report-anping — Project Long-term Memory

> **Purpose**: store the project's stable facts, architectural decisions, key constraints, and common pitfalls.
> The AI agent should read this file at the start of every task to gain context.
> When the project changes significantly, update this file in sync.

---

## 📋 Project Basics

| Attribute | Value |
|------|---|
| Project name | report-anping |
| Project type | Hermes Skill |
| Business scenario | 微信对话驱动的地震安全性评价报告生成服务，基于本仓库自维护的 GB 17741 领域库 |
| User scale | 个人/小型团队 (1–10 人) |
| Current stage | v0.1.0 development |
| Design principle | 极简主义 — 无服务器、无数据库、无 LLM API；Skill = SKILL.md + 脚本 |
| Primary language | Python 3.11 |
| Backend framework | N/A |
| Database | N/A |

---

## 🏗️ Architecture Overview

```
WeChat user
    │
    ▼
Hermes Agent（用自己的 LLM 完成全部对话与生成）
    │  读 SKILL.md
    │
    ├ bash: python scripts/show_params.py            → 13 参数清单 + 章节结构
    ├ 多轮问用户 → params.json
    ├ bash: build_chapter_prompt.py --chapter N --params params.json
    │         → stdout 输出该章 prompt【不调 LLM】
    ├ Hermes 用自己的 LLM 生成 markdown → chapters/NN.md（逐章循环）
    ├ bash: generate_figures.py --params params.json --out-dir assets/generated
    │         → 生成反应谱图 / PGA 对比图（可选追加 M-T 图）
    ├ bash: render_docx.py --params … --chapters chapters/ --out exports/report.docx
    └ bash: check_compliance.py --report exports/report.docx
```

### Core Characteristics
- Hermes 主导一切 LLM 调用；Skill = SKILL.md + thin deterministic scripts
- 领域逻辑位于本仓库 `lib/`，源自 ajepro 纯函数模块，**已独立拷入本仓库自行维护，不再依赖 ajepro**
- 脚本间状态交换走 `params.json` + `chapters/*.md` 文件，无隐式耦合

---

## 🔄 Core Business Flow

```
WeChat user → Hermes 读 SKILL.md
  → bash: init_project.py --out-dir <project_dir> → 创建目录结构 + params.json 模板
  → bash: show_params.py → 多轮对话收集 → params.json
  → 逐章循环：bash: build_chapter_prompt.py → Hermes LLM 生成 → chapters/NN.md
  → bash: generate_figures.py（自动检测 data/ceic_catalog.csv；可选 --catalog 显式指定）→ assets/generated/*.png
  → bash: render_docx.py → exports/<project>.docx
  → bash: check_compliance.py → 合规报告
  → Hermes 告知用户路径
```

### 需要收集的 13 个参数（源于 ajepro projects 表）
| 字段 | 含义 | 示例 |
|------|------|------|
| name | 项目名称 | 某某医院主楼安评 |
| level | 安评级别 | I/II/III |
| location | 所在地 | 北京市朝阳区 |
| engineering_type | 工程类型 | 建筑工程/重大工程等 |
| coordinate_lat | 纬度 | 39.9042 |
| coordinate_lon | 经度 | 116.4074 |
| building_height | 建筑高度 (m) | 30 |
| construction_unit | 建设单位 | — |
| survey_unit | 勘察单位 | — |
| evaluation_unit | 评价单位 | — |
| exceedance_probs | 超越概率 | {"50_year":[10,5],"100_year":[2]} |
| boreholes | 钻孔参数 | {} 可选 |
| status | 状态 | 默认 "进行中" |

---

## 📦 Core Modules

| Module | Description | Status |
|------|------|------|
| `SKILL.md` | Hermes 总调度手册 | ✅ implemented |
| `scripts/init_project.py` | 初始化新项目工作区（目录+params.json 模板） | ✅ implemented |
| `scripts/show_params.py` | 输出 13 参数清单 + GB 17741 章节结构 | ✅ implemented |
| `scripts/build_chapter_prompt.py` | 读 params + 调用 lib/prompts 拼出某章 prompt | ✅ implemented |
| `scripts/render_docx.py` | 调用 lib/docx_builder、table_renderer、figure_renderer 渲染 .docx | ✅ implemented |
| `scripts/check_compliance.py` | 调用 lib/compliance 规则引擎 | ✅ implemented |
| `scripts/generate_figures.py` | 基于参数生成反应谱图、PGA 对比图；自动检测 data/ceic_catalog.csv 追加震目录图件 | ✅ implemented |
| `scripts/build_mt_chart.py` | 基于 CEIC 导出目录（CSV/JSON）生成 M-T 图 | ✅ implemented |
| `lib/chart_builder.py` | 图件引擎（目录解析 + 6 类图件：反应谱/PGA/M-T/震中分布/震源深度/烈度影响） | ✅ implemented |
| `lib/logger.py` | 纯 stdlib 日志，去 Flask 化 | ✅ implemented |
| `lib/gb17741_knowledge.py` | GB 17741-2025 国标知识库 | ✅ implemented |
| `lib/docx_builder.py` | Word 文档构建器 | ✅ implemented |
| `lib/table_renderer.py` | Markdown 表格 → Word 表格 | ✅ implemented |
| `lib/figure_renderer.py` | 图片渲染引擎 | ✅ implemented |
| `lib/compliance.py` | GB 17741 合规规则引擎 | ✅ implemented |
| `lib/prompts/chapter_prompts.py` | 章节 prompt 构建 | ✅ implemented |
| `lib/prompts/compliance_prompts.py` | 合规检查/修复系统提示词常量 | ✅ implemented |
| `lib/data/standards/` | GB 17741-2025 JSON 标准数据（10 个文件） | ✅ implemented |
| `params_example.json` | 13 字段参数示例（含 historical_influences） | ✅ implemented |

---

## ⚠️ Key Constraints

1. 所有文件以 `from __future__ import annotations` 开头
2. 不引入重量依赖；不硬编密钥；不用 print() 调试
3. 单函数 ≤ 50 行，单文件 ≤ 500 行，行宽 120 字符
4. **Skill frontmatter 硬限**：name ≤ 64，description ≤ 1024，SKILL.md 总长 ≤ 100,000（推荐 8–14k）
5. **SKILL.md 正文章节（Hermes 标准）**：`# <标题>` / `## Overview` / `## When to Use` / `## Parameters` / `## Workflow` / `## Common Pitfalls` / `## Verification Checklist`
6. **脚本不调 LLM**：不 import qwen_client/deepseek_client/doubao_client；Hermes 负责生成
7. **lib/ 自维护原则**：`lib/` 是本仓库的一部分，与 ajepro 完全解耦；`lib/` 内部只允许 import stdlib 和 `requirements.txt` 中列出的第三方库，**禁止** import LLM 客户端、Flask、数据库模块
8. **lib/ Python import 能工作的原因**：Hermes 运行 `python scripts/xxx.py` 时 cwd 是技能根，`from lib.xxx import` 天然可用
9. **脚本间交换**：只走 `params.json`（参数）+ `chapters/NN.md`（Hermes LLM 产出）
10. **安装路径**：`~/.hermes/skills/domain/report-anping/`（`cp -r . ~/.hermes/skills/domain/report-anping/`）
11. **图件输入约束**：CEIC 目录优先使用导出 CSV/JSON，避免在线抓取不稳定性

---

## 🐛 Known Issues & Common Pitfalls

| ID | Problem | Solution | Date |
|------|---------|---------|------|
| 1 | logger.py 拷入后 import flask 报错 | 去除 `from flask import g, has_request_context, request`，改用纯 stdlib `threading.local()` | 2026-05-05 |
| 2 | docx_builder/table_renderer 中 `from backend.utils.logger import get_logger` 路径失效 | 改为 `from lib.logger import get_logger` | 2026-05-05 |
| 3 | gb17741_knowledge.py 内 `_DATA_DIR` 指向 ajepro 的 data/ | 调整为相对本仓库 `lib/data/standards/` | 2026-05-05 |

---

## 🔧 Development Environment

### Startup
```bash
pip install -r requirements.txt
python scripts/show_params.py
# 完整流程由 Hermes 驱动；Shell 下仅可手动验证各脚本输入输出

# 图件能力验证
python scripts/generate_figures.py --params params_example.json --out-dir assets/generated
python scripts/build_mt_chart.py --catalog tests/fixtures/ceic_catalog_sample.csv --out assets/generated/mt_chart.png
```
