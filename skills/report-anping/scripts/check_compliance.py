from __future__ import annotations

"""
scripts/check_compliance.py — 对已生成的章节 markdown 执行 GB 17741-2025 合规检查

从 chapters/ 目录读取每个章节的 .md 内容，调用 lib/compliance.ComplianceService
逐章检查，汇总输出合规报告到 stdout。

用法:
    python scripts/check_compliance.py --chapters chapters/
    python scripts/check_compliance.py --chapters chapters/ --level I
    python scripts/check_compliance.py --chapters chapters/ --format json
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.compliance import ComplianceService
from lib.logger import get_logger

logger = get_logger("check_compliance")

# ============================================================
# 章节文件名 → chapter_key 映射
# ============================================================

# 文件名中可能包含: "01_chapter1.md", "chapter1.md", "preface.md" 等
_STEM_TO_KEY_RE = re.compile(
    r"(?:^\d+[_\-]?)?"  # optional leading digits
    r"(preface|chapter\d+|appendix)",
    re.IGNORECASE,
)

_VALID_KEYS = {
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
}


def _stem_to_chapter_key(stem: str) -> str | None:
    """Extract a valid chapter_key from a file stem, or return None."""
    m = _STEM_TO_KEY_RE.search(stem.lower())
    if m:
        key = m.group(1).lower()
        return key if key in _VALID_KEYS else None
    return None


# ============================================================
# Core check function
# ============================================================


def check_chapters(chapters_dir: Path, work_level: str) -> list[dict]:
    """
    检查 chapters_dir 下所有 .md 文件，返回每章的检查结果列表。

    Args:
        chapters_dir: 包含章节 .md 文件的目录
        work_level: 工作等级 I/II/III

    Returns:
        list of {file, chapter_key, score, status, passed, warnings, errors, summary}
    """
    md_files = sorted(chapters_dir.glob("*.md"))
    results: list[dict] = []

    for md_file in md_files:
        chapter_key = _stem_to_chapter_key(md_file.stem)
        if chapter_key is None:
            logger.warning(f"无法识别章节 ID，跳过: {md_file.name}")
            continue

        content = md_file.read_text(encoding="utf-8")
        result = ComplianceService.check_chapter(chapter_key, content, work_level)
        result["file"] = md_file.name
        result["chapter_key"] = chapter_key
        results.append(result)
        logger.info(f"[{md_file.name}] 得分={result['score']}, 状态={result['status']}")

    return results


# ============================================================
# 格式化输出
# ============================================================


def _status_icon(status: str) -> str:
    icons = {"pass": "✅", "warning": "⚠️", "error": "❌"}
    return icons.get(status, "?")


def format_human(results: list[dict], work_level: str) -> str:
    """将检查结果格式化为人类可读文本。"""
    lines: list[str] = []
    lines.append(f"=== GB 17741-2025 合规检查报告  (工作等级 {work_level}) ===")
    lines.append("")

    if not results:
        lines.append("未找到任何章节文件，检查跳过。")
        return "\n".join(lines)

    total_score = sum(r["score"] for r in results)
    avg_score = total_score // len(results) if results else 0
    overall_status = (
        "error"
        if any(r["status"] == "error" for r in results)
        else "warning"
        if any(r["status"] == "warning" for r in results)
        else "pass"
    )

    lines.append(f"综合评分: {avg_score}/100  {_status_icon(overall_status)}")
    lines.append(f"检查章节: {len(results)} 个")
    lines.append("")

    for r in results:
        icon = _status_icon(r["status"])
        lines.append(f"── {icon} [{r['chapter_key']}] {r['file']}  得分={r['score']}")

        if r["errors"]:
            lines.append("   ❌ 不合规项:")
            for item in r["errors"]:
                lines.append(f"      • {item['label']}: {item.get('description', '')}")
                if item.get("suggestion"):
                    lines.append(f"        建议: {item['suggestion']}")

        if r["warnings"]:
            lines.append("   ⚠️ 警告:")
            for item in r["warnings"]:
                lines.append(f"      • {item['label']}: {item.get('description', '')}")

        if r["passed"]:
            lines.append(f"   ✅ 通过 {len(r['passed'])} 项")

        lines.append("")

    return "\n".join(lines)


def format_json_output(results: list[dict], work_level: str) -> str:
    """将检查结果序列化为 JSON。"""
    total_score = sum(r["score"] for r in results)
    avg_score = total_score // len(results) if results else 0
    payload = {
        "work_level": work_level,
        "chapter_count": len(results),
        "average_score": avg_score,
        "overall_passed": all(r["status"] != "error" for r in results),
        "chapters": results,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ============================================================
# CLI 入口
# ============================================================


def main() -> None:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(description="对 chapters/ 下的 .md 文件执行 GB 17741-2025 合规检查")
    parser.add_argument(
        "--chapters",
        default="chapters/",
        help="章节 .md 文件目录，默认 chapters/",
    )
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
        help="输出格式：human 或 json，默认 human",
    )
    args = parser.parse_args()

    chapters_dir = Path(args.chapters)
    if not chapters_dir.is_dir():
        print(f"[ERROR] 章节目录不存在: {args.chapters}", file=sys.stderr)
        sys.exit(1)

    results = check_chapters(chapters_dir, args.level)

    if args.format == "json":
        print(format_json_output(results, args.level))
    else:
        print(format_human(results, args.level))

    # 如果有 error 状态，以非零退出码告知 Hermes
    if any(r["status"] == "error" for r in results):
        sys.exit(2)


if __name__ == "__main__":
    main()
