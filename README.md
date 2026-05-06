# report-anping

> **Hermes Skill** — WeChat 对话驱动的地震安全性评价报告生成服务。
> 通过多轮对话收集项目参数，自动生成符合 **GB 17741-2025** 的 `.docx` 报告。

---

## 功能概述

| 能力 | 说明 |
|------|------|
| 参数收集 | 多轮对话依次询问 13 个必要参数，保存为 `params.json` |
| 章节生成 | 为每章输出定制 prompt，Hermes LLM 生成符合国标的 Markdown 正文 |
| 文档渲染 | Markdown + 参数 → 格式规范的 `.docx`（含封面、目录、表格、图片）|
| 合规检查 | 逐章对照 GB 17741-2025 评分，输出不符合项与改进建议 |

---

## 快速上手

### 1. 环境准备

```bash
python3 --version   # 需要 3.11+
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 查看参数清单

```bash
python scripts/show_params.py --level II
```

### 3. 拼接章节 prompt（不调 LLM）

```bash
# 列出当前等级全部章节 ID
python scripts/build_chapter_prompt.py --params params_example.json --list-chapters

# 获取某章节的生成 prompt（stdout 输出，供 Hermes 使用）
python scripts/build_chapter_prompt.py --chapter chapter4 --params params_example.json
```

### 4. 渲染 Word 文档

```bash
python scripts/render_docx.py \
  --params params_example.json \
  --chapters tests/fixtures/chapters/ \
  --out /tmp/demo.docx
```

### 5. 合规检查

```bash
python scripts/check_compliance.py \
  --chapters tests/fixtures/chapters/ \
  --level II
# 退出码 0 = 全部通过；2 = 存在 error 级章节
```

### 6. 运行测试

```bash
pip install pytest pytest-cov
pytest tests/ -v
```

---

## 安装为 Hermes Skill

> **推荐方式：git clone** — 零依赖、支持 `git pull` 一键更新。
> `hermes skills install` 的 GitHub 标识符格式要求 SKILL.md 在子目录下，
> 而 git clone 可直接将整个仓库克隆到 Hermes skill 目录，开箱即用。

### 前提条件

1. 确认 Python 版本 ≥ 3.11：`python3 --version`
2. 将本仓库推送到 GitHub（若尚未推送）
3. Hermes Agent 已安装：`hermes --version`

---

### 方式一：微信一句话安装（推荐）

在微信中向 Hermes 发送以下消息：

```
帮我安装地震安评技能，执行以下两条命令：
1. cd ~/.hermes/skills/domain && git clone https://github.com/Mark7766/report-anping.git
2. $(head -1 $(which hermes) | sed 's|#!||') -m pip install python-docx markdown -q
```

Hermes 执行完毕后，**重启 Hermes session**，之后直接说「我要生成地震安评报告」即可触发本技能。

---

### 方式二：命令行安装

```bash
# Step 1 — 克隆到 Hermes skill 目录
cd ~/.hermes/skills/domain
git clone https://github.com/Mark7766/report-anping.git

# Step 2 — 安装 Python 依赖到 Hermes 的 Python 环境
# （Hermes 使用自己 venv 内的 Python，需明确安装）
$(head -1 $(which hermes) | sed 's|#!||') -m pip install python-docx markdown -q

# Step 3 — 验证安装
hermes skills list | grep report-anping
# 预期输出: report-anping | domain | local | local | enabled
```

---

### 更新技能

```bash
cd ~/.hermes/skills/domain/report-anping
git pull
# 无需重新安装依赖（requirements.txt 只含 python-docx 和 markdown）
```

---

### 触发词

Hermes 加载后，以下任意短语均可触发本技能：

- 「帮我生成地震安评报告」
- 「安评报告生成」
- 「GB 17741 报告」
- 「地震安全性评价」

---

### 卸载

```bash
rm -rf ~/.hermes/skills/domain/report-anping
```

---

## 目录结构

```
report-anping/
├── SKILL.md                    Hermes 总调度手册（触发词、参数说明、Workflow）
├── scripts/
│   ├── show_params.py          输出 13 个参数清单 + 章节结构
│   ├── build_chapter_prompt.py 输出某章节的生成 prompt（不调 LLM）
│   ├── render_docx.py          渲染 chapters/*.md → .docx
│   └── check_compliance.py     GB 17741-2025 合规检查
├── lib/                        本仓库自维护领域库
│   ├── gb17741_knowledge.py    GB 17741-2025 知识库（常量 + JSON 数据查询）
│   ├── docx_builder.py         Word 文档辅助（目录、页眉页脚、样式）
│   ├── table_renderer.py       Markdown 表格 → Word 表格
│   ├── figure_renderer.py      图片 → Word 图文块（自动编号）
│   ├── compliance.py           合规规则引擎（纯函数，无 DB）
│   ├── logger.py               统一日志（纯 stdlib，无 Flask）
│   ├── prompts/
│   │   ├── chapter_prompts.py  章节 prompt 构建
│   │   └── compliance_prompts.py 合规相关 prompt
│   └── data/standards/         GB 17741-2025 JSON 标准数据（10 文件）
├── tests/                      单元 + 集成测试（70 条）
│   └── fixtures/chapters/      3 个示例章节 .md 文件
├── params_example.json         13 字段参数示例
├── requirements.txt            python-docx>=1.1.0, markdown>=3.5
└── ruff.toml                   Lint 配置（行宽 120，忽略 E402）
```

---

## 数据流

```
微信用户
  │
  ▼
Hermes Agent（用自己的 LLM 完成所有对话与章节生成）
  │  读 SKILL.md 获得领域知识与脚本调用顺序
  │
  ├─► python scripts/show_params.py
  │       → 输出 13 参数清单 + 章节结构
  │   Hermes 多轮问用户 → 写入 params.json
  │
  ├─► python scripts/build_chapter_prompt.py --chapter N --params params.json
  │       → stdout 输出该章 prompt（不调 LLM）
  │   Hermes 用自己的 LLM 生成 Markdown → chapters/NN.md
  │   对全部章节循环
  │
  ├─► python scripts/render_docx.py --params params.json --chapters chapters/ --out exports/report.docx
  │       → 纯确定性渲染
  │
  └─► python scripts/check_compliance.py --chapters chapters/ --level II
          → GB 17741-2025 逐章合规检查，输出评分与不符合项
```

---

## 约束与限制

- **Python 3.11+**；依赖极少（`python-docx`、`markdown`）
- **脚本不调 LLM**；所有 LLM 调用由 Hermes 自主完成
- **无数据库**；状态通过 `params.json` + `chapters/*.md` 文件交换
- **无密钥**；若需签名 URL 等凭证，通过环境变量注入
- `lib/` 源自 ajepro 纯函数模块，已独立维护，与 ajepro 完全解耦

---

## 开发

```bash
# Lint
ruff check lib scripts tests

# Format check
ruff format --check lib scripts tests

# Tests with coverage
pytest tests/ --cov=lib --cov=scripts -v
```

---

## License

MIT
