from __future__ import annotations

"""
Integration tests for Phase 2 scripts — show_params, build_chapter_prompt,
render_docx, check_compliance.

All tests run purely from within the Python process (no subprocess) to keep
execution fast, while still exercising the full CLI logic paths.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

FIXTURES_CHAPTERS = REPO_ROOT / "tests" / "fixtures" / "chapters"
PARAMS_EXAMPLE = REPO_ROOT / "params_example.json"


# ============================================================
# show_params
# ============================================================


class TestShowParams:
    """Tests for scripts/show_params.py CLI logic."""

    def test_format_human_ii_contains_key_fields(self) -> None:
        from scripts.show_params import format_params_human

        output = format_params_human("II")
        assert "GB 17741" in output
        assert "name" in output
        assert "level" in output
        assert "exceedance_probs" in output
        assert "chapter" in output.lower()

    def test_format_human_lists_all_three_param_sections(self) -> None:
        from scripts.show_params import format_params_human

        output = format_params_human("II")
        assert "必填参数" in output
        assert "选填参数" in output

    def test_format_json_is_valid_json(self) -> None:
        from scripts.show_params import format_params_json

        raw = format_params_json("II")
        parsed = json.loads(raw)
        assert "params" in parsed
        assert "chapters" in parsed
        assert isinstance(parsed["params"], list)
        assert len(parsed["params"]) == 13

    def test_format_json_level_i_has_chapters(self) -> None:
        from scripts.show_params import format_params_json

        raw = format_params_json("I")
        parsed = json.loads(raw)
        assert len(parsed["chapters"]) > 0

    def test_param_spec_has_13_entries(self) -> None:
        from scripts.show_params import PARAM_SPEC

        assert len(PARAM_SPEC) == 13

    def test_all_required_params_have_example(self) -> None:
        from scripts.show_params import PARAM_SPEC

        for p in PARAM_SPEC:
            if p["required"]:
                assert p["example"] != "" or p["example"] == 0 or p["example"] == {}


# ============================================================
# build_chapter_prompt
# ============================================================


class TestBuildChapterPrompt:
    """Tests for scripts/build_chapter_prompt.py CLI logic."""

    def _load_params(self) -> dict:
        return json.loads(PARAMS_EXAMPLE.read_text(encoding="utf-8"))

    def test_known_chapter_returns_long_prompt(self) -> None:
        from lib.gb17741_knowledge import get_chapters_by_level
        from lib.prompts.chapter_prompts import build_chapter_prompt
        from scripts.build_chapter_prompt import find_chapter

        params = self._load_params()
        level = params.get("level", "II")
        chapters = get_chapters_by_level(level)
        chapter = find_chapter(chapters, "chapter4")
        assert chapter is not None

        prompt = build_chapter_prompt(
            project_data=params,
            chapter=chapter,
            chapter_index=3,
            total_chapters=len(chapters),
        )
        assert len(prompt) > 100
        assert "GB 17741" in prompt or "工程场地" in prompt

    def test_preface_chapter_prompt(self) -> None:
        from lib.gb17741_knowledge import get_chapters_by_level
        from lib.prompts.chapter_prompts import build_chapter_prompt
        from scripts.build_chapter_prompt import find_chapter

        params = self._load_params()
        chapters = get_chapters_by_level("II")
        chapter = find_chapter(chapters, "preface")
        assert chapter is not None

        prompt = build_chapter_prompt(params, chapter, 0, len(chapters))
        assert len(prompt) > 100

    def test_list_chapters_for_all_levels(self) -> None:
        from lib.gb17741_knowledge import get_chapters_by_level

        for level in ("I", "II", "III"):
            chapters = get_chapters_by_level(level)
            assert len(chapters) > 0
            for ch in chapters:
                assert "id" in ch and "title" in ch

    def test_find_chapter_returns_none_for_unknown(self) -> None:
        from scripts.build_chapter_prompt import find_chapter

        assert find_chapter([], "nonexistent") is None


# ============================================================
# render_docx
# ============================================================


class TestRenderDocx:
    """Integration tests for scripts/render_docx.py render() function."""

    def test_render_creates_docx_file(self, tmp_path: Path) -> None:
        from scripts.render_docx import render

        params = json.loads(PARAMS_EXAMPLE.read_text(encoding="utf-8"))
        out = tmp_path / "report.docx"
        render(params=params, chapters_dir=FIXTURES_CHAPTERS, out_path=out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_render_docx_is_nonzero_for_empty_chapters(self, tmp_path: Path) -> None:
        """render() with empty chapters dir should still produce a valid docx."""
        from scripts.render_docx import render

        empty_dir = tmp_path / "empty_chapters"
        empty_dir.mkdir()
        params = json.loads(PARAMS_EXAMPLE.read_text(encoding="utf-8"))
        out = tmp_path / "empty_report.docx"
        render(params=params, chapters_dir=empty_dir, out_path=out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_render_output_in_nested_dir(self, tmp_path: Path) -> None:
        """out_path parent is created automatically."""
        from scripts.render_docx import render

        params = json.loads(PARAMS_EXAMPLE.read_text(encoding="utf-8"))
        out = tmp_path / "exports" / "subdir" / "report.docx"
        render(params=params, chapters_dir=FIXTURES_CHAPTERS, out_path=out)
        assert out.exists()


# ============================================================
# check_compliance
# ============================================================


class TestCheckCompliance:
    """Tests for scripts/check_compliance.py logic."""

    def test_check_chapters_returns_list(self) -> None:
        from scripts.check_compliance import check_chapters

        results = check_chapters(FIXTURES_CHAPTERS, "II")
        assert isinstance(results, list)
        assert len(results) == 3  # preface, chapter1, chapter8

    def test_each_result_has_required_keys(self) -> None:
        from scripts.check_compliance import check_chapters

        for r in check_chapters(FIXTURES_CHAPTERS, "II"):
            assert "score" in r
            assert "status" in r
            assert "chapter_key" in r
            assert "file" in r

    def test_chapter_keys_are_valid(self) -> None:
        from scripts.check_compliance import _VALID_KEYS, check_chapters

        for r in check_chapters(FIXTURES_CHAPTERS, "II"):
            assert r["chapter_key"] in _VALID_KEYS

    def test_stem_to_chapter_key_mapping(self) -> None:
        from scripts.check_compliance import _stem_to_chapter_key

        assert _stem_to_chapter_key("01_preface") == "preface"
        assert _stem_to_chapter_key("02_chapter1") == "chapter1"
        assert _stem_to_chapter_key("chapter8") == "chapter8"
        assert _stem_to_chapter_key("03_chapter8") == "chapter8"
        assert _stem_to_chapter_key("unknown_file") is None

    def test_format_human_output(self) -> None:
        from scripts.check_compliance import check_chapters, format_human

        results = check_chapters(FIXTURES_CHAPTERS, "II")
        output = format_human(results, "II")
        assert "GB 17741" in output
        assert "合规检查报告" in output
        assert "综合评分" in output

    def test_format_json_is_valid(self) -> None:
        from scripts.check_compliance import check_chapters, format_json_output

        results = check_chapters(FIXTURES_CHAPTERS, "II")
        raw = format_json_output(results, "II")
        parsed = json.loads(raw)
        assert "work_level" in parsed
        assert "chapter_count" in parsed
        assert isinstance(parsed["chapters"], list)

    def test_empty_dir_returns_empty_results(self, tmp_path: Path) -> None:
        from scripts.check_compliance import check_chapters

        empty = tmp_path / "chapters"
        empty.mkdir()
        results = check_chapters(empty, "II")
        assert results == []
