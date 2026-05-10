---
name: report-anping
description: >-
  WeChat 对话驱动的地震安全性评价报告生成技能。通过多轮对话收集 13 个项目参数，
  调用确定性脚本查阅 GB 17741-2025 知识库、拼接各章节生成 prompt、将 Hermes
  生成的 Markdown 章节渲染为合规 .docx 报告，最后执行合规检查并将文件路径告知用户。
  适用工程类别：核电站、大坝、高层建筑等 GB 17741-2025 规定的重大工程。
  触发词：安全性评价、安评报告、地震评价、GB 17741。
version: "1.3.0"
author: report-anping contributors
license: MIT
metadata:
  hermes:
    tags:
      - seismic
      - gb17741
      - report-generation
      - docx
      - earthquake
---

# 地震安全性评价报告生成

## Overview

本 Skill 封装了 GB 17741-2025《工程场地地震安全性评价》报告的**全生命周期生成流程**：

1. **参数收集**：通过微信多轮对话，依次向用户询问 13 个必要项目参数（项目名称、工作等级、工程类别、场地位置等），写入 `params.json`。
2. **章节生成**：对每一章调用 `build_chapter_prompt.py` 获取定制 prompt，Hermes 用自己的 LLM 生成 Markdown，保存至 `chapters/NN_chapterX.md`。
3. **图件生成**：调用 `generate_figures.py` 基于 `params.json` 生成反应谱图、PGA 对比图；若 `data/ceic_catalog.csv` 存在（CEIC 导出文件）则**自动**追加生成 M-T 图、震中分布图、震源深度分布图；若 `params.json` 含 `historical_influences` 字段则生成烈度影响条形图。
4. **文档渲染**：调用 `render_docx.py` 将全部章节 Markdown 渲染为格式规范的 Word 文档（`exports/report.docx`）。支持内联粗体/斜体、表格内图片检测；缺失图片自动插入红框占位符。
5. **合规检查**：调用 `check_compliance.py` 对照 GB 17741-2025 逐章检查，输出评分与不符合项。

脚本本身**不调用任何 LLM**；所有 LLM 调用均由 Hermes 自主完成。脚本只负责：查询标准知识库、拼接 prompt 模板、纯确定性渲染。

## When to Use

**触发本 Skill 的情况：**
- 用户明确要求生成地震安全性评价报告（关键词：安评、安全性评价、GB 17741、地震评价报告）
- 用户提供了工程项目背景并询问如何生成 .docx 报告

**不使用本 Skill 的情况：**
- 用户只是询问 GB 17741 标准内容（直接回答，无需调用脚本）
- 用户涉及的工程不属于 GB 17741-2025 适用范围（如普通住宅、道路）
- 用户需要的是地震烈度速查，而非完整报告

## Parameters

以下 13 个参数在多轮对话中逐一收集，全部收集完成后写入 `params.json`。

| # | key | 标签 | 说明 | 示例值 | 必填 |
|---|-----|------|------|--------|------|
| 1 | `name` | 项目名称 | 工程项目完整名称 | `某核电站工程地震安全性评价` | ✅ |
| 2 | `level` | 工作等级 | GB 17741-2025 安评等级：I / II / III | `II` | ✅ |
| 3 | `engineering_type` | 工程类别 | 如核电站、大坝、高层建筑、桥梁等 | `核电站` | ✅ |
| 4 | `location` | 场地地址 | 工程场地所在行政地名 | `广东省某市某县` | ✅ |
| 5 | `coordinate_lon` | 经度 | 十进制度，WGS-84 | `114.06` | ✅ |
| 6 | `coordinate_lat` | 纬度 | 十进制度，WGS-84 | `22.54` | ✅ |
| 7 | `building_height` | 建筑高度 | 主体建筑最大高度（m） | `80` | ✅ |
| 8 | `construction_unit` | 建设单位 | 工程建设方全称 | `某能源集团有限公司` | ✅ |
| 9 | `survey_unit` | 勘察单位 | 场地勘察承担单位全称 | `某地质勘察院` | ✅ |
| 10 | `evaluation_unit` | 评价单位 | 安评工作承担单位全称 | `某地震工程研究院` | ✅ |
| 11 | `exceedance_probs` | 超越概率 | 各年限各概率水准设计参数，JSON 对象 | `{"50_year":[63,10,5,2],"100_year":[10,5,2,1]}` | ✅ |
| 12 | `report_date` | 报告日期 | 报告编制年月，格式 YYYY-MM | `2025-06` | ✅ |
| 13 | `extra_notes` | 备注 | 其他特殊说明（可留空） | `""` | ❌ |

