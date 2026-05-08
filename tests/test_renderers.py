from __future__ import annotations

"""Unit tests for pure-Python renderer helpers.

Covers the stateless parser and numbering tracker classes that do not
require a live python-docx Document object.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))


# ============================================================
# MarkdownTableParser
# ============================================================


class TestMarkdownTableParser:
    """Unit tests for lib/table_renderer.MarkdownTableParser."""

    def _parse(self, text: str):
        from lib.table_renderer import MarkdownTableParser

        lines = text.strip().splitlines()
        return MarkdownTableParser.parse(lines)

    def test_parse_simple_table(self) -> None:
        md = "| A | B | C |\n|---|---|---|\n| 1 | 2 | 3 |"
        result = self._parse(md)
        assert result is not None
        assert result["headers"] == ["A", "B", "C"]
        assert result["rows"] == [["1", "2", "3"]]

    def test_parse_returns_none_for_empty_input(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        assert MarkdownTableParser.parse([]) is None

    def test_parse_returns_none_for_no_header(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        assert MarkdownTableParser.parse(["no pipe here"]) is None

    def test_parse_alignments_center(self) -> None:
        md = "| H |\n|:---:|\n| v |"
        result = self._parse(md)
        assert result["alignments"] == ["center"]

    def test_parse_alignments_right(self) -> None:
        md = "| H |\n|---:|\n| v |"
        result = self._parse(md)
        assert result["alignments"] == ["right"]

    def test_parse_alignments_left_explicit(self) -> None:
        md = "| H |\n|:---|\n| v |"
        result = self._parse(md)
        assert result["alignments"] == ["left"]

    def test_parse_alignments_default_left(self) -> None:
        md = "| H |\n|---|\n| v |"
        result = self._parse(md)
        assert result["alignments"] == ["left"]

    def test_parse_multiple_data_rows(self) -> None:
        md = "| X | Y |\n|---|---|\n| a | b |\n| c | d |"
        result = self._parse(md)
        assert len(result["rows"]) == 2
        assert result["rows"][1] == ["c", "d"]

    def test_parse_strips_cell_whitespace(self) -> None:
        md = "|  Name  |  Value  |\n|--------|--------|\n|  foo   |  42    |"
        result = self._parse(md)
        assert result["headers"] == ["Name", "Value"]
        assert result["rows"][0] == ["foo", "42"]

    def test_parse_cells_without_leading_pipe(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        cells = MarkdownTableParser._parse_cells("| a | b | c |")
        assert cells == ["a", "b", "c"]

    def test_parse_mixed_alignment_columns(self) -> None:
        md = "| L | C | R |\n|:--|:--:|--:|\n| v | v | v |"
        result = self._parse(md)
        assert result["alignments"] == ["left", "center", "right"]

    def test_is_numeric_integer(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        assert MarkdownTableParser.is_numeric("42") is True

    def test_is_numeric_float(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        assert MarkdownTableParser.is_numeric("3.14") is True

    def test_is_numeric_with_comma(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        assert MarkdownTableParser.is_numeric("1,234") is True

    def test_is_numeric_with_percent(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        assert MarkdownTableParser.is_numeric("5%") is True

    def test_is_numeric_range_tilde(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        assert MarkdownTableParser.is_numeric("0.05~0.10") is True

    def test_is_numeric_false_for_text(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        assert MarkdownTableParser.is_numeric("hello") is False

    def test_is_numeric_false_for_empty(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        assert MarkdownTableParser.is_numeric("") is False

    def test_is_numeric_false_for_none(self) -> None:
        from lib.table_renderer import MarkdownTableParser

        assert MarkdownTableParser.is_numeric(None) is False  # type: ignore[arg-type]


# ============================================================
# TableNumbering
# ============================================================


class TestTableNumbering:
    """Unit tests for lib/table_renderer.TableNumbering."""

    def test_first_number_in_chapter(self) -> None:
        from lib.table_renderer import TableNumbering

        tn = TableNumbering()
        tn.set_chapter(3)
        assert tn.next_number() == "3-1"

    def test_sequential_numbers_same_chapter(self) -> None:
        from lib.table_renderer import TableNumbering

        tn = TableNumbering()
        tn.set_chapter(2)
        assert tn.next_number() == "2-1"
        assert tn.next_number() == "2-2"

    def test_chapter_change_resets_counter(self) -> None:
        from lib.table_renderer import TableNumbering

        tn = TableNumbering()
        tn.set_chapter(1)
        tn.next_number()
        tn.set_chapter(2)
        assert tn.next_number() == "2-1"

    def test_string_chapter(self) -> None:
        from lib.table_renderer import TableNumbering

        tn = TableNumbering()
        tn.set_chapter("前")
        assert tn.next_number() == "前-1"

    def test_registry_lookup(self) -> None:
        from lib.table_renderer import TableNumbering

        tn = TableNumbering()
        tn.set_chapter(4)
        tn.next_number(table_id="t_soil")
        assert tn.get_number("t_soil") == "4-1"

    def test_registry_unknown_id(self) -> None:
        from lib.table_renderer import TableNumbering

        tn = TableNumbering()
        assert tn.get_number("nonexistent") is None

    def test_zero_chapter_defaults_to_4(self) -> None:
        from lib.table_renderer import TableNumbering

        tn = TableNumbering()
        tn.chapter = 0  # force invalid state
        num = tn.next_number()
        assert num.startswith("4-")

    def test_same_chapter_set_twice_no_reset(self) -> None:
        from lib.table_renderer import TableNumbering

        tn = TableNumbering()
        tn.set_chapter(5)
        tn.next_number()
        tn.set_chapter(5)  # same chapter — counter must NOT reset
        assert tn.next_number() == "5-2"

    def test_set_chapter_zero_clamped_to_4(self) -> None:
        from lib.table_renderer import TableNumbering

        tn = TableNumbering()
        tn.set_chapter(0)  # triggers internal warning → clamped to 4
        assert tn.next_number() == "4-1"

    def test_next_number_warning_when_chapter_zero(self) -> None:
        from lib.table_renderer import TableNumbering

        tn = TableNumbering()
        tn.chapter = 0  # force invalid state bypassing set_chapter guard
        tn.table_count = 0
        num = tn.next_number()
        assert num == "4-1"


# ============================================================
# FigureNumbering
# ============================================================


class TestFigureNumbering:
    """Unit tests for lib/figure_renderer.FigureNumbering."""

    def test_first_figure_in_chapter(self) -> None:
        from lib.figure_renderer import FigureNumbering

        fn = FigureNumbering()
        fn.set_chapter(3)
        assert fn.next_number() == "3-1"

    def test_sequential_figures(self) -> None:
        from lib.figure_renderer import FigureNumbering

        fn = FigureNumbering()
        fn.set_chapter(2)
        assert fn.next_number() == "2-1"
        assert fn.next_number() == "2-2"

    def test_chapter_change_resets_counter(self) -> None:
        from lib.figure_renderer import FigureNumbering

        fn = FigureNumbering()
        fn.set_chapter(1)
        fn.next_number()
        fn.set_chapter(2)
        assert fn.next_number() == "2-1"

    def test_string_chapter_appendix(self) -> None:
        from lib.figure_renderer import FigureNumbering

        fn = FigureNumbering()
        fn.set_chapter("附A")
        assert fn.next_number() == "附A-1"

    def test_registry_with_id(self) -> None:
        from lib.figure_renderer import FigureNumbering

        fn = FigureNumbering()
        fn.set_chapter(4)
        fn.next_number(figure_id="fig_site")
        assert fn.get_number("fig_site") == "4-1"

    def test_registry_unknown_id(self) -> None:
        from lib.figure_renderer import FigureNumbering

        fn = FigureNumbering()
        assert fn.get_number("missing") is None

    def test_zero_chapter_defaults_to_4(self) -> None:
        from lib.figure_renderer import FigureNumbering

        fn = FigureNumbering()
        fn.chapter = 0
        num = fn.next_number()
        assert num.startswith("4-")

    def test_same_chapter_set_twice_no_reset(self) -> None:
        from lib.figure_renderer import FigureNumbering

        fn = FigureNumbering()
        fn.set_chapter(6)
        fn.next_number()
        fn.set_chapter(6)
        assert fn.next_number() == "6-2"

    def test_set_chapter_zero_clamped_to_4(self) -> None:
        from lib.figure_renderer import FigureNumbering

        fn = FigureNumbering()
        fn.set_chapter(0)  # triggers internal warning → clamped to 4
        assert fn.next_number() == "4-1"

    def test_next_number_warning_when_chapter_zero_bypassed(self) -> None:
        from lib.figure_renderer import FigureNumbering

        fn = FigureNumbering()
        fn.chapter = 0  # force invalid state
        fn.figure_count = 0
        num = fn.next_number()
        assert num == "4-1"


# ============================================================
# ChapterNumberingTracker
# ============================================================


class TestChapterNumberingTracker:
    """Unit tests for lib/figure_renderer.ChapterNumberingTracker."""

    def test_detect_numeric_chapter(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        result = tracker.detect_initial_chapter("# 3 场地地质条件\n## 3.1 地层\n内容")
        assert result == 3

    def test_detect_chapter_with_chinese_prefix(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        result = tracker.detect_initial_chapter("# 第4章 地震动参数")
        assert result == 4

    def test_detect_special_chapter_preface(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        result = tracker.detect_initial_chapter("# 前言\n内容")
        assert result == 0
        assert tracker.current_chapter_text == "前"

    def test_detect_special_chapter_appendix_b(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        result = tracker.detect_initial_chapter("# 附录B\n内容")
        assert result == 0
        assert tracker.current_chapter_text == "附B"

    def test_detect_no_heading_returns_default_4(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        result = tracker.detect_initial_chapter("只有普通段落文本，没有标题")
        assert result == 4

    def test_detect_skips_h2_headings(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        result = tracker.detect_initial_chapter("## 3.1 小节")  # H2, not H1
        assert result == 4  # no H1 found → default

    def test_initialize_from_content(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        tracker.initialize_from_content("# 5 场地土层\n内容")
        assert tracker.current_chapter == 5

    def test_update_from_heading_numeric(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        tracker.update_from_heading("3 场地地质", level=1)
        assert tracker.current_chapter == 3

    def test_update_from_heading_special(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        tracker.update_from_heading("前言", level=1)
        assert tracker.current_chapter == 0
        assert tracker.current_chapter_text == "前"

    def test_update_from_heading_level2_ignored(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        tracker.update_from_heading("3.1 子节", level=2)
        assert tracker.current_chapter == 0  # unchanged

    def test_get_current_chapter_returns_text_for_special(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        tracker.current_chapter = 0
        tracker.current_chapter_text = "前"
        assert tracker.get_current_chapter() == "前"

    def test_get_current_chapter_zero_without_text_returns_default(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        tracker.current_chapter = 0
        tracker.current_chapter_text = None
        assert tracker.get_current_chapter() == 4

    def test_get_current_chapter_numeric(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        tracker.current_chapter = 7
        assert tracker.get_current_chapter() == 7

    def test_update_from_heading_unmatched_increments(self) -> None:
        from lib.figure_renderer import ChapterNumberingTracker

        tracker = ChapterNumberingTracker()
        tracker.current_chapter = 3
        # A heading that doesn't match the numeric or special-chapter pattern
        tracker.update_from_heading("Introduction", level=1)
        assert tracker.current_chapter == 4  # incremented by 1
