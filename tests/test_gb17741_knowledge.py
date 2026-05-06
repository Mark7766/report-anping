from __future__ import annotations

"""
Tests for lib/gb17741_knowledge.py — pure-function knowledge base queries.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.gb17741_knowledge import (
    CHAPTER_STANDARD_MAPPING,
    NON_STANDARD_TERM_MAPPING,
    STANDARD_INFO,
    WORK_LEVELS,
    get_all_chapter_ids,
    get_all_formulas,
    get_all_tables,
    get_all_terms,
    get_appendix_b,
    get_appendix_b_section,
    get_chapter_standard_guidance,
    get_chapters_by_level,
    get_check_rules,
    get_formula,
    get_level_requirements,
    get_numeric_rules,
    get_table,
    get_term,
    search_term,
)


class TestStandardInfo:
    """Tests for top-level constant STANDARD_INFO."""

    def test_standard_code_present(self) -> None:
        assert "GB 17741" in STANDARD_INFO["code"]

    def test_standard_name_present(self) -> None:
        assert "地震安全性评价" in STANDARD_INFO["name"]


class TestWorkLevels:
    """Tests for WORK_LEVELS constant and helpers."""

    def test_three_levels_exist(self) -> None:
        assert set(WORK_LEVELS.keys()) >= {"I", "II", "III"}

    def test_get_level_requirements_ii(self) -> None:
        req = get_level_requirements("II")
        assert isinstance(req, dict)
        assert "target" in req

    def test_get_level_requirements_unknown_falls_back(self) -> None:
        req = get_level_requirements("X")
        # Should return II defaults rather than crash
        assert isinstance(req, dict)


class TestTerms:
    """Tests for term query functions."""

    def test_get_all_terms_returns_dict(self) -> None:
        terms = get_all_terms()
        assert isinstance(terms, dict)
        assert len(terms) > 0

    def test_get_term_known(self) -> None:
        terms = get_all_terms()
        first_id = next(iter(terms))
        term = get_term(first_id)
        assert term is not None
        assert "cn" in term

    def test_get_term_unknown_returns_none(self) -> None:
        assert get_term("nonexistent_term_id") is None

    def test_search_term_returns_list(self) -> None:
        results = search_term("地震")
        assert isinstance(results, list)


class TestTables:
    """Tests for table query functions."""

    def test_get_all_tables_returns_dict(self) -> None:
        tables = get_all_tables()
        assert isinstance(tables, dict)

    def test_get_table_unknown_returns_none(self) -> None:
        assert get_table("nonexistent_table_9999") is None


class TestFormulas:
    """Tests for formula query functions."""

    def test_get_all_formulas_returns_dict(self) -> None:
        formulas = get_all_formulas()
        assert isinstance(formulas, dict)

    def test_get_formula_unknown_returns_none(self) -> None:
        assert get_formula("nonexistent_formula") is None


class TestAppendixB:
    """Tests for appendix B query functions."""

    def test_get_appendix_b_returns_dict(self) -> None:
        appendix = get_appendix_b()
        assert isinstance(appendix, dict)

    def test_get_appendix_b_section_unknown_returns_none(self) -> None:
        assert get_appendix_b_section("Z.999") is None


class TestChapterStandardMapping:
    """Tests for chapter mapping and guidance."""

    def test_mapping_has_known_chapters(self) -> None:
        assert "chapter1" in CHAPTER_STANDARD_MAPPING
        assert "chapter8" in CHAPTER_STANDARD_MAPPING
        assert "preface" in CHAPTER_STANDARD_MAPPING

    def test_get_all_chapter_ids(self) -> None:
        ids = get_all_chapter_ids()
        assert isinstance(ids, list)
        assert "chapter1" in ids

    def test_get_chapter_standard_guidance_returns_dict(self) -> None:
        result = get_chapter_standard_guidance("chapter1")
        assert isinstance(result, dict)
        assert set(result.keys()) == {"technical", "report", "clauses"}

    def test_get_chapter_standard_guidance_unknown_returns_empty(self) -> None:
        result = get_chapter_standard_guidance("nonexistent")
        assert result == {}


class TestChaptersByLevel:
    """Tests for get_chapters_by_level."""

    def test_returns_list(self) -> None:
        chapters = get_chapters_by_level("II")
        assert isinstance(chapters, list)
        assert len(chapters) > 0

    def test_each_chapter_has_id_and_title(self) -> None:
        for ch in get_chapters_by_level("II"):
            assert "id" in ch
            assert "title" in ch


class TestCheckRules:
    """Tests for get_check_rules."""

    def test_returns_expected_keys(self) -> None:
        rules = get_check_rules("chapter1", "II")
        assert "keywords" in rules
        assert "appendix_b_items" in rules
        assert "numeric_rules" in rules
        assert "chapter_info" in rules

    def test_keywords_has_required(self) -> None:
        rules = get_check_rules("chapter1", "II")
        assert isinstance(rules["keywords"].get("required"), list)


class TestNumericRules:
    """Tests for get_numeric_rules."""

    def test_returns_dict(self) -> None:
        rules = get_numeric_rules("II")
        assert isinstance(rules, dict)
        assert len(rules) > 0

    def test_unknown_level_falls_back(self) -> None:
        rules = get_numeric_rules("X")
        assert isinstance(rules, dict)


class TestNonStandardTermMapping:
    """Tests for NON_STANDARD_TERM_MAPPING constant."""

    def test_mapping_is_non_empty(self) -> None:
        assert len(NON_STANDARD_TERM_MAPPING) > 0

    def test_values_are_standard_terms(self) -> None:
        for non_std, std in NON_STANDARD_TERM_MAPPING.items():
            assert isinstance(non_std, str) and len(non_std) > 0
            assert isinstance(std, str) and len(std) > 0
