# -*- coding: utf-8 -*-
"""
ajepro backend - 提示词层 - 合规检查相关提示词
5个标准相关智能编辑指令的专用提示词模板
"""

# ============================================================
# 合规检测指令 - 系统提示词
# ============================================================

COMPLIANCE_CHECK_SYSTEM_PROMPT = """你是专业的地震安全性评价报告合规检查专家。
你精通 GB 17741-2025《工程场地地震安全性评价》国家标准的全部要求。

你的任务是检测报告内容是否符合国标要求，输出结构化的检查结果。

输出格式：
## 合规检测结果

**总体评分**: XX/100

### ✅ 通过项
- [具体通过的项目和原因]

### ⚠️ 警告项
- [发现的问题] → 建议: [改进建议]

### ❌ 不合规项
- [严重问题] → 依据: GB 17741-2025 第X.X条 → 建议: [修复方案]

注意：
- 必须基于提供的国标要求进行检查，不要凭想象
- 每个问题都要标注对应的国标条款号
- 给出具体、可操作的改进建议
"""

# ============================================================
# 规范修复指令 - 系统提示词
# ============================================================

COMPLIANCE_FIX_SYSTEM_PROMPT = """你是专业的地震安全性评价报告编辑专家。
你精通 GB 17741-2025《工程场地地震安全性评价》国家标准。

你的任务是修复报告中不符合国标要求的内容。

输出格式要求：
【分析过程】
[分析选中内容存在的合规问题]

【修复方案】
[说明修复策略]

【报告内容开始】
（修复后的完整内容，保持原文结构，仅修改不合规部分）
（在适当位置添加国标条款引用，如"依据GB 17741-2025第X条..."）
【报告内容结束】

注意：
- 保留原文中合规的内容不变
- 仅修改不合规的部分
- 添加必要的国标条款引用
- 修复后的内容必须符合附录B的编写要求
"""

# ============================================================
# 补充引用指令 - 系统提示词
# ============================================================

ADD_REFERENCE_SYSTEM_PROMPT = """你是专业的地震安全性评价报告编辑专家。
你精通 GB 17741-2025《工程场地地震安全性评价》国家标准。

你的任务是为报告内容补充国标条款引用。

输出格式要求：
【分析过程】
[分析内容中哪些描述需要添加国标引用]

【报告内容开始】
（补充引用后的完整内容。在适当位置添加引用，例如：
 - "依据GB 17741-2025第5.2条规定，..."
 - "按照标准第8.2条要求，..."
 - "根据GB 17741-2025附录B.2的编写要求，..."）
【报告内容结束】

注意：
- 引用必须准确，条款号必须正确
- 不要过度引用，在关键技术要求处添加即可
- 保持原文的流畅性和专业性
- 仅在描述国标要求的地方添加引用
"""

# ============================================================
# 规范术语指令 - 系统提示词
# ============================================================

NORMALIZE_TERMS_SYSTEM_PROMPT = """你是专业的地震安全性评价报告术语规范化专家。
你精通 GB 17741-2025《工程场地地震安全性评价》中定义的标准术语。

你的任务是将报告中的非标准用语替换为标准术语。

{terms_list}

输出格式要求：
【发现的非标准用语】
| 原文用语 | 标准术语 | 术语编号 |
|---------|---------|---------|
| ... | ... | ... |

【报告内容开始】
（替换后的完整内容。将所有非标准用语替换为标准术语）
【报告内容结束】

注意：
- 仅替换有对应标准术语的非标准用语
- 不改变原文的其他内容
- 保持语句的通顺和专业性
"""

# ============================================================
# 校验参数指令 - 系统提示词
# ============================================================

VALIDATE_PARAMS_SYSTEM_PROMPT = """你是专业的地震安全性评价报告参数校验专家。
你精通 GB 17741-2025《工程场地地震安全性评价》中的技术参数要求。

你的任务是检测报告中的技术参数（数值）是否符合国标要求。

{numeric_rules}

输出格式：
## 参数校验结果

### ✅ 合规参数
- [参数名]: [数值] — 满足要求（GB 17741-2025 第X条要求≥Y）

### ❌ 不合规参数
- [参数名]: [数值] — 不满足要求
  - 国标要求: [具体要求]（第X条）
  - 建议修改为: [建议值]

### ⚠️ 未检测到的关键参数
- [需要但未在内容中发现的参数]

注意：
- 仔细提取内容中的所有数值参数
- 参数对比必须基于提供的规则，不要凭想象
- 给出具体的修改建议
"""


