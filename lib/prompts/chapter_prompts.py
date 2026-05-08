# -*- coding: utf-8 -*-
"""
ajepro backend - 提示词层 - 章节提示词
章节生成相关的提示词构建函数

从 backend/utils/prompts.py 迁移而来，统一到提示词层管理
使用 gb17741_knowledge.py 作为唯一数据源
"""

from lib.gb17741_knowledge import (
    STANDARD_INFO,
    get_chapter_standard_guidance,
    get_chapters_by_level,
    get_level_requirements,
)

# ============================================================
# 章节提示词构建函数
# ============================================================


def build_chapter_prompt(project_data, chapter, chapter_index, total_chapters):
    """
    构建单个章节的生成提示词

    Args:
        project_data: 项目数据字典
        chapter: 章节信息（格式：{'id': 'chapter1', 'title': '...', 'sections': [...]）
        chapter_index: 当前章节索引
        total_chapters: 总章节数

    Returns:
        str: 章节提示词
    """
    project_info = _build_project_info(project_data)
    sections_str = "\n".join([f"- {s}" for s in chapter["sections"]])
    level = project_data.get("level", "II")

    # 获取超越概率参数化指导（用于需要图表的章节）
    exceedance_guidance = _build_exceedance_prob_guidance(project_data)

    # 判断是否是需要包含超越概率参数化图表的章节
    chapters_need_prob_tables = ["chapter7", "chapter8", "appendix"]  # 概率分析、地震动参数、附录
    needs_prob_guidance = chapter["id"] in chapters_need_prob_tables

    # 获取国标知识库中该章节的技术要求和报告编写要求
    standard_guidance_dict = get_chapter_standard_guidance(chapter["id"])
    standard_guidance = ""
    if standard_guidance_dict:
        if standard_guidance_dict.get("technical"):
            standard_guidance += standard_guidance_dict["technical"] + "\n\n"
        if standard_guidance_dict.get("report"):
            standard_guidance += standard_guidance_dict["report"] + "\n\n"
        if standard_guidance_dict.get("clauses"):
            standard_guidance += standard_guidance_dict["clauses"]
    level_requirements = get_level_requirements(level)

    # 附录章节使用特殊的提示词
    if chapter["id"] == "appendix":
        # 构建超越概率相关的附表要求
        exceedance_probs = project_data.get("exceedance_probs", {})
        prob_table_requirement = _build_appendix_table_requirement(exceedance_probs)

        prompt = f"""请为以下工程项目编写技术评价报告的【附录】部分。

{project_info}

{standard_guidance}

【附录要求】
请生成完整的附录内容，包括：

1. **参考文献**（至少列出8-10条）
   必须引用的标准：
   - {STANDARD_INFO["code"]}《{STANDARD_INFO["name"]}》
   - GB 18306《中国地震动参数区划图》
   - GB/T 50011《建筑抗震设计标准》
   - GB 50021《岩土工程勘察规范》
   - GB/T 50269《地基动力特性测试规范》
   - 其他相关区域地震地质研究文献

2. **附表**（生成数据表格）
{prob_table_requirement}

3. **附图说明**
   - 图1：工程场地位置图
   - 图2：区域地震构造图
   - 图3：场地地质剖面图
   - 图4：地震反应谱曲线图（需包含所有超越概率水准）
   - 图5：加速度时程曲线图
   （注：实际图件需根据工程实际情况绘制）
{exceedance_guidance}

【格式要求】
1. 使用Markdown格式
2. 参考文献按标准格式列出
3. 表格使用Markdown表格语法，表头必须清晰标注超越概率参数
4. 内容专业、规范
5. 每个自然段控制在 300～500 字以内，段与段之间用空行分隔
6. 禁止输出超过 500 字的连续不分段文本

请生成附录内容："""
    else:
        # 为需要图表的章节添加超越概率指导
        extra_guidance = exceedance_guidance if needs_prob_guidance else ""

        prompt = f"""请为以下工程项目编写技术评价报告的【{chapter["title"]}】章节。

{project_info}

{standard_guidance}

【{level}级工作要求】
- 工作目标：{level_requirements.get("target", "")}
- 区域范围：{level_requirements.get("requirements", {}).get("region_range", "不小于工程场地外延150km")}

【本章节结构】
章节：{chapter["title"]}
包含内容：
{sections_str}

【技术要求】
1. 使用Markdown格式（##表示章节，###表示小节）
2. 内容必须符合{STANDARD_INFO["code"]}附录B的报告编写要求
3. 技术参数必须符合{STANDARD_INFO["code"]}正文各章节的规定
4. 内容要专业、客观、符合工程技术规范
5. 可使用合理的示例数据进行说明
6. 图表必须与文字结论一一对应，并在段内明确引用（如“见图2-3、表2-1”）
7. 直接输出章节内容

【专业表达与格式增强】
1. 优先使用“先结论后论证”的写法，每小节第一段先给综合判断
2. 关键数据尽量结构化表达：范围、均值、极值、主控因素
3. 章节末尾增加“### 本节小结”，用 2-4 条条目总结
4. 对于图件相关内容，使用规范图题风格（图X-Y 名称）
5. 若可引用生成图件，请使用 Markdown 图片语法，例如：
    - ![图 2-1 区域地震 M-T 图](assets/generated/mt_chart.png)
    - ![图 6-1 设计反应谱对比图](assets/generated/response_spectrum.png)
    - ![图 6-2 不同超越概率 PGA 对比图](assets/generated/pga_comparison.png)

【排版规范——必须严格遵守】
1. 每个自然段控制在 300～500 字以内，段与段之间用空行分隔
2. 不同主题（地质背景、调查方法、分析结论等）必须分段论述，禁止在同一段落中堆砌多个主题
3. 当使用编号列举（如（1）、（2）、①②等）时，每个编号项必须另起一段
4. 禁止输出超过 500 字的连续不分段文本
5. 每段只聚焦一个论点或一组紧密相关的数据
{extra_guidance}

请撰写本章节："""

    return prompt