**参数收集策略：**
- 先用 `python scripts/show_params.py --level II` 获取完整清单，向用户展示
- 逐参数询问；若用户提供的值格式不符，给出示例并重新询问
- 全部必填参数确认后，将 JSON 写入 `params.json`（工作目录 = 技能根目录）

## Workflow

> 所有命令均在技能根目录（`~/.hermes/skills/domain/report-anping/`）下执行。
> 中间产物：`params.json`、`chapters/NN_chapterX.md`；最终产物：`exports/report.docx`。

### Step 0 — 首次运行：安装依赖（仅需一次）

在调用任何脚本前，先检查依赖是否已安装：

```bash
$(head -1 $(which hermes) | sed 's|#!||') -c "import docx, markdown, matplotlib" 2>/dev/null \
  || $(head -1 $(which hermes) | sed 's|#!||') -m pip install python-docx markdown matplotlib -q
```

如果命令成功（无报错），继续 Step 1。若失败，告知用户运行：
`pip install python-docx markdown matplotlib`（使用 Hermes 同版本的 Python）。

### Step 0b — 初始化项目工作区

在开始新项目前，先创建工作区目录结构和 `params.json` 模板：

```bash
python scripts/init_project.py --out-dir <project_dir>
# 例：python scripts/init_project.py --out-dir ~/reports/my_project
# 在当前目录初始化（适合已 cd 到目标目录的情况）：
# python scripts/init_project.py
```

脚本自动创建 `chapters/`、`exports/`、`data/`、`assets/generated/` 四个目录，
并写入 `params.json` 参数模板。若 `params.json` 已存在则跳过写入（传 `--force` 可强制覆盖）。

### Step 0c — 查询参数清单与章节结构

```bash
python scripts/show_params.py --level II
# 或以 JSON 格式获取，便于程序化处理
python scripts/show_params.py --level II --format json
```

输出：13 个参数说明 + 当前等级的章节列表（含章节 ID）。

### Step 1 — 多轮对话收集参数

根据 Step 0 的清单，逐一向用户询问 13 个参数。全部收集后，将以下 JSON 写入 `params.json`：

```json
{
  "name": "...",
  "level": "II",
  "engineering_type": "...",
  "location": "...",
  "coordinate_lon": "...",
  "coordinate_lat": "...",
  "building_height": 0,
  "construction_unit": "...",
  "survey_unit": "...",
  "evaluation_unit": "...",
  "exceedance_probs": {"50_year": [63, 10, 5, 2], "100_year": [10, 5, 2, 1]},
  "report_date": "YYYY-MM",
  "extra_notes": ""
}
```

### Step 2 — 逐章生成 Markdown

首先列出当前等级的全部章节 ID：

```bash
python scripts/build_chapter_prompt.py --params params.json --list-chapters
```

对每个章节（以 `preface` 为例），获取生成 prompt：

```bash
python scripts/build_chapter_prompt.py --chapter preface --params params.json
```

脚本将 prompt 输出到 stdout，Hermes 用该 prompt 调用自己的 LLM 生成章节正文 Markdown，
并将结果**保存到** `chapters/01_preface.md`（编号按章节顺序，两位补零前缀）。

对全部章节（preface → chapter1 → chapter2 → … → appendix）重复此步骤。

### Step 3 — 生成图件（推荐）

```bash
# 一键生成全部可自动生成的图件
# 若 data/ceic_catalog.csv 存在，自动追加震目录相关图件
# 若无 CEIC 数据，震中分布图自动降级为场地标记简图
# 钻孔平面图、钻孔柱状图总是自动生成
python scripts/generate_figures.py --params params.json --out-dir assets/generated

# 显式指定震目录路径（覆盖自动检测）
python scripts/generate_figures.py --params params.json --out-dir assets/generated \
  --catalog data/ceic_catalog.csv
```

**图件生成清单：**

| 图件 | 生成条件 | 说明 |
|------|---------|------|
| `response_spectrum.png` | 总是 | 设计反应谱对比图 |
| `pga_comparison.png` | 总是 | 不同超越概率 PGA 对比图 |
| `intensity_bar_chart.png` | params 含 historical_influences | 历史地震烈度影响条形图 |
| `epicenter_map.png` | 总是 | 真实 CEIC 数据或场地标记 fallback |
| `borehole_plan.png` | 总是 (v1.3.0+) | 钻孔平面位置示意图 |
| `borehole_log.png` | 总是 (v1.3.0+) | 典型钻孔柱状示意图 |
| `mt_chart.png` | CEIC 目录存在时 | 区域地震 M-T 时序图 |
| `focal_depth_distribution.png` | CEIC 目录存在时 | 震源深度分布直方图 |

在章节 Markdown 中按需插入图片引用（示例）：