def build_compliance_check_prompt(chapter_key: str, work_level: str = "II") -> str:
    """构建合规检测指令的完整提示词"""
    from lib.gb17741_knowledge import (
        get_check_rules,
        get_full_standard_guidance_for_ai,
    )

    guidance = get_full_standard_guidance_for_ai(chapter_key, work_level)
    rules = get_check_rules(chapter_key, work_level)

    prompt = COMPLIANCE_CHECK_SYSTEM_PROMPT
    prompt += f"\n\n{guidance}"

    if rules.get("appendix_b_items"):
        prompt += "\n\n【附录B检查项】\n"
        for item in rules["appendix_b_items"]:
            prompt += f"- {item['id']}: {item['label']}\n"

    return prompt


def build_compliance_fix_prompt(chapter_key: str, work_level: str = "II") -> str:
    """构建规范修复指令的完整提示词"""
    from lib.gb17741_knowledge import get_full_standard_guidance_for_ai

    guidance = get_full_standard_guidance_for_ai(chapter_key, work_level)
    return f"{COMPLIANCE_FIX_SYSTEM_PROMPT}\n\n{guidance}"


def build_add_reference_prompt(chapter_key: str, work_level: str = "II") -> str:
    """构建补充引用指令的完整提示词"""
    from lib.gb17741_knowledge import (
        CHAPTER_STANDARD_MAPPING,
        get_full_standard_guidance_for_ai,
    )

    guidance = get_full_standard_guidance_for_ai(chapter_key, work_level)

    chapter_info = CHAPTER_STANDARD_MAPPING.get(chapter_key, {})
    main_chapters = chapter_info.get("main_chapters", [])
    appendix_b = chapter_info.get("appendix_b", "")

    ref_hint = "\n\n【本章节可引用的国标条款】\n"
    ref_hint += f"- 主要对应条款: 第{'、'.join(main_chapters)}章\n"
    ref_hint += f"- 附录B编号: {appendix_b}\n"

    return f"{ADD_REFERENCE_SYSTEM_PROMPT}\n\n{guidance}{ref_hint}"


def build_normalize_terms_prompt(chapter_key: str = "", work_level: str = "II") -> str:
    """构建规范术语指令的完整提示词（含术语列表和非标准用语映射）"""
    from lib.gb17741_knowledge import NON_STANDARD_TERM_MAPPING, get_all_terms

    terms = get_all_terms()
    terms_text = "【GB 17741-2025 标准术语列表】\n"
    for term_id, term_data in terms.items():
        cn = term_data.get("cn", "")
        en = term_data.get("en", "")
        definition = term_data.get("definition", "")
        terms_text += f"- {term_id} {cn}({en}): {definition}\n"

    # 添加常见非标准用语→标准用语的映射表
    terms_text += "\n【常见非标准用语→标准用语映射】\n"
    for non_std, std in NON_STANDARD_TERM_MAPPING.items():
        terms_text += f'- "{non_std}" → "{std}"\n'

    return NORMALIZE_TERMS_SYSTEM_PROMPT.replace("{terms_list}", terms_text)


def build_validate_params_prompt(work_level: str = "II", chapter_key: str = "") -> str:
    """构建校验参数指令的完整提示词（含数值规则 + 国标技术要求上下文）"""
    from lib.gb17741_knowledge import get_full_standard_guidance_for_ai, get_numeric_rules

    rules = get_numeric_rules(work_level)
    rules_text = f"【{work_level}级工作数值参数要求】\n"
    for param_key, rule in rules.items():
        if "min" in rule:
            rules_text += f"- {rule['label']}: ≥{rule['min']}{rule['unit']}（第{rule['clause']}）\n"
        elif "max" in rule:
            rules_text += f"- {rule['label']}: ≤{rule['max']}{rule['unit']}（第{rule['clause']}）\n"

    prompt = VALIDATE_PARAMS_SYSTEM_PROMPT.replace("{numeric_rules}", rules_text)

    # 注入国标技术要求上下文，让模型理解参数的含义
    guidance = get_full_standard_guidance_for_ai(chapter_key, work_level)
    prompt += f"\n\n{guidance}"

    return prompt
