from __future__ import annotations

"""
scripts/show_params.py — 输出 13 个安评参数说明 + 当前级别章节列表

用法:
    python scripts/show_params.py
    python scripts/show_params.py --level I
    python scripts/show_params.py --format json
"""

import argparse
import json
import sys
from pathlib import Path

# 确保 cwd = 技能根时 lib/ 可寻址
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.gb17741_knowledge import STANDARD_INFO, get_chapters_by_level

# ============================================================
# 13 个参数的元数据
# ============================================================

PARAM_SPEC: list[dict] = [
    {
        "key": "name",
        "label": "项目名称",
        "description": "工程项目的完整名称",
        "example": "某核电站工程地震安全性评价",
        "required": True,
        "type": "str",
    },
    {
        "key": "level",
        "label": "工作等级",
        "description": "GB 17741-2025 规定的安评工作等级：I（最高）/ II（常规）/ III（最低）",
        "example": "II",
        "required": True,
        "type": "str",
        "choices": ["I", "II", "III"],
    },
    {
        "key": "engineering_type",
        "label": "工程类型",
        "description": "建设工程的功能类型",
        "example": "核电站",
        "required": True,
        "type": "str",
    },
    {
        "key": "location",
        "label": "项目地址",
        "description": "工程场地所在省市县",
        "example": "广东省深圳市宝安区",
        "required": True,
        "type": "str",
    },
    {
        "key": "coordinate_lon",
        "label": "经度",
        "description": "工程场地东经坐标（度，小数格式）",
        "example": "114.06",
        "required": True,
        "type": "float",
    },
    {
        "key": "coordinate_lat",
        "label": "纬度",
        "description": "工程场地北纬坐标（度，小数格式）",
        "example": "22.54",
        "required": True,
        "type": "float",
    },
    {
        "key": "building_height",
        "label": "建筑高度",
        "description": "主体建筑高度（米）",
        "example": 80,
        "required": True,
        "type": "float",
    },
    {
        "key": "construction_unit",
        "label": "建设单位",
        "description": "委托方/业主单位全称",
        "example": "某能源集团有限公司",
        "required": True,
        "type": "str",
    },
    {
        "key": "survey_unit",
        "label": "勘察单位",
        "description": "负责场地勘察的单位全称",
        "example": "某地质勘察院",
        "required": False,
        "type": "str",
    },
    {
        "key": "evaluation_unit",
        "label": "评价单位",
        "description": "负责安评的资质单位全称",
        "example": "某地震安全性评价机构",
        "required": True,
        "type": "str",
    },
    {
        "key": "exceedance_probs",
        "label": "超越概率设置",
        "description": (
            "需计算的超越概率水准，分 50 年和 100 年两档，各为整数百分比列表。"
            "常用设置：50年[63,10,5,2]、100年[10,5,2,1]"
        ),
        "example": {"50_year": [63, 10, 5, 2], "100_year": [10, 5, 2, 1]},
        "required": True,
        "type": "dict",
    },
    {
        "key": "report_date",
        "label": "报告日期",
        "description": "报告编制年月，格式 YYYY-MM",
        "example": "2025-06",
        "required": False,
        "type": "str",
    },
    {
        "key": "extra_notes",
        "label": "补充说明",
        "description": "其他需要在报告中体现的特殊要求或背景信息",
        "example": "",
        "required": False,
        "type": "str",
    },
]


# ============================================================
# 格式化输出
# ============================================================


def format_params_human(level: str) -> str:
    """将参数规格和章节列表格式化为人类可读文本。"""
    lines: list[str] = []

    lines.append(f"=== {STANDARD_INFO['code']} 安评参数清单 ===")
    lines.append(f"标准名称: {STANDARD_INFO['name']}")
    lines.append("")

    # 参数表
    lines.append("【必填参数】")
    for p in PARAM_SPEC:
        if p["required"]:
            choices_str = f"  可选值: {p['choices']}" if "choices" in p else ""
            lines.append(f"  {p['key']} ({p['label']}): {p['description']}")
            if choices_str:
                lines.append(f"      {choices_str.strip()}")
            lines.append(f"      示例: {p['example']}")

    lines.append("")
    lines.append("【选填参数】")
    for p in PARAM_SPEC:
        if not p["required"]:
            lines.append(f"  {p['key']} ({p['label']}): {p['description']}")
            lines.append(f"      示例: {p['example']}")

    # 章节结构
    lines.append("")
    lines.append(f"=== {level} 级安评报告章节结构 ===")
    chapters = get_chapters_by_level(level)
    for idx, ch in enumerate(chapters, 1):
        lines.append(f"  {idx}. [{ch['id']}] {ch['title']}")
        for sec in ch.get("sections", []):
            lines.append(f"       - {sec}")

    return "\n".join(lines)


def format_params_json(level: str) -> str:
    """将参数规格和章节列表序列化为 JSON 字符串。"""
    payload = {
        "standard": STANDARD_INFO,
        "params": PARAM_SPEC,
        "chapters": get_chapters_by_level(level),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ============================================================
# CLI 入口
# ============================================================


def main() -> None:
    """CLI 入口：解析参数后输出到 stdout。"""
    parser = argparse.ArgumentParser(description="输出 GB 17741-2025 安评参数清单与报告章节结构")
    parser.add_argument(
        "--level",
        choices=["I", "II", "III"],
        default="II",
        help="安评工作等级，默认 II",
    )
    parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="输出格式：human（人类可读）或 json，默认 human",
    )
    args = parser.parse_args()

    if args.format == "json":
        print(format_params_json(args.level))
    else:
        print(format_params_human(args.level))


if __name__ == "__main__":
    main()