```markdown
![图 2-1 震中空间分布图](assets/generated/epicenter_map.png)
![图 2-2 区域地震 M-T 图](assets/generated/mt_chart.png)
![图 2-3 震源深度分布图](assets/generated/focal_depth_distribution.png)
![图 2-4 历史地震烈度影响图](assets/generated/intensity_bar_chart.png)
![图 6-1 设计反应谱对比图](assets/generated/response_spectrum.png)
![图 6-2 不同超越概率 PGA 对比图](assets/generated/pga_comparison.png)
```

### Step 4 — 渲染 Word 文档

```bash
python scripts/render_docx.py \
  --params params.json \
  --chapters chapters/ \
  --out exports/report.docx
```

脚本将 `chapters/*.md` 按标准顺序合并，插入封面、目录，渲染表格与图片，输出 `exports/report.docx`。

### Step 5 — GB 17741-2025 合规检查

```bash
python scripts/check_compliance.py \
  --chapters chapters/ \
  --level II
```

脚本对每个章节评分（0–100）并列出不符合项。若任一章节状态为 `error`，退出码为 2。

人类可读报告（默认）；JSON 格式：`--format json`。

### Step 6 — 告知用户

检查通过后，将 `exports/report.docx` 的**绝对路径**发送给用户，并简要说明：
- 报告总章节数
- 综合合规得分
- 任何需要人工复核的章节（若有）

## Common Pitfalls

### 0. 首次安装：依赖未装到 Hermes 的 Python
- Hermes 使用自己 venv 内的 Python 执行脚本（不是系统 `python3`），需将依赖装入该环境
- **一次性操作**（Hermes 安装后执行）：
  ```bash
  # 在技能根目录下执行
  cd ~/.hermes/skills/domain/report-anping
  python3 -m pip install -r requirements.txt
  ```
  或明确指定 Hermes 的 Python：
  ```bash
  $(head -1 $(which hermes) | sed 's/#!//') -m pip install -r requirements.txt
  ```

### 1. 参数 JSON 格式错误
- `exceedance_probs` 必须是合法 JSON 对象，而非字符串
- `level` 只接受大写 `I` / `II` / `III`，不接受 `1` / `2` / `3`
- `coordinate_lon` / `coordinate_lat` 为字符串，保留两位小数

### 2. chapters/ 为空
- 若 `chapters/` 目录不存在或无 `.md` 文件，`render_docx.py` 仍会生成仅含封面和目录的 .docx，但 `check_compliance.py` 会返回空结果
- **解决**：确认 Step 2 中每个章节都已保存为 `.md` 文件

### 3. 章节文件命名
- 文件名格式应为 `NN_chapterX.md`（如 `04_chapter4.md`）
- `check_compliance.py` 通过文件名 stem 中的 `chapter\d+` / `preface` / `appendix` 关键词识别章节类型；无法识别的文件名会被跳过并输出警告

### 4. exports/ 目录权限
- `render_docx.py` 会自动创建 `exports/` 目录，但若技能安装目录权限不足会报错
- **解决**：确认 `~/.hermes/skills/domain/report-anping/` 的写权限

### 5. 工作等级不匹配
- `params.json` 中的 `level` 决定章节列表；若 `check_compliance.py` 的 `--level` 与 `params.json` 不一致，合规判定可能遗漏章节
- **最佳实践**：`check_compliance.py` 不单独指定 `--level`，从 `params.json` 读取（目前需手动保持一致）

### 6. python 版本
- 本技能需要 Python 3.11+；`python` 命令在部分系统指向 Python 2，建议显式使用 `python3`

### 7. 依赖安装要点（Debian 13 / Raspberry Pi arm64）

Debian 13 系统 Python 是 externally-managed，`pip install` 会报错。正确安装方式：

```bash
# matplotlib（系统 Python 必须用 apt）
sudo apt install python3-matplotlib -y

# python-docx（系统 Python 用 apt）
sudo apt install python3-docx -y

# Hermes venv 中也需要 python-docx + markdown（render_docx.py 用）
/home/mark/hermes-agent/.venv/bin/pip install python-docx markdown -q
```

**脚本调用规则：**
- `show_params.py`、`build_chapter_prompt.py`、`init_project.py`、`generate_figures.py`、`check_compliance.py`：用系统 `python3`
- `render_docx.py`：**必须用 Hermes venv 的 Python**（`/home/mark/hermes-agent/.venv/bin/python`）

### 8. matplotlib 中文字体（CJK 支持）

Linux 默认字体 DejaVu Sans 不含中文，`generate_figures.py` 生成的图表中文会显示为方框。修复：

```bash
sudo apt install fonts-wqy-microhei -y
rm -rf ~/.cache/matplotlib/  # 清除字体缓存
```

### 9. `which hermes` 不可用

