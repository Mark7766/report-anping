# -*- coding: utf-8 -*-
from __future__ import annotations

"""
ajepro backend - 服务层 - 合规检查服务
基于 GB 17741-2025 国标的合规检查逻辑

职责：
1. 章节内容关键词检查
2. 附录B必要内容检查
3. 数值参数提取与校验
4. 综合合规评分
"""

import re
from typing import Any, Dict, List, Optional

from lib.gb17741_knowledge import (
    NON_STANDARD_TERM_MAPPING,
    get_check_rules,
    get_numeric_rules,
)
from lib.logger import get_logger

logger = get_logger("compliance_service")


class ComplianceService:
    """合规检查服务"""

    # 数值提取正则模式
    NUMERIC_PATTERNS = {
        "borehole_count": [
            r"(?:布置|布设|共有?|共计|设置)\s*(\d+)\s*个?\s*钻孔",
            r"钻孔\s*(\d+)\s*个",
            r"(\d+)\s*个\s*钻孔",
        ],
        "borehole_vs": [
            r"[剪切波速|波速]\s*[≥>=]*\s*(\d+)\s*m/s",
            r"Vs\s*[≥>=]*\s*(\d+)",
        ],
        "region_range": [
            r"(?:外延|半径)\s*(\d+)\s*km",
            r"(\d+)\s*km\s*(?:范围|外延)",
        ],
        "near_field_range": [
            r"(?:外延|半径)\s*(\d+)\s*km",
        ],
        "site_nearby_range": [
            r"(?:外延|半径)\s*(\d+)\s*km",
        ],
        "time_history_groups": [
            r"(\d+)\s*组\s*(?:时程|地震动)",
            r"(?:选取|选用|共)\s*(\d+)\s*组",
        ],
        "dynamic_test_points": [
            r"(?:测试点|试验点)\s*(?:数量)?\s*(?:不少于)?\s*(\d+)\s*个",
            r"(\d+)\s*个\s*(?:测试点|试验点)",
        ],
        "fault_observation_points": [
            r"(?:观测点|验证点)\s*(?:不少于)?\s*(\d+)\s*个",
            r"(\d+)\s*个\s*(?:观测点|验证点)",
        ],
    }

    @classmethod
    def check_chapter(cls, chapter_key: str, content: str, work_level: str = "II") -> Dict[str, Any]:
        """
        综合检查章节合规性

        Args:
            chapter_key: 章节ID
            content: 章节内容文本
            work_level: 工作等级

        Returns:
            {score, status, passed, warnings, errors, summary}
        """
        if not content or not content.strip():
            return {
                "score": 0,
                "status": "error",
                "passed": [],
                "warnings": [],
                "errors": [
                    {
                        "id": "empty",
                        "label": "章节内容为空",
                        "type": "error",
                        "description": "该章节没有任何内容",
                        "suggestion": "请编写章节内容",
                    }
                ],
                "summary": "章节内容为空",
            }

        rules = get_check_rules(chapter_key, work_level)
        passed = []
        warnings = []
        errors = []

        # 1. 关键词检查
        kw_result = cls._check_keywords(content, rules["keywords"])
        passed.extend(kw_result["passed"])
        warnings.extend(kw_result["warnings"])

        # 2. 附录B必要内容检查
        ab_result = cls._check_appendix_b_items(content, rules["appendix_b_items"])
        passed.extend(ab_result["passed"])
        warnings.extend(ab_result["warnings"])
        errors.extend(ab_result["errors"])

        # 3. 数值参数校验
        if rules["numeric_rules"]:
            num_result = cls._check_numeric_params(content, rules["numeric_rules"])
            passed.extend(num_result["passed"])
            warnings.extend(num_result["warnings"])
            errors.extend(num_result["errors"])

        # 4. 内容长度检查
        length_result = cls._check_content_length(content, chapter_key)
        if length_result:
            warnings.append(length_result)

        # 5. 国标引用检查
        ref_result = cls._check_standard_reference(content)
        if ref_result:
            warnings.append(ref_result)
        else:
            passed.append(
                {"id": "std_ref", "label": "国标条款引用", "type": "pass", "description": "内容中包含国标条款引用"}
            )

        # 计算评分
        total = len(passed) + len(warnings) + len(errors)
        if total == 0:
            score = 50
        else:
            score = round(len(passed) / total * 100)
            # 有错误项时降低评分
            score = max(0, score - len(errors) * 10)
            score = min(100, score)

        if errors:
            status = "error"
        elif warnings:
            status = "warning"
        else:
            status = "pass"

        return {
            "score": score,
            "status": status,
            "passed": passed,
            "warnings": warnings,
            "errors": errors,
            "summary": f"检查完成: {len(passed)}项通过, {len(warnings)}项警告, {len(errors)}项不合规",
        }

    @classmethod
    def check_parameters(cls, content: str, work_level: str = "II") -> List[Dict]:
        """
        检查内容中的数值参数合规性

        Returns:
            参数校验结果列表
        """
        all_rules = get_numeric_rules(work_level)
        results = []

        for param_key, rule in all_rules.items():
            patterns = cls.NUMERIC_PATTERNS.get(param_key, [])
            found = False
            for pattern in patterns:
                if found:
                    break
                matches = list(re.finditer(pattern, content))
                for match in matches:
                    found = True
                    value = int(match.group(1))
                    item = {
                        "param": param_key,
                        "label": rule["label"],
                        "value": value,
                        "unit": rule["unit"],
                        "clause": rule.get("clause", ""),
                        "match_text": match.group(0),
                        "position": match.start(),
                    }
                    if "min" in rule and value < rule["min"]:
                        item["status"] = "error"
                        item["requirement"] = f"≥{rule['min']}{rule['unit']}"
                        item["description"] = (
                            f"{rule['label']}为{value}{rule['unit']}，"
                            f"国标要求≥{rule['min']}{rule['unit']}（GB 17741-2025 第{rule['clause']}）"
                        )
                    elif "max" in rule and value > rule["max"]:
                        item["status"] = "error"
                        item["requirement"] = f"≤{rule['max']}{rule['unit']}"
                        item["description"] = (
                            f"{rule['label']}为{value}{rule['unit']}，"
                            f"国标要求≤{rule['max']}{rule['unit']}（GB 17741-2025 第{rule['clause']}）"
                        )
                    else:
                        item["status"] = "pass"
                        item["description"] = f"{rule['label']}为{value}{rule['unit']}，符合要求"

                    results.append(item)

        return results

    @classmethod
    def get_missing_terms(cls, content: str) -> List[Dict]:
        """
        检测内容中使用的非标准术语

        Returns:
            非标准用语列表 [{original, standard_term, term_id}]
        """
        non_standard_usages = []

        # 使用统一数据源的非标准用语映射（数据源: gb17741_knowledge.py）
        for non_standard, standard in NON_STANDARD_TERM_MAPPING.items():
            if non_standard in content and standard not in content:
                non_standard_usages.append(
                    {
                        "original": non_standard,
                        "standard_term": standard,
                        "suggestion": f'建议将"{non_standard}"替换为标准术语"{standard}"',
                    }
                )

        return non_standard_usages

    # ==================== 内部方法 ====================

    @classmethod
    def _check_keywords(cls, content: str, keywords: Dict) -> Dict:
        """关键词覆盖检查"""
        passed = []
        warnings = []

        for kw in keywords.get("required", []):
            if kw in content:
                passed.append(
                    {
                        "id": f"kw_{kw}",
                        "label": f"关键内容: {kw}",
                        "type": "pass",
                        "description": f'包含必要关键词"{kw}"',
                    }
                )
            else:
                warnings.append(
                    {
                        "id": f"kw_{kw}",
                        "label": f"缺少关键内容: {kw}",
                        "type": "warning",
                        "category": "内容完整性",
                        "description": f'未发现关键词"{kw}"，请确认是否包含相关内容',
                        "suggestion": f"根据GB 17741-2025要求，本章节应包含{kw}相关描述",
                    }
                )

        missing_suggested = [kw for kw in keywords.get("suggested", []) if kw not in content]
        if missing_suggested:
            warnings.append(
                {
                    "id": "kw_suggested",
                    "label": "建议补充内容",
                    "type": "suggestion",
                    "category": "内容完善",
                    "description": f"建议补充: {', '.join(missing_suggested)}",
                    "suggestion": "补充这些内容有助于提高报告的专业性和完整性",
                }
            )

        return {"passed": passed, "warnings": warnings}

    @classmethod
    def _check_appendix_b_items(cls, content: str, items: List[Dict]) -> Dict:
        """附录B必要内容检查"""
        passed = []
        warnings = []
        errors = []

        for item in items:
            found = any(kw in content for kw in item["keywords"])
            if found:
                passed.append(
                    {
                        "id": item["id"],
                        "label": item["label"],
                        "type": "pass",
                        "description": f'附录B要求项"{item["label"]}"已覆盖',
                    }
                )
            else:
                errors.append(
                    {
                        "id": item["id"],
                        "label": f"缺少: {item['label']}",
                        "type": "error",
                        "category": "附录B合规",
                        "description": f'缺少附录B要求的"{item["label"]}"相关内容',
                        "suggestion": f"请补充{item['label']}的描述（附录{item['id']}要求）",
                    }
                )

        return {"passed": passed, "warnings": warnings, "errors": errors}

    @classmethod
    def _check_numeric_params(cls, content: str, rules: Dict) -> Dict:
        """数值参数校验"""
        passed = []
        warnings = []
        errors = []

        for param_key, rule in rules.items():
            patterns = cls.NUMERIC_PATTERNS.get(param_key, [])
            found = False
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    found = True
                    value = int(match.group(1))
                    if "min" in rule and value < rule["min"]:
                        errors.append(
                            {
                                "id": f"num_{param_key}",
                                "label": f"{rule['label']}不足",
                                "type": "error",
                                "category": "参数校验",
                                "description": (
                                    f"{rule['label']}为{value}{rule['unit']}，"
                                    f"国标要求≥{rule['min']}{rule['unit']}（第{rule['clause']}）"
                                ),
                                "suggestion": f"请将{rule['label']}调整至≥{rule['min']}{rule['unit']}",
                                "match_text": match.group(0),
                                "position": match.start(),
                            }
                        )
                    elif "max" in rule and value > rule["max"]:
                        errors.append(
                            {
                                "id": f"num_{param_key}",
                                "label": f"{rule['label']}超标",
                                "type": "error",
                                "category": "参数校验",
                                "description": (
                                    f"{rule['label']}为{value}{rule['unit']}，"
                                    f"国标要求≤{rule['max']}{rule['unit']}（第{rule['clause']}）"
                                ),
                                "suggestion": f"请将{rule['label']}调整至≤{rule['max']}{rule['unit']}",
                                "match_text": match.group(0),
                                "position": match.start(),
                            }
                        )
                    else:
                        passed.append(
                            {
                                "id": f"num_{param_key}",
                                "label": f"{rule['label']}合规",
                                "type": "pass",
                                "description": f"{rule['label']}为{value}{rule['unit']}，符合要求",
                            }
                        )
                    break

            if not found and param_key in ["borehole_count", "time_history_groups"]:
                warnings.append(
                    {
                        "id": f"num_{param_key}_missing",
                        "label": f"未检测到{rule['label']}",
                        "type": "warning",
                        "category": "参数校验",
                        "description": f"未在内容中检测到{rule['label']}的具体数值",
                        "suggestion": f"建议明确标注{rule['label']}（国标第{rule['clause']}要求）",
                    }
                )

        return {"passed": passed, "warnings": warnings, "errors": errors}

    @classmethod
    def _check_content_length(cls, content: str, chapter_key: str) -> Optional[Dict]:
        """内容长度检查"""
        min_lengths = {
            "preface": 300,
            "chapter1": 500,
            "chapter2": 500,
            "chapter3": 400,
            "chapter4": 500,
            "chapter5": 400,
            "chapter6": 400,
            "chapter7": 500,
            "chapter8": 500,
            "chapter9": 300,
            "chapter10": 300,
            "appendix": 100,
        }
        min_len = min_lengths.get(chapter_key, 200)
        if len(content) < min_len:
            return {
                "id": "content_length",
                "label": "内容过短",
                "type": "warning",
                "category": "内容完整性",
                "description": f"章节内容仅{len(content)}字，建议至少{min_len}字",
                "suggestion": "请补充更多技术细节和分析内容",
            }
        return None

    @classmethod
    def _check_standard_reference(cls, content: str) -> Optional[Dict]:
        """检查是否引用国标条款"""
        patterns = [
            r"GB\s*17741",
            r"国标",
            r"标准",
            r"依据.*?第.*?条",
            r"按照.*?规定",
        ]
        for pattern in patterns:
            if re.search(pattern, content):
                return None  # 已引用

        return {
            "id": "std_ref_missing",
            "label": "缺少国标引用",
            "type": "warning",
            "category": "条款引用",
            "description": "内容中未发现GB 17741-2025条款引用",
            "suggestion": '建议在适当位置添加国标条款引用，如"依据GB 17741-2025第X条..."',
        }
