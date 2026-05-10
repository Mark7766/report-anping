# -*- coding: utf-8 -*-
from __future__ import annotations

"""
GB 17741-2025 国标知识库
工程场地地震安全性评价标准知识库

提供：
1. 章节与国标条款的映射关系
2. 附录B报告编写要求
3. 技术要求与参数标准
4. 术语定义
5. 核心公式
6. 技术表格

数据来源：backend/data/standards/gb17741_2025_*.json
"""

import json
import os
from functools import lru_cache
from typing import Dict, List, Optional

# ============================================================
# JSON数据加载
# ============================================================

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "standards")


def _load_json_file(filename: str) -> dict:
    """加载JSON文件"""
    filepath = os.path.join(_DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@lru_cache(maxsize=1)
def _load_all_standard_data() -> dict:
    """加载所有国标数据（带缓存）"""
    data = {
        "terms": _load_json_file("gb17741_2025_terms.json"),
        "tables": _load_json_file("gb17741_2025_tables.json"),
        "formulas": _load_json_file("gb17741_2025_formulas.json"),
        "chapter4": _load_json_file("gb17741_2025_chapter4.json"),
        "chapter5": _load_json_file("gb17741_2025_chapter5.json"),
        "chapter6": _load_json_file("gb17741_2025_chapter6.json"),
        "chapter7_9": _load_json_file("gb17741_2025_chapter7_9.json"),
        "chapter10_11": _load_json_file("gb17741_2025_chapter10_11.json"),
        "chapter12_14": _load_json_file("gb17741_2025_chapter12_14.json"),
        "appendix_b": _load_json_file("gb17741_2025_appendix_b.json"),
    }
    return data


# ============================================================
# 国标基本信息
# ============================================================

STANDARD_INFO = {
    "code": "GB 17741-2025",
    "name": "工程场地地震安全性评价",
    "publish_date": "2025-02-28",
    "implement_date": "2025-09-01",
    "replaced": "GB 17741-2005",
}

# ============================================================
# 工作等级定义（第4章）
# ============================================================

WORK_LEVELS = {
    "I": {
        "name": "I级工作",
        "target": "场地极罕遇地震动参数（重现期10000a或年超越概率1×10⁻⁴）确定、能动断层鉴定",
        "contents": [
            "区域地震活动性和地震构造评价",
            "近场区地震活动性和地震构造评价",
            "场址附近范围能动断层鉴定",
            "场地地震工程地质条件勘测",
            "地震动预测方程确定",
            "地震危险性确定性分析",
            "地震危险性概率分析",
            "场地地震动参数确定",
            "场地地震地质灾害评价",
        ],
        "requirements": {
            "region_range": "不小于工程场地外延150km",
            "near_field_range": "不小于工程场地外延25km",
            "site_nearby_range": "不小于工程场地外延5km",
            "map_scale": {"region": "1:1000000", "near_field": "1:100000", "site_nearby": "1:25000"},
            "borehole_count": "不少于5个",
            "borehole_depth": "达到基岩或剪切波速≥800m/s",
            "time_history_groups": "不少于20组",
        },
    },
    "II": {
        "name": "II级工作",
        "target": "场地多概率水准地震动参数确定、断层活动性相关场址条件评价",
        "subtypes": {
            "II1": "需在场址附近范围内开展满足不小于1:50000调查精度要求的断层活动性评价工作",
            "II2": "其他II级工作",
        },
        "contents": [
            "区域地震活动性和地震构造评价",
            "近场区地震活动性和地震构造评价",
            "场址附近范围断层活动性鉴定（II1类）",
            "场地地震工程地质条件勘测",
            "地震动预测方程确定",
            "地震危险性概率分析",
            "场地地震动参数确定",
            "场地地震地质灾害评价",
        ],
        "requirements": {
            "region_range": "不小于工程场地外延150km",
            "near_field_range": "不小于工程场地外延25km",
            "map_scale": {"region": "1:1000000", "near_field": "1:250000"},
            "borehole_count": "不少于3个",
            "borehole_depth": "达到基岩或剪切波速≥500m/s",
            "time_history_groups": "不少于10组",
        },
    },
    "III": {
        "name": "III级工作",
        "target": "线状工程沿线场地地震动参数区划、活动断层断错影响评价",
        "contents": [
            "区域地震活动性和地震构造评价",
            "近场区地震活动性和地震构造评价",
            "地震动预测方程确定",
            "地震危险性概率分析",
            "II类场地地震动参数确定",
            "场地断层错动评价",
        ],
        "requirements": {
            "region_range": "不小于工程场地外延150km",
            "map_scale": {"region": "1:2500000"},
            "calculation_spacing": "不大于2km，变化大时不大于1km",
        },
    },
}

# ============================================================
# 报告章节与国标条款映射
# ============================================================

CHAPTER_STANDARD_MAPPING = {
    "preface": {
        "title": "前言",
        "chapter_number": "0",
        "work_levels": ["I", "II", "III"],
        "sections": ["0.1 项目概况", "0.2 评价依据", "0.3 评价等级确定", "0.4 工作内容"],
        "appendix_b": "B.1",
        "main_chapters": ["4"],
        "report_requirements": """【GB 17741-2025 附录B.1 前言编写要求】
应陈述工程基本信息，明确评价目标与任务要求，确定工作等级以及工作技术途径，概括任务完成状况与实际工作量、人员组织与报告编写信息。

必须包含以下基本技术信息：
a) 项目名称
b) 场址及其经纬度坐标（精确到小数点后2位）、地震动参数区划分区
c) 工程抗震设防需求：工程类型与结构特点、抗震设防分类、抗震设计参数
d) 工程场地地震安全性评价技术任务要求
e) 工程场地地震安全性评价工作等级、依据的标准、技术路线、评价成果指标
f) 项目执行情况：人员组成及签名、报告主要起草人专业能力证明材料、工作进程、实际工作量
g) 项目报告编写""",
    },
    "chapter1": {
        "title": "区域地震活动性和地震构造评价",
        "chapter_number": "1",
        "work_levels": ["I", "II", "III"],
        "sections": ["1.1 区域地震活动性评价", "1.2 区域地震构造评价", "1.3 区域地震影响分析"],
        "appendix_b": "B.2, B.3",
        "main_chapters": ["5.2", "5.3"],
        "technical_requirements": """【GB 17741-2025 第5章技术要求】

5.1 区域范围和图件比例尺
- 区域范围应不小于工程场地外延150km
- I级工作区域图件比例尺不小于1:1000000

5.2 区域地震活动性
- 编录区域内震级≥4.7级破坏性地震事件
- 编录仪器记录的震级<4.7级中小地震事件
- 分析区域地震活动时空特征
- 分析区域现代构造应力场特征
- 评价工程场地地震影响

5.3 区域地震构造
- 开展区域地质构造分析
- 开展区域新构造分析
- 区域断层活动性评价
- 编制区域地震构造图""",
        "report_requirements": """【GB 17741-2025 附录B.2 区域与近场区地震活动性评价编写要求】
应总结陈述按照5.2与6.2要求开展的工作、获得的结果、分析的数据及评价的结论，包含下列内容：

a) 地震资料：地震目录、完整性分析
b) 区域地震活动空间分布特征
c) 区域地震活动时间分布特征
d) 区域现代构造应力场
e) 工程场地历史地震影响
f) 近场区地震活动性
g) 地震活动性综合评价

【GB 17741-2025 附录B.3 区域地震构造评价编写要求】
a) 区域地质构造
b) 区域新构造
c) 区域地球物理场
d) 区域断层活动性
e) 区域地震构造特征
f) 地震构造综合评价""",
    },
    "chapter2": {
        "title": "近场区地震活动性和地震构造评价",
        "chapter_number": "2",
        "work_levels": ["I", "II", "III"],
        "sections": ["2.1 近场区地震活动性评价", "2.2 近场区地震构造评价", "2.3 发震构造分析"],
        "appendix_b": "B.2, B.4",
        "main_chapters": ["6.2", "6.3"],
        "technical_requirements": """【GB 17741-2025 第6章技术要求】

6.1 近场区范围和图件比例尺
- 近场区范围应不小于工程场地外延25km
- I级工作图件比例尺应不小于1:100000
- 探槽剖面图比例尺应不小于1:50

6.2 近场区地震活动性
- I级工作应对参数有疑问的地震事件进行核查
- I级工作应对震级<4.7级的仪器记录地震重新定位
- 分析近场区地震活动性特征

6.3 近场区地震构造
- 近场区地质构造特征分析
- 近场区主要断层活动性鉴定
- 编制近场区地震构造图""",
        "report_requirements": """【GB 17741-2025 附录B.4 近场区地震构造评价编写要求】
a) 近场区地质构造
b) 近场区第四纪构造活动
c) 近场区主要断层活动性鉴定
d) 近场区地震构造特征""",
    },
    "chapter3": {
        "title": "场址附近范围能动断层鉴定",
        "chapter_number": "3",
        "work_levels": ["I", "II"],
        "sections": ["3.1 场址附近断层调查", "3.2 断层活动性鉴定", "3.3 能动断层判定"],
        "appendix_b": "B.5, B.6, B.7",
        "main_chapters": ["7", "8.4"],
        "technical_requirements": """【GB 17741-2025 第7章技术要求】

7.1 场址附近范围
- 场址附近范围应不小于工程场地外延5km
- I级工作图件比例尺应不小于1:25000

7.2 场址附近范围断层活动性鉴定
- 搜集空间分辨率优于2m的遥感影像进行第四纪断层解译
- 每条断层验证的观测点不少于2个

7.3 能动断层鉴定标准
断层符合下列条件之一时，应鉴定为能动断层：
a) 晚更新世(距今120000a)以来存在明显活动证据
b) 与已知能动断层存在明确的构造联系
c) 可合理推断在地表或近地表处可产生断错活动""",
        "report_requirements": """【GB 17741-2025 附录B.5/B.6/B.7编写要求】
B.5 场址附近范围断层活动性评价
B.6 场地活动断层勘查
B.7 场址附近范围能动断层鉴定""",
    },
    "chapter4": {
        "title": "场地地震工程地质条件勘测",
        "chapter_number": "4",
        "work_levels": ["I", "II", "III"],
        "sections": ["4.1 场地工程地质条件", "4.2 场地钻孔勘查与波速测试", "4.3 场地类别确定", "4.4 岩土动力性质试验"],
        "appendix_b": "B.11",
        "main_chapters": ["8.1", "8.2", "8.3"],
        "technical_requirements": """【GB 17741-2025 第8章技术要求】

8.2 场地地震工程地质条件钻孔勘测
- 钻孔间距不大于500m
- I级工作不少于5个钻孔，II级工作不少于3个钻孔
- I级工作钻孔达到基岩或剪切波速≥800m/s
- II级工作钻孔达到基岩或剪切波速≥500m/s
- 波速测试沿深度间距不大于2m

8.3 场地岩土动力性质试验
- I级工作测试点数量不少于12个
- II级工作测试点数量不少于8个""",
        "report_requirements": """【GB 17741-2025 附录B.11 工程场地地震工程地质条件勘测编写要求】
a) 场地工程地质条件概述
b) 场地钻孔勘查
c) 钻孔波速测试
d) 工程场地类别
e) 场地岩土动力性质试验""",
    },
    "chapter5": {
        "title": "地震动预测方程确定",
        "chapter_number": "5",
        "work_levels": ["I", "II", "III"],
        "sections": ["5.1 地震动预测方程选择", "5.2 基岩地震动预测方程确定", "5.3 方程适用性验证"],
        "appendix_b": "B.8",
        "main_chapters": ["9"],
        "technical_requirements": """【GB 17741-2025 第9章技术要求】

9.1 地震动预测方程表达
- 应采用数学函数式或表格形式表达
- 应反映高频地震动的震级和距离饱和特性
- 地震动反应谱预测方程的周期应满足工程需求且不小于6s
- 周期点在对数坐标下应近似均匀分布且数量不少于20个

9.2 基岩地震动预测方程确定
- 强震动观测数据充足地区应采用统计方法建立
- 数据不足地区应采用类比性方法确定
- 应论证地震动预测方程的适用性""",
        "report_requirements": """【GB 17741-2025 附录B.8 地震动预测方程确定编写要求】
a) 地震动预测方程基本原理论述
b) 地震动预测方程与参数确定方法与确定结果论述
c) 地震动预测方程适用性论证""",
    },
    "chapter6": {
        "title": "地震危险性确定性分析",
        "chapter_number": "6",
        "work_levels": ["I"],
        "sections": ["6.1 确定性震源模型", "6.2 最大潜在地震确定", "6.3 确定性地震危险性计算", "6.4 确定性分析结果"],
        "appendix_b": "B.9",
        "main_chapters": ["10"],
        "technical_requirements": """【GB 17741-2025 第10章技术要求】

10.1 确定性地震危险性分析震源模型
震源类型包括：
- 地震构造区及其最大潜在地震
- 发震构造及其最大潜在地震

地震构造区最大潜在地震震级不应小于5.0级
发震构造最大潜在地震震级不应小于5.5级

10.2 确定性地震危险性计算要求
- 将最大潜在地震置于距场址最近处
- 考虑地震动预测方程的不确定性
- 最近距离≤10km时，基于近场强震动数据评定

10.3 结果要求
- 地震动加速度反应谱控制点通常取0.0s, 0.2s, 2.0s, 4.0s周期点""",
        "report_requirements": """【GB 17741-2025 附录B.9 地震危险性确定性分析编写要求】
a) 区域地震构造环境
b) 确定性震源模型
c) 确定性地震危险性计算""",
    },
    "chapter7": {
        "title": "地震危险性概率分析",
        "chapter_number": "7",
        "work_levels": ["I", "II", "III"],
        "sections": ["7.1 潜在震源区划分", "7.2 地震活动性参数确定", "7.3 概率地震危险性计算", "7.4 概率分析结果"],
        "appendix_b": "B.10",
        "main_chapters": ["11"],
        "technical_requirements": """【GB 17741-2025 第11章技术要求】

11.1 概率地震危险性分析潜在震源区模型
三层级源区构成：
- 地震统计区及其地震活动模型
- 背景地震潜在震源区及其震级上限
- 构造潜在震源区及其震级上限

11.5 概率地震危险性分析计算要求
- 根据工程抗震设防需要确定超越概率水平
- III级工作计算场点间距应不大于2km
- 在结果变化较大地段（相邻点差异超过5%），间距应不大于1km
- 应计算地震动参数超越概率曲线
- 应计算各超越概率水平地震动反应谱曲线

11.6 概率地震危险性分析结果
- 编制基岩场地地震动参数表
- 编制超越概率曲线（延至最低年超越概率1×10⁻⁵）
- 反应谱控制周期点：0.0s, 0.2s, 2.0s, 4.0s""",
        "report_requirements": """【GB 17741-2025 附录B.10 地震危险性概率分析编写要求】
a) 概率地震危险性分析方法概述
b) 潜在震源区划分
c) 地震活动性参数确定
d) 概率地震危险性计算""",
    },
    "chapter8": {
        "title": "场地地震动参数确定",
        "chapter_number": "8",
        "work_levels": ["I", "II", "III"],
        "sections": ["8.1 场地土层反应分析", "8.2 输入地震动时程确定", "8.3 场地地震动参数", "8.4 场地地震动时程"],
        "appendix_b": "B.12, B.13",
        "main_chapters": ["12"],
        "technical_requirements": """【GB 17741-2025 第12章技术要求】

12.1 场地地震反应分析模型
- 地表、土层界面及基岩面均较平坦时，采用一维土层反应分析模型
- 起伏较大时，采用二维或三维土层反应分析模型

12.2 输入地震动时程的确定
- I级工作不少于20组，II级工作不少于10组
- 不同时程样本相关系数不大于0.16
- 目标反应谱控制点频率间隔按表1确定
- 反应谱相对误差绝对值不大于5%

表1 目标反应谱控制点频率间隔（Hz）：
< 0.2: 0.02
0.2~2.9: 0.10
3.0~3.5: 0.15
3.6~4.9: 0.20
5.0~7.9: 0.25
8.0~14.9: 0.50
15.0~17.9: 1.00
18.0~21.9: 2.00
≥22.0: 3.00

12.4 场地地震动参数确定
- I级工作取确定性方法和概率方法结果的包络
- II级工作根据概率地震危险性分析结果确定
- 竖向与水平向地震动比值应不小于2/3

12.5 场地地震动时程
- 强震平稳段持续时间大于6.0s
- 有效持时不低于结构基本自振周期的5倍""",
        "report_requirements": """【GB 17741-2025 附录B.12/B.13编写要求】
B.12 场地土层反应分析
a) 基岩输入地震动时程确定
b) 场地土层地震反应分析

B.13 场地地震动参数确定
a) I级工作场地地震动参数
b) II级工作场地地震动参数
c) III级工作场地地震动参数区划
d) 场地地震动时程确定""",
    },
    "chapter9": {
        "title": "场地地震地质灾害评价",
        "chapter_number": "9",
        "work_levels": ["I", "II"],
        "sections": ["9.1 断层错动评价", "9.2 地震液化评价", "9.3 软土震陷评价", "9.4 地震崩塌与滑坡评价"],
        "appendix_b": "B.14",
        "main_chapters": ["13"],
        "technical_requirements": """【GB 17741-2025 第13章技术要求】

13.1 断层错动评价
- 编制断层地震地表破裂影响带分布图，比例尺不小于1:10000
- 给出断层面上走滑位移和倾滑位移分量

13.2 地震液化初步评价
- 按GB/T 50011进行地震液化初步判别
- 地面以下20m深度范围内可液化土层按标准判别
- 20m以下采用标准贯入试验判别法

液化判别公式参数：
- 调整系数β₀按特征周期Tg确定：
  Tg<0.40s: β₀=0.85
  Tg=0.40~0.45s: β₀=1.00
  Tg>0.45s: β₀=1.10

13.3 软土震陷初步评价
- 按JGJ83规定的软土震陷判别方法进行

13.4 地震崩塌与滑坡初步评价
- 计算地震崩塌滑坡危险性指数H = Ss × Sp × Sr
- 危险性指数H：1~4低，6~12中，18~27高""",
        "report_requirements": """【GB 17741-2025 附录B.14 场地地震地质灾害评价编写要求】
a) 断层错动评价论述
b) 地震液化评价论述
c) 软土震陷评价论述
d) 崩塌滑坡评价论述""",
    },
    "chapter10": {
        "title": "结论与建议",
        "chapter_number": "10",
        "work_levels": ["I", "II", "III"],
        "sections": ["10.1 主要结论", "10.2 抗震设防建议"],
        "appendix_b": "B.15",
        "main_chapters": ["14"],
        "report_requirements": """【GB 17741-2025 附录B.15 结论编写要求】
应总结概述各调查范围地震活动性评价与地震构造评价的主要结论，总结给出工程场地地震动参数的评价结果，总结陈述工程场地地震地质灾害评价结论。

结论应包括：
1. 区域与近场区地震活动性评价主要结论
2. 区域与近场区地震构造评价主要结论
3. 场址断层活动性/能动断层鉴定结论
4. 场地工程地质条件评价结论
5. 地震危险性分析主要结果
6. 场地地震动参数（各超越概率水平）
7. 场地地震地质灾害评价结论
8. 抗震设防建议""",
    },
    "appendix": {
        "title": "附录",
        "chapter_number": "附录",
        "work_levels": ["I", "II", "III"],
        "sections": ["附录A 地震动反应谱与功率谱", "参考文献", "附表", "附图"],
        "appendix_b": "附录A",
        "main_chapters": ["附录A", "参考文献"],
        "technical_requirements": """【GB 17741-2025 附录A】
与目标地震动反应谱匹配的目标功率谱的确定方法

A.1 基本步骤
a) 获得5%阻尼比目标地震动反应谱
b) 按标准地震动反应谱控制点谱值进行插值
c) 计算标准功率谱
d) 计算目标功率谱

标准地震动反应谱控制点谱值：
频率(Hz) | 谱值(gn)
33.0     | 1.0
9.0      | 2.61
2.5      | 3.13
0.25     | 0.472""",
        "report_requirements": """【附录编写要求】
1. 参考文献
   - 国家标准（GB 17741-2025、GB 18306、GB/T 50011等）
   - 行业规范和技术标准
   - 区域地震地质研究文献

2. 附表
   - 场地钻孔土层参数汇总表
   - 地震动参数汇总表（各超越概率水平）
   - 场地液化判别结果表

3. 附图
   - 工程场地位置图
   - 区域/近场区地震构造图
   - 场地地质剖面图
   - 地震反应谱曲线图
   - 加速度时程曲线图""",
    },
}

# ============================================================
# 工作等级→章节映射
# ============================================================

WORK_LEVEL_CHAPTERS = {
    "I": [
        "preface",
        "chapter1",
        "chapter2",
        "chapter3",
        "chapter4",
        "chapter5",
        "chapter6",
        "chapter7",
        "chapter8",
        "chapter9",
        "chapter10",
        "appendix",
    ],
    "II": [
        "preface",
        "chapter1",
        "chapter2",
        "chapter3",
        "chapter4",
        "chapter5",
        "chapter7",
        "chapter8",
        "chapter9",
        "chapter10",
        "appendix",
    ],
    "III": ["preface", "chapter1", "chapter2", "chapter4", "chapter5", "chapter7", "chapter8", "appendix"],
}

# ============================================================
# 关键技术参数（从国标提取）
# ============================================================

TECHNICAL_PARAMETERS = {
    "response_spectrum_periods": {
        "control_points": ["0.0s", "0.2s", "2.0s", "4.0s"],
        "description": "地震动加速度反应谱控制周期点",
    },
    "exceedance_probability": {
        "common_levels": {
            "50_year_63%": "多遇地震",
            "50_year_10%": "设防地震",
            "50_year_2%": "罕遇地震",
            "100_year_2%": "极罕遇地震",
            "100_year_1%": "极罕遇地震",
        },
        "return_period": {"10000a": "I级工作极罕遇地震动参数"},
    },
    "frequency_intervals": {
        "description": "目标反应谱控制点频率间隔（表1）",
        "values": {
            "< 0.2 Hz": "0.02 Hz",
            "0.2~2.9 Hz": "0.10 Hz",
            "3.0~3.5 Hz": "0.15 Hz",
            "3.6~4.9 Hz": "0.20 Hz",
            "5.0~7.9 Hz": "0.25 Hz",
            "8.0~14.9 Hz": "0.50 Hz",
            "15.0~17.9 Hz": "1.00 Hz",
            "18.0~21.9 Hz": "2.00 Hz",
            "≥22.0 Hz": "3.00 Hz",
        },
    },
    "liquefaction_adjustment": {
        "description": "液化判别调整系数β₀（表2）",
        "values": {"Tg < 0.40s": 0.85, "Tg = 0.40~0.45s": 1.00, "Tg > 0.45s": 1.10},
    },
}

# ============================================================
# 引用标准列表
# ============================================================

REFERENCE_STANDARDS = [
    "GB 17740 地震震级的规定",
    "GB/T 18207（所有部分）防震减灾术语",
    "GB 18306 中国地震动参数区划图",
    "GB/T 36072 活动断层探测",
    "GB/T 50011 建筑抗震设计标准",
    "GB 50021 岩土工程勘察规范",
    "GB/T 50269 地基动力特性测试规范",
    "JGJ 83 软土地区岩土工程勘察规程",
]


# ============================================================
# 新增：术语定义查询
# ============================================================


def get_all_terms() -> Dict[str, dict]:
    """获取所有术语定义"""
    data = _load_all_standard_data()
    terms_data = data.get("terms", {})
    return terms_data.get("terms", {})


def get_term(term_id: str) -> Optional[dict]:
    """获取指定术语定义

    Args:
        term_id: 术语编号，如 '3.1', '3.15'

    Returns:
        术语定义字典，包含cn、en、definition等字段
    """
    terms = get_all_terms()
    return terms.get(term_id)


def search_term(keyword: str) -> List[dict]:
    """搜索术语

    Args:
        keyword: 搜索关键词（中文或英文）

    Returns:
        匹配的术语列表
    """
    terms = get_all_terms()
    results = []
    keyword_lower = keyword.lower()
    for term_id, term_data in terms.items():
        if (
            keyword in term_data.get("cn", "")
            or keyword_lower in term_data.get("en", "").lower()
            or keyword in term_data.get("definition", "")
        ):
            results.append({"id": term_id, **term_data})
    return results


# ============================================================
# 新增：技术表格查询
# ============================================================


def get_all_tables() -> Dict[str, dict]:
    """获取所有技术表格"""
    data = _load_all_standard_data()
    tables_data = data.get("tables", {})
    return tables_data.get("tables", {})


def get_table(table_id: str) -> Optional[dict]:
    """获取指定表格

    Args:
        table_id: 表格ID，如 'table1', 'table2', 'tableA1'

    Returns:
        表格数据字典
    """
    tables = get_all_tables()
    return tables.get(table_id)


def get_frequency_interval_table() -> dict:
    """获取目标反应谱控制点频率间隔表（表1）"""
    return get_table("table1")


def get_liquefaction_adjustment_table() -> dict:
    """获取液化判别调整系数表（表2）"""
    return get_table("table2")


def get_landslide_hazard_tables() -> dict:
    """获取地震崩塌滑坡相关表格（表3-6）"""
    return {
        "slope_factor": get_table("table3"),
        "seismic_factor": get_table("table4"),
        "condition_factor": get_table("table5"),
        "hazard_level": get_table("table6"),
    }


# ============================================================
# 新增：核心公式查询
# ============================================================


def get_all_formulas() -> Dict[str, dict]:
    """获取所有核心公式"""
    data = _load_all_standard_data()
    formulas_data = data.get("formulas", {})
    return formulas_data.get("formulas", {})


def get_formula(formula_id: str) -> Optional[dict]:
    """获取指定公式

    Args:
        formula_id: 公式ID，如 'formula1', 'formula2', 'formulaA1'

    Returns:
        公式数据字典，包含title、latex、parameters等字段
    """
    formulas = get_all_formulas()
    return formulas.get(formula_id)


def get_response_spectrum_formula() -> dict:
    """获取场地地震动反应谱公式（公式1）"""
    return get_formula("formula1")


def get_liquefaction_formula() -> dict:
    """获取液化判别公式（公式2）"""
    return get_formula("formula2")


def get_landslide_hazard_formula() -> dict:
    """获取地震崩塌滑坡危险性指数公式（公式3）"""
    return get_formula("formula3")


# ============================================================
# 新增：章节详细条款查询
# ============================================================


def get_chapter_clauses(chapter_num: int) -> dict:
    """获取指定章节的详细条款

    Args:
        chapter_num: 章节号，如 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14

    Returns:
        章节条款数据
    """
    data = _load_all_standard_data()

    if chapter_num == 4:
        return data.get("chapter4", {}).get("chapters", {})
    elif chapter_num == 5:
        return data.get("chapter5", {}).get("chapters", {})
    elif chapter_num == 6:
        return data.get("chapter6", {}).get("chapters", {})
    elif chapter_num in [7, 8, 9]:
        chapters = data.get("chapter7_9", {}).get("chapters", {})
        return chapters.get(str(chapter_num), {})
    elif chapter_num in [10, 11]:
        chapters = data.get("chapter10_11", {}).get("chapters", {})
        return chapters.get(str(chapter_num), {})
    elif chapter_num in [12, 13, 14]:
        chapters = data.get("chapter12_14", {}).get("chapters", {})
        return chapters.get(str(chapter_num), {})
    return {}


def get_clause(clause_id: str) -> Optional[dict]:
    """获取指定条款

    Args:
        clause_id: 条款编号，如 '5.2.1', '11.4.2'

    Returns:
        条款内容
    """
    parts = clause_id.split(".")
    if len(parts) < 2:
        return None

    chapter_num = int(parts[0])
    chapter_data = get_chapter_clauses(chapter_num)

    if not chapter_data:
        return None

    # 尝试查找条款
    section_key = f"{parts[0]}.{parts[1]}"
    section = chapter_data.get("sections", chapter_data).get(section_key, {})

    if len(parts) == 2:
        return section

    clause_key = clause_id
    clauses = section.get("clauses", {})
    return clauses.get(clause_key)


# ============================================================
# 新增：附录B报告内容查询
# ============================================================


def get_appendix_b() -> dict:
    """获取附录B完整内容"""
    data = _load_all_standard_data()
    return data.get("appendix_b", {}).get("appendix_b", {})


def get_appendix_b_section(section_id: str) -> Optional[dict]:
    """获取附录B指定节的内容

    Args:
        section_id: 节编号，如 'B.1', 'B.2', 'B.15'

    Returns:
        节内容，包含title、description、required_content等
    """
    appendix_b = get_appendix_b()
    return appendix_b.get(section_id)


# ============================================================
# 增强版：章节国标指导内容（整合JSON数据）
# ============================================================


def get_chapter_standard_guidance(chapter_id: str) -> dict:
    """
    获取指定章节的国标指导内容（结构化版本）

    Args:
        chapter_id: 章节ID，如 'chapter1', 'preface' 等

    Returns:
        dict: 结构化的国标指导内容，包含 technical, report, clauses 三个字段
    """
    # 保持原有映射兼容
    mapping = CHAPTER_STANDARD_MAPPING.get(chapter_id)
    if not mapping:
        return {}

    result = {"technical": "", "report": "", "clauses": ""}

    # 添加技术要求
    if "technical_requirements" in mapping:
        result["technical"] = mapping["technical_requirements"].strip()

    # 添加报告编写要求
    if "report_requirements" in mapping:
        result["report"] = mapping["report_requirements"].strip()

    # 从JSON数据补充详细条款
    chapter_num_map = {
        "preface": 4,
        "chapter1": 5,
        "chapter2": 6,
        "chapter3": 7,
        "chapter4": 8,
        "chapter5": 9,
        "chapter6": 10,
        "chapter7": 11,
        "chapter8": 12,
        "chapter9": 13,
        "chapter10": 14,
        "appendix": None,
    }

    chapter_num = chapter_num_map.get(chapter_id)
    if chapter_num:
        detailed_clauses = get_chapter_clauses(chapter_num)
        if detailed_clauses:
            result["clauses"] = _format_clauses(detailed_clauses).strip()

    return result


def _format_clauses(clauses: dict, indent: int = 0) -> str:
    """递归格式化条款内容"""
    result = ""
    prefix = "  " * indent

    if isinstance(clauses, str):
        return f"{prefix}{clauses}\n"

    if isinstance(clauses, dict):
        for key, value in clauses.items():
            if key in ["title", "content", "note", "description"]:
                if value:
                    result += f"{prefix}{value}\n"
            elif key == "items":
                for item in value:
                    result += f"{prefix}  {item}\n"
            elif key == "clauses":
                result += _format_clauses(value, indent)
            elif key == "sections":
                result += _format_clauses(value, indent)
            elif isinstance(value, dict):
                result += f"\n{prefix}【{key}】\n"
                result += _format_clauses(value, indent + 1)

    return result


# ============================================================
# 新增：获取完整国标指导（用于AI生成）
# ============================================================


def get_full_standard_guidance_for_ai(chapter_id: str, work_level: str = "II") -> str:
    """
    获取完整的国标指导内容，用于AI生成报告时的知识注入

    当 chapter_id 为空时，提供国标全局概述（覆盖所有章节的要点）
    当 chapter_id 非空时，提供该章节的详细技术要求和编写要求

    Args:
        chapter_id: 章节ID
        work_level: 工作等级 'I', 'II', 'III'

    Returns:
        完整的国标指导内容
    """
    guidance = []

    # 1. 基本信息
    guidance.append(f"【国标标准】{STANDARD_INFO['code']} {STANDARD_INFO['name']}")
    guidance.append(f"【工作等级】{work_level}级工作")
    guidance.append("")

    # 2. 工作等级要求
    level_req = get_level_requirements(work_level)
    if level_req:
        guidance.append("【工作等级技术要求】")
        guidance.append(f"目标：{level_req.get('target', '')}")
        if "requirements" in level_req:
            for key, value in level_req["requirements"].items():
                if isinstance(value, dict):
                    guidance.append(f"  {key}:")
                    for k, v in value.items():
                        guidance.append(f"    - {k}: {v}")
                else:
                    guidance.append(f"  - {key}: {value}")
        guidance.append("")

    # 3. 章节具体要求
    if chapter_id:
        # 指定了具体章节：提供详细的技术要求和编写要求
        chapter_guidance = get_chapter_standard_guidance(chapter_id)
        if chapter_guidance:
            if chapter_guidance.get("technical"):
                guidance.append(chapter_guidance["technical"])
            if chapter_guidance.get("report"):
                guidance.append(chapter_guidance["report"])
            if chapter_guidance.get("clauses"):
                guidance.append(chapter_guidance["clauses"])
    else:
        # 未指定章节：提供国标全局概述，涵盖所有章节核心要求
        guidance.append("【GB 17741-2025 国标全局要求概述】")
        guidance.append("（未指定具体章节，提供所有章节核心技术要求摘要）\n")
        for cid, mapping in CHAPTER_STANDARD_MAPPING.items():
            title = mapping.get("title", cid)
            appendix_b = mapping.get("appendix_b", "")
            guidance.append(f"■ {title}（附录{appendix_b}）")
            # 从 technical_requirements 中提取前几行作为摘要
            tech = mapping.get("technical_requirements", "")
            if tech:
                # 提取条目（以 - 开头的行），最多取6条
                items = [
                    line.strip()
                    for line in tech.split("\n")
                    if line.strip().startswith("- ") or line.strip().startswith("【")
                ]
                for item in items[:6]:
                    guidance.append(f"  {item}")
            # 从 report_requirements 提取编写要点
            report = mapping.get("report_requirements", "")
            if report:
                items = [
                    line.strip()
                    for line in report.split("\n")
                    if line.strip().startswith(("a)", "b)", "c)", "d)", "e)", "f)", "g)"))
                ]
                if items:
                    guidance.append(f"  编写要求: {'; '.join(items[:4])}")
            guidance.append("")

    # 4. 相关术语（选择性添加）
    chapter_terms_map = {
        "preface": ["3.10"],  # 地震危险性分析
        "chapter1": ["3.3", "3.6", "3.7", "3.8"],  # 地震带、地震构造等
        "chapter2": ["3.11", "3.13"],  # 发震构造、活动构造
        "chapter3": ["3.15"],  # 能动断层
        "chapter7": ["3.9", "3.16", "3.17", "3.19"],  # 地震统计区、潜在震源区等
    }

    term_ids = chapter_terms_map.get(chapter_id, [])
    if term_ids:
        guidance.append("\n【相关术语定义】")
        for term_id in term_ids:
            term = get_term(term_id)
            if term:
                guidance.append(f"  • {term['cn']}({term['en']}): {term['definition']}")

    # 5. 相关公式（选择性添加）
    chapter_formulas_map = {
        "chapter8": ["formula1"],  # 反应谱公式
        "chapter9": ["formula2", "formula3"],  # 液化、滑坡公式
    }

    formula_ids = chapter_formulas_map.get(chapter_id, [])
    if formula_ids:
        guidance.append("\n【相关计算公式】")
        for formula_id in formula_ids:
            formula = get_formula(formula_id)
            if formula:
                guidance.append(f"  • {formula['title']}（{formula['reference']}）")
                guidance.append(f"    {formula.get('description', '')}")

    return "\n".join(guidance)


# ============================================================
# 新增：按工作等级获取章节列表
# ============================================================


def get_chapters_by_level(level: str) -> list:
    """
    根据工作等级获取章节列表（替代prompts.py中的同名函数）

    Args:
        level: 工作等级，'I', 'II', 'III'

    Returns:
        章节列表，格式与原prompts.py兼容：
        [
            {
                'id': 'chapter1',
                'title': '1 区域地震活动性和地震构造评价',
                'sections': ['1.1 区域地震活动性评价', ...]
            },
            ...
        ]
    """
    chapter_keys = WORK_LEVEL_CHAPTERS.get(level, WORK_LEVEL_CHAPTERS["II"])
    chapters = []

    for key in chapter_keys:
        info = CHAPTER_STANDARD_MAPPING.get(key)
        if info:
            chapter_num = info.get("chapter_number", "")
            title = info["title"]

            # 构建完整标题
            if chapter_num and chapter_num != "0" and chapter_num != "附录":
                full_title = f"{chapter_num} {title}"
            else:
                full_title = title

            chapters.append({"id": key, "title": full_title, "sections": info.get("sections", [])})

    return chapters


# ============================================================
# 保持原有函数兼容性
# ============================================================


def get_level_requirements(level: str) -> dict:
    """
    获取指定工作等级的技术要求

    Args:
        level: 工作等级，'I', 'II', 'III'

    Returns:
        dict: 工作等级要求
    """
    return WORK_LEVELS.get(level, WORK_LEVELS["II"])


def get_all_chapter_ids() -> List[str]:
    """获取所有章节ID列表"""
    return list(CHAPTER_STANDARD_MAPPING.keys())


# ============================================================
# 非标准术语→标准术语映射
# ============================================================

NON_STANDARD_TERM_MAPPING = {
    "地震危险": "地震危险性分析",
    "活动断裂": "活动构造",
    "可能断层": "能动断层",
    "潜在震源": "潜在震源区",
    "地震安全": "地震安全性评价",
    "场地效应": "场地条件",
    "地震波": "地震动",
    "震害": "地震地质灾害",
    "活断层": "能动断层",
    "地震烈度": "地震影响",
    "断层破裂": "断层错动",
    "地震破坏": "地震地质灾害",
}


# ============================================================
# 合规检查规则
# ============================================================

# 各章节关键词检查规则（从standards_routes硬编码迁移并增强）
CHAPTER_CHECK_KEYWORDS = {
    "preface": {
        "required": ["项目名称", "工作等级", "评价依据", "技术路线"],
        "suggested": ["抗震设防", "工程类型", "经纬度", "工作量"],
    },
    "chapter1": {
        "required": ["区域", "地震", "构造", "断裂", "地震目录"],
        "suggested": ["震级", "震中", "活动性", "台网", "完整性", "地震构造图"],
    },
    "chapter2": {
        "required": ["近场区", "断层", "活动性", "地震构造"],
        "suggested": ["第四纪", "探槽", "地质", "重新定位"],
    },
    "chapter3": {
        "required": ["场址附近", "断层", "能动断层", "活动性鉴定"],
        "suggested": ["遥感", "探槽", "晚更新世", "观测点"],
    },
    "chapter4": {
        "required": ["钻孔", "土层", "波速", "场地类别"],
        "suggested": ["剪切波速", "标贯", "动力性质", "勘测"],
    },
    "chapter5": {"required": ["地震动预测方程", "衰减关系", "适用性"], "suggested": ["基岩", "反应谱", "统计", "验证"]},
    "chapter6": {
        "required": ["确定性", "最大潜在地震", "震源模型"],
        "suggested": ["地震构造区", "发震构造", "最近距离"],
    },
    "chapter7": {
        "required": ["概率", "潜在震源区", "地震活动性参数", "危险性"],
        "suggested": ["统计区", "震级上限", "超越概率", "反应谱"],
    },
    "chapter8": {
        "required": ["场地", "地震动参数", "反应谱", "时程"],
        "suggested": ["土层反应", "峰值加速度", "设计谱", "输入地震动"],
    },
    "chapter9": {"required": ["地质灾害"], "suggested": ["液化", "滑坡", "崩塌", "断层错动", "软土震陷"]},
    "chapter10": {"required": ["结论", "地震动参数", "建议"], "suggested": ["抗震设防", "合规", "超越概率"]},
    "appendix": {"required": ["参考文献"], "suggested": ["附表", "附图"]},
}

# 数值参数校验规则
NUMERIC_CHECK_RULES = {
    "I": {
        "borehole_count": {"min": 5, "unit": "个", "label": "钻孔数量", "clause": "8.2条"},
        "borehole_vs": {"min": 800, "unit": "m/s", "label": "钻孔达到剪切波速", "clause": "8.2条"},
        "region_range": {"min": 150, "unit": "km", "label": "区域范围", "clause": "5.1条"},
        "near_field_range": {"min": 25, "unit": "km", "label": "近场区范围", "clause": "6.1条"},
        "site_nearby_range": {"min": 5, "unit": "km", "label": "场址附近范围", "clause": "7.1条"},
        "time_history_groups": {"min": 20, "unit": "组", "label": "时程组数", "clause": "12.2条"},
        "dynamic_test_points": {"min": 12, "unit": "个", "label": "动力性质测试点", "clause": "8.3条"},
        "fault_observation_points": {"min": 2, "unit": "个", "label": "断层验证观测点", "clause": "7.2条"},
    },
    "II": {
        "borehole_count": {"min": 3, "unit": "个", "label": "钻孔数量", "clause": "8.2条"},
        "borehole_vs": {"min": 500, "unit": "m/s", "label": "钻孔达到剪切波速", "clause": "8.2条"},
        "region_range": {"min": 150, "unit": "km", "label": "区域范围", "clause": "5.1条"},
        "near_field_range": {"min": 25, "unit": "km", "label": "近场区范围", "clause": "6.1条"},
        "time_history_groups": {"min": 10, "unit": "组", "label": "时程组数", "clause": "12.2条"},
        "dynamic_test_points": {"min": 8, "unit": "个", "label": "动力性质测试点", "clause": "8.3条"},
    },
    "III": {
        "region_range": {"min": 150, "unit": "km", "label": "区域范围", "clause": "5.1条"},
        "calculation_spacing": {"max": 2, "unit": "km", "label": "计算场点间距", "clause": "11.5条"},
    },
}

# 附录B必要内容检查项
APPENDIX_B_CHECK_ITEMS = {
    "preface": [
        {"id": "B.1.a", "label": "项目名称", "keywords": ["项目名称", "工程名称"]},
        {"id": "B.1.b", "label": "场址经纬度坐标", "keywords": ["经纬度", "坐标", "经度", "纬度"]},
        {"id": "B.1.c", "label": "抗震设防需求", "keywords": ["抗震设防", "设防类别", "设防分类"]},
        {"id": "B.1.d", "label": "技术任务要求", "keywords": ["技术任务", "评价任务"]},
        {"id": "B.1.e", "label": "工作等级与技术路线", "keywords": ["工作等级", "技术路线", "评价标准"]},
        {"id": "B.1.f", "label": "人员组成与工作量", "keywords": ["人员", "工作量", "起草人"]},
    ],
    "chapter1": [
        {"id": "B.2.a", "label": "地震资料", "keywords": ["地震目录", "地震资料", "地震数据"]},
        {"id": "B.2.b", "label": "区域地震活动空间分布", "keywords": ["空间分布", "震中分布"]},
        {"id": "B.2.c", "label": "区域地震活动时间分布", "keywords": ["时间分布", "活动周期", "活动趋势"]},
        {"id": "B.2.d", "label": "区域现代构造应力场", "keywords": ["应力场", "构造应力"]},
        {"id": "B.2.e", "label": "工程场地历史地震影响", "keywords": ["历史地震", "地震影响", "烈度"]},
        {"id": "B.3.a", "label": "区域地质构造", "keywords": ["地质构造", "构造单元"]},
        {"id": "B.3.b", "label": "区域新构造", "keywords": ["新构造", "新生代"]},
        {"id": "B.3.d", "label": "区域断层活动性", "keywords": ["断层活动", "活动断层", "断裂"]},
        {"id": "B.3.e", "label": "区域地震构造特征", "keywords": ["地震构造", "构造特征"]},
    ],
    "chapter2": [
        {"id": "B.4.a", "label": "近场区地质构造", "keywords": ["近场区", "地质构造"]},
        {"id": "B.4.b", "label": "近场区第四纪构造活动", "keywords": ["第四纪", "构造活动"]},
        {"id": "B.4.c", "label": "近场区主要断层活动性鉴定", "keywords": ["断层", "活动性鉴定"]},
        {"id": "B.4.d", "label": "近场区地震构造特征", "keywords": ["地震构造", "构造特征"]},
    ],
    "chapter3": [
        {"id": "B.5", "label": "场址附近范围断层活动性评价", "keywords": ["场址附近", "断层活动"]},
        {"id": "B.6", "label": "场地活动断层勘查", "keywords": ["活动断层", "勘查"]},
        {"id": "B.7", "label": "能动断层鉴定", "keywords": ["能动断层", "鉴定"]},
    ],
    "chapter4": [
        {"id": "B.11.a", "label": "场地工程地质条件概述", "keywords": ["工程地质", "地质条件"]},
        {"id": "B.11.b", "label": "场地钻孔勘查", "keywords": ["钻孔", "勘查"]},
        {"id": "B.11.c", "label": "钻孔波速测试", "keywords": ["波速", "测试"]},
        {"id": "B.11.d", "label": "工程场地类别", "keywords": ["场地类别"]},
        {"id": "B.11.e", "label": "岩土动力性质试验", "keywords": ["动力性质", "试验"]},
    ],
    "chapter5": [
        {"id": "B.8.a", "label": "地震动预测方程基本原理", "keywords": ["预测方程", "基本原理", "衰减关系"]},
        {"id": "B.8.b", "label": "方程参数确定", "keywords": ["参数确定", "参数选取"]},
        {"id": "B.8.c", "label": "方程适用性论证", "keywords": ["适用性", "论证", "验证"]},
    ],
    "chapter6": [
        {"id": "B.9.a", "label": "区域地震构造环境", "keywords": ["地震构造", "环境"]},
        {"id": "B.9.b", "label": "确定性震源模型", "keywords": ["确定性", "震源模型"]},
        {"id": "B.9.c", "label": "确定性地震危险性计算", "keywords": ["确定性", "危险性计算"]},
    ],
    "chapter7": [
        {"id": "B.10.a", "label": "概率方法概述", "keywords": ["概率", "方法"]},
        {"id": "B.10.b", "label": "潜在震源区划分", "keywords": ["潜在震源区", "划分"]},
        {"id": "B.10.c", "label": "地震活动性参数确定", "keywords": ["活动性参数", "参数确定"]},
        {"id": "B.10.d", "label": "概率地震危险性计算", "keywords": ["概率", "危险性计算"]},
    ],
    "chapter8": [
        {"id": "B.12.a", "label": "基岩输入地震动时程确定", "keywords": ["输入地震动", "时程"]},
        {"id": "B.12.b", "label": "场地土层地震反应分析", "keywords": ["土层反应", "反应分析"]},
        {"id": "B.13", "label": "场地地震动参数确定", "keywords": ["地震动参数", "参数确定"]},
    ],
    "chapter9": [
        {"id": "B.14.a", "label": "断层错动评价", "keywords": ["断层错动"]},
        {"id": "B.14.b", "label": "地震液化评价", "keywords": ["液化", "液化评价"]},
        {"id": "B.14.c", "label": "软土震陷评价", "keywords": ["软土", "震陷"]},
        {"id": "B.14.d", "label": "崩塌滑坡评价", "keywords": ["崩塌", "滑坡"]},
    ],
    "chapter10": [
        {"id": "B.15.1", "label": "地震活动性评价结论", "keywords": ["地震活动", "结论"]},
        {"id": "B.15.2", "label": "地震构造评价结论", "keywords": ["地震构造", "结论"]},
        {"id": "B.15.3", "label": "地震动参数结果", "keywords": ["地震动参数", "结果"]},
        {"id": "B.15.4", "label": "抗震设防建议", "keywords": ["抗震设防", "建议"]},
    ],
}


def get_check_rules(chapter_key: str, work_level: str = "II") -> Dict:
    """
    获取章节合规检查规则

    Args:
        chapter_key: 章节ID
        work_level: 工作等级

    Returns:
        检查规则字典：{keywords, appendix_b_items, numeric_rules, chapter_info}
    """
    rules = {
        "keywords": CHAPTER_CHECK_KEYWORDS.get(chapter_key, {"required": [], "suggested": []}),
        "appendix_b_items": APPENDIX_B_CHECK_ITEMS.get(chapter_key, []),
        "numeric_rules": {},
        "chapter_info": CHAPTER_STANDARD_MAPPING.get(chapter_key, {}),
    }

    # 数值校验规则（根据章节和工作等级过滤）
    level_rules = NUMERIC_CHECK_RULES.get(work_level, {})
    chapter_numeric_map = {
        "chapter4": ["borehole_count", "borehole_vs", "dynamic_test_points"],
        "chapter1": ["region_range"],
        "chapter2": ["near_field_range"],
        "chapter3": ["site_nearby_range", "fault_observation_points"],
        "chapter8": ["time_history_groups"],
        "chapter7": ["calculation_spacing"],
    }
    relevant_params = chapter_numeric_map.get(chapter_key, [])
    for param in relevant_params:
        if param in level_rules:
            rules["numeric_rules"][param] = level_rules[param]

    return rules


def get_numeric_rules(work_level: str = "II") -> Dict:
    """
    获取指定工作等级的全部数值校验规则

    Args:
        work_level: 工作等级

    Returns:
        数值校验规则字典
    """
    return NUMERIC_CHECK_RULES.get(work_level, NUMERIC_CHECK_RULES.get("II", {}))
