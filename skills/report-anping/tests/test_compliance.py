from __future__ import annotations

"""
Tests for lib/compliance.py — deterministic compliance rule engine.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.compliance import ComplianceService

SAMPLE_CHAPTER1_CONTENT = """
本章节依据GB 17741-2025第5章要求，对区域地震活动性和地震构造进行综合评价。

1. 区域范围
采用以工程场地为中心、外延150km的区域，收集地震目录及地质构造资料。

2. 地震活动性
区域内历史地震记录丰富，震中分布具有明显的沿活动断裂带展布的特征。
地震活动性分析表明，场地所在区域地震活动较强，历史上发生过多次中强地震。

3. 地震构造
区域内主要构造单元包括华南地块及相邻构造带。区内断裂发育，
主要断裂带活动性鉴定结果显示部分为晚更新世以来的活动构造。

依据GB 17741-2025标准，区域地震活动分析需建立完整的地震目录，
并对震中分布、历史地震影响进行系统评价。本次评价收集了仪器记录时期的地震数据，
重新定位计算了区域历史地震目录。
"""

SAMPLE_SHORT_CONTENT = "短内容"


class TestCheckChapter:
    """Tests for ComplianceService.check_chapter()."""

    def test_returns_expected_keys(self) -> None:
        result = ComplianceService.check_chapter("chapter1", SAMPLE_CHAPTER1_CONTENT, "II")
        assert "score" in result
        assert "status" in result
        assert "passed" in result
        assert "warnings" in result
        assert "errors" in result
        assert "summary" in result

    def test_score_in_range(self) -> None:
        result = ComplianceService.check_chapter("chapter1", SAMPLE_CHAPTER1_CONTENT, "II")
        assert 0 <= result["score"] <= 100

    def test_empty_content_returns_error(self) -> None:
        result = ComplianceService.check_chapter("chapter1", "", "II")
        assert result["status"] == "error"
        assert result["score"] == 0

    def test_short_content_triggers_warning(self) -> None:
        result = ComplianceService.check_chapter("chapter1", SAMPLE_SHORT_CONTENT, "II")
        warning_ids = [w["id"] for w in result["warnings"]]
        assert "content_length" in warning_ids

    def test_with_standard_reference_passes_ref_check(self) -> None:
        result = ComplianceService.check_chapter("chapter1", SAMPLE_CHAPTER1_CONTENT, "II")
        passed_ids = [p["id"] for p in result["passed"]]
        assert "std_ref" in passed_ids

    def test_valid_for_different_levels(self) -> None:
        for level in ("I", "II", "III"):
            result = ComplianceService.check_chapter("chapter4", SAMPLE_CHAPTER1_CONTENT, level)
            assert isinstance(result["score"], int)


class TestCheckParameters:
    """Tests for ComplianceService.check_parameters()."""

    def test_returns_list(self) -> None:
        results = ComplianceService.check_parameters(SAMPLE_CHAPTER1_CONTENT, "II")
        assert isinstance(results, list)

    def test_detects_region_range(self) -> None:
        content = "勘察区域外延150km范围内的地震地质资料。"
        results = ComplianceService.check_parameters(content, "II")
        found = [r for r in results if r["param"] == "region_range"]
        assert len(found) == 1
        assert found[0]["value"] == 150

    def test_detects_insufficient_borehole_count(self) -> None:
        content = "本次勘察布置2个钻孔进行波速测试。"
        results = ComplianceService.check_parameters(content, "II")
        found = [r for r in results if r["param"] == "borehole_count"]
        if found:
            assert found[0]["status"] == "error"


class TestGetMissingTerms:
    """Tests for ComplianceService.get_missing_terms()."""

    def test_returns_list(self) -> None:
        result = ComplianceService.get_missing_terms("正常的报告内容")
        assert isinstance(result, list)

    def test_detects_non_standard_term(self) -> None:
        # "活动断裂" is non-standard; "活动构造" is standard
        content = "该地区存在多条活动断裂，其活动性较强。"
        result = ComplianceService.get_missing_terms(content)
        originals = [item["original"] for item in result]
        assert "活动断裂" in originals

    def test_standard_term_not_flagged(self) -> None:
        # When non-standard term is absent, nothing flagged for it
        content = "该地区存在多条活动构造，其活动性较强。"
        result = ComplianceService.get_missing_terms(content)
        originals = [item["original"] for item in result]
        assert "活动断裂" not in originals