def build_full_report_prompt(project_data):
    """
    构建完整报告生成的提示词（用于一次性生成简化版）

    Args:
        project_data: 项目数据字典

    Returns:
        str: 完整提示词
    """
    project_info = _build_project_info(project_data)
    level = project_data.get("level", "II")
    chapters = get_chapters_by_level(level)

    # 构建章节结构
    structure = f"# {project_data.get('name', '项目')} 地震安全性评价报告\n\n"
    for chapter in chapters:
        structure += f"## {chapter['title']}\n"
        for section in chapter["sections"]:
            structure += f"### {section}\n"
        structure += "\n"

    prompt = f"""请为以下地震安全性评价项目生成一份完整的{level}级评价报告。

{project_info}

【报告结构】
{structure}

【写作要求】
1. 使用 Markdown 格式
2. 严格按照上述结构撰写
3. 每个小节至少包含1-2段内容
4. 使用专业术语，符合 {STANDARD_INFO["code"]} 标准
5. 结论要明确，参数要具体
6. 每个自然段控制在 300～500 字以内，段与段之间用空行分隔
7. 不同主题必须分段论述，禁止堆砌在同一段落
8. 编号列举项（如（1）（2）①②等）每项必须另起一段

请直接输出完整报告："""

    return prompt


# ============================================================
# 合规检查提示词
# ============================================================

COMPLIANCE_CHECK_PROMPT = f"""请检查以下地震安全性评价报告是否符合 {STANDARD_INFO["code"]} 标准要求。

【检查项目】
1. 章节完整性：是否包含所有必需章节
2. 内容规范性：术语使用是否准确
3. 数据完整性：是否包含必要的参数数据
4. 结论明确性：结论是否清晰、有依据
5. 格式规范性：格式是否符合标准

【报告内容】
{{report_content}}

请逐项检查并给出结果，格式如下：
```json
{{{{
    "章节完整性": {{{{"passed": true/false, "details": "说明"}}}},
    "内容规范性": {{{{"passed": true/false, "details": "说明"}}}},
    "数据完整性": {{{{"passed": true/false, "details": "说明"}}}},
    "结论明确性": {{{{"passed": true/false, "details": "说明"}}}},
    "格式规范性": {{{{"passed": true/false, "details": "说明"}}}},
    "overall_passed": true/false,
    "suggestions": ["改进建议1", "改进建议2"]
}}}}
```
"""


# ============================================================
# 辅助函数
# ============================================================