部分环境（crontab、SSH）`which hermes` 返回空。直接使用已知路径：
- Hermes 二进制：`/home/mark/hermes-agent/.venv/bin/hermes`
- Hermes Python：`/home/mark/hermes-agent/.venv/bin/python`

### 10. 章节生成：不要用 delegate_task 批量生成

生成 11 个章节时，**禁止**用 `delegate_task` 打包多个章节给子 agent —— 每个章节 prompt 为 2–5K chars，6 个章节 = 15–30K 上下文，子 agent 会在 600s 后超时。

**正确做法**：在主会话中逐章生成，用 `build_chapter_prompt.py` 获取 prompt → 直接生成 Markdown → `write_file` 保存。每章约 1–2 分钟，全流程可控。

```bash
# 先批量获取所有章节 prompt，再逐章生成
for ch in preface chapter1 chapter2 chapter3 chapter4 chapter5 chapter7 chapter8 chapter9 chapter10 appendix; do
  python3 scripts/build_chapter_prompt.py --chapter $ch --params params.json > /tmp/prompt_$ch.txt
done
```

### 11. 合规检查误报处理

`check_compliance.py` 通过关键词匹配检查，可能对实质性内容已覆盖但未出现特定术语的章节报 error（如「项目名称」「衰减关系」等）。常见误报类型：
- 章节内容已覆盖要求但措辞不同 → 合规检查给出低分但实际质量合格
- 数值被误解析（如 `Vs20=198.5` 被当作 `20m/s` 与 500m/s 对比）
- 对于 demo 报告，这些误报属正常现象；正式项目可在章节 prompt 中显式列出 GB 17741 要求的关键词

### 12. 图片渲染：表格内图片被静默跳过（v1.3.0 修复）

章节 Markdown 中使用 `| ![...](...) |` 表格格式包裹的图片引用（常见于居中排版），在 v1.2.0 及之前会被静默跳过——渲染器先匹配表格 `|...|` 行，图片正则 `_IMG_RE.match()` 仅匹配行首，导致图片从未被检测。

**v1.3.0 修复**：
- `render_docx.py`：图片检测改用 `search()`（查找行内任意位置）+ 图片检查移到表格检查之前
- 修复后 `| ![...](...) |` 格式的图片能正常渲染

**验证方法**：渲染日志中应出现 `[PIL.PngImagePlugin] [DEBUG] STREAM` 表示图片被加载，或 `[figure_renderer] [WARNING] 图片文件不存在` 表示检测到但文件缺失。

### 13. 缺失图片的可视化占位（v1.3.0 升级）

当引用的图片文件不存在时，`figure_renderer.py` 会插入红框占位符表格（含红色加粗错误信息 + 图名 + 灰色补充提示），替代 v1.2.0 灰体斜体小字。格式：
- ⚠ 错误类型（红色加粗）
- 图名
- 灰色提示「请联系报告编制人员补充此图件」

**目的**：让报告审阅者一眼看到缺失图件，不致因无声跳过长年遗漏。

### 14. 图片可自动生成类型对照（v1.3.0）

| 图片 | 生成条件 | 自动？ |
|------|---------|--------|
| `response_spectrum.png` | params.json 含 exceedance_probs | ✅ |
| `pga_comparison.png` | params.json 含 exceedance_probs | ✅ |
| `intensity_bar_chart.png` | params.json 含 historical_influences | ✅ |
| `epicenter_map.png` | 总是（有 CEIC 用真实，无则 fallback 简图） | ✅ |
| `borehole_plan.png` | 总是（参数生成示意布局） | ✅ |
| `borehole_log.png` | 总是（典型地层剖面） | ✅ |
| `mt_chart.png` | data/ceic_catalog.csv 存在 | ✅ |
| `focal_depth_distribution.png` | data/ceic_catalog.csv 存在 | ✅ |
| 断层分布图 / 构造图 | 依赖空间 GIS 数据 | ❌ 需手动 |

**建议**：LLM 生成章节时，对 ❌ 类图片使用 `[此处需插入：图X-X 示意图]` 占位文本而非 `![...](assets/...)` 引用，避免渲染出缺失占位。

Hermes 完成 Step 3–4 后，依次验证以下条目后再告知用户：

- [ ] `exports/report.docx` 存在且文件大小 > 0 字节
- [ ] `check_compliance.py` 退出码为 0（无 `error` 级章节）
- [ ] 合规输出中每章评分 ≥ 60（低于 60 需提示用户人工审核）
- [ ] 报告文件名包含项目名称或日期，避免覆盖历史版本（可重命名 `exports/report_YYYYMMDD.docx`）
- [ ] 向用户发送的路径是**绝对路径**（`~` 展开后的完整路径）