def _build_project_info(project_data):
    """构建项目信息描述"""
    info = f"""【项目基本信息】
- 项目名称：{project_data.get("name", "未命名项目")}
- 评价等级：{project_data.get("level", "II")}级
- 工程类型：{project_data.get("engineering_type", "一般建筑工程")}
- 项目地址：{project_data.get("location", "未提供")}
- 地理坐标：东经 {project_data.get("coordinate_lon", "未提供")}°，北纬 {project_data.get("coordinate_lat", "未提供")}°
- 建筑高度：{project_data.get("building_height", 0)} 米
- 建设单位：{project_data.get("construction_unit", "未提供")}
- 勘察单位：{project_data.get("survey_unit", "未提供")}
- 评价单位：{project_data.get("evaluation_unit", "未提供")}"""

    # 超越概率信息
    exceedance_probs = project_data.get("exceedance_probs", {})
    if exceedance_probs:
        info += "\n\n【设防要求 - 超越概率设置】"
        if "50_year" in exceedance_probs and exceedance_probs["50_year"]:
            probs = exceedance_probs["50_year"]
            info += f"\n- 50年超越概率：{', '.join([str(p) + '%' for p in probs])}"
        if "100_year" in exceedance_probs and exceedance_probs["100_year"]:
            probs = exceedance_probs["100_year"]
            info += f"\n- 100年超越概率：{', '.join([str(p) + '%' for p in probs])}"

        # 生成图题/表头参考示例
        info += "\n\n【图题/表头命名规范】"
        info += "\n报告中的图、表标题必须明确标注超越概率，格式示例："
        all_probs = []
        if "50_year" in exceedance_probs and exceedance_probs["50_year"]:
            for p in exceedance_probs["50_year"]:
                all_probs.append(f"50年超越概率{p}%")
        if "100_year" in exceedance_probs and exceedance_probs["100_year"]:
            for p in exceedance_probs["100_year"]:
                all_probs.append(f"100年超越概率{p}%")

        if all_probs:
            info += f"\n- 图题示例：「{all_probs[0]}地震动峰值加速度分布图」"
            info += "\n- 表头示例：「不同超越概率下的地震动参数表」"
            info += "\n- 表格中应包含以下超越概率水准的数据行：" + "、".join(all_probs)

    return info


def _build_exceedance_prob_guidance(project_data):
    """构建超越概率参数化图表生成指导"""
    exceedance_probs = project_data.get("exceedance_probs", {})
    if not exceedance_probs:
        return ""

    guidance = "\n\n【重要：图表参数化要求】"
    guidance += "\n本报告需要覆盖以下超越概率水准，所有相关图表必须针对这些参数生成："

    all_probs = []
    if "50_year" in exceedance_probs and exceedance_probs["50_year"]:
        for p in exceedance_probs["50_year"]:
            all_probs.append({"period": "50年", "prob": p, "label": f"50年超越概率{p}%"})
    if "100_year" in exceedance_probs and exceedance_probs["100_year"]:
        for p in exceedance_probs["100_year"]:
            all_probs.append({"period": "100年", "prob": p, "label": f"100年超越概率{p}%"})

    if all_probs:
        guidance += "\n\n需覆盖的超越概率水准："
        for prob in all_probs:
            guidance += f"\n- {prob['label']}"

        guidance += "\n\n图表命名要求："
        guidance += f"\n1. 每个超越概率水准需单独成图，如：「图X-X {all_probs[0]['label']}地震动峰值加速度分布」"
        guidance += "\n2. 汇总表格需包含所有超越概率水准的数据行"
        guidance += "\n3. 表头需明确标注「超越概率」列"

    return guidance


def _build_appendix_table_requirement(exceedance_probs):
    """构建附录表格要求，根据超越概率参数动态生成"""
    if not exceedance_probs:
        return """   - 表1：场地钻孔土层参数汇总表（包含土层名称、厚度、密度、剪切波速等）
   - 表2：地震动参数汇总表（不同超越概率下的峰值加速度等）
   - 表3：场地液化判别结果表（如适用）"""

    # 收集所有超越概率
    all_probs = []
    if "50_year" in exceedance_probs and exceedance_probs["50_year"]:
        for p in exceedance_probs["50_year"]:
            all_probs.append(f"50年超越概率{p}%")
    if "100_year" in exceedance_probs and exceedance_probs["100_year"]:
        for p in exceedance_probs["100_year"]:
            all_probs.append(f"100年超越概率{p}%")

    prob_list_str = "、".join(all_probs) if all_probs else "各超越概率水准"

    requirement = f"""   - 表1：场地钻孔土层参数汇总表（包含土层名称、厚度、密度、剪切波速等）
   - 表2：地震动参数汇总表【重要：必须包含{prob_list_str}的数据行】
     * 表格应包含列：超越概率水准、重现周期(年)、水平向峰值加速度PGA(g)、特征周期Tg(s)、
       反应谱平台值βmax、设计地震分组、场地类别、地震影响系数最大值αmax
     * 每个超越概率水准单独一行
   - 表3：不同超越概率下反应谱特征值表
   - 表4：场地液化判别结果表（如适用）"""

    return requirement


# ============================================================
# 兼容旧版API
# ============================================================


def get_report_structure(level):
    """获取报告结构模板（兼容旧版）"""
    chapters = get_chapters_by_level(level)
    structure = ""
    for chapter in chapters:
        structure += f"\n## {chapter['title']}\n"
        for section in chapter["sections"]:
            structure += f"### {section}\n"
    return structure


def build_report_prompt(project_data):
    """构建报告提示词（兼容旧版，现在使用分章节生成）"""
    return build_full_report_prompt(project_data)
