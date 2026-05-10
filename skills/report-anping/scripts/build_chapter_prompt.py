from __future__ import annotations

"""
scripts/build_chapter_prompt.py — 为指定章节拼接 Hermes 生成 prompt

不调用 LLM；仅读取 params.json + lib/prompts/chapter_prompts.py，
将完整 prompt 输出到 stdout 供 Hermes 使用。

用法:
    python scripts/build_chapter_prompt.py --chapter chapter4 --params params_example.json
    python scripts/build_chapter_prompt.py --chapter preface --params params.json
    python scripts/build_chapter_prompt.py --list-chapters --params params.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.gb17741_knowledge import get_chapters_by_level
from lib.prompts.chapter_prompts import build_chapter_prompt

# ============================================================
# 辅助函数
# ============================================================


def load_params(params_path: str) -> dict:
    """从 JSON 文件加载项目参数。"""
    path = Path(params_path)
    if not path.exists():
        print(f"[ERROR] 参数文件不存在: {params_path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[ERROR] 参数文件 JSON 解析失败: {exc}", file=sys.stderr)
        sys.exit(1)


def find_chapter(chapters: list[dict], chapter_id: str) -> dict | None:
    """在章节列表中按 id 查找。"""
    for ch in chapters:
        if ch["id"] == chapter_id:
            return ch
    return None


# ============================================================
# CLI 入口
# ============================================================


def main() -> None:
    """CLI 入口：输出指定章节的生成 prompt 到 stdout。"""
    parser = argparse.ArgumentParser(description="为安评报告某章节拼接 Hermes 生成 prompt（不调 LLM）")
    parser.add_argument(
        "--chapter",
        help="章节 ID，如 chapter1 / chapter4 / preface / appendix",
    )
    parser.add_argument(
        "--params",
        default="params.json",
        help="项目参数 JSON 文件路径，默认 params.json",
    )
    parser.add_argument(
        "--list-chapters",
        action="store_true",
        help="列出当前工作等级的所有章节 ID 后退出",
    )
    args = parser.parse_args()

    params = load_params(args.params)
    level = params.get("level", "II")
    chapters = get_chapters_by_level(level)

    if args.list_chapters:
        for idx, ch in enumerate(chapters, 1):
            print(f"{idx:2}. {ch['id']:<16}  {ch['title']}")
        return

    if not args.chapter:
        parser.error("--chapter 为必填参数（或使用 --list-chapters 查看可用章节）")

    chapter = find_chapter(chapters, args.chapter)
    if chapter is None:
        valid_ids = [ch["id"] for ch in chapters]
        print(
            f"[ERROR] 章节 ID '{args.chapter}' 在 {level} 级安评中不存在。\n       可用章节: {valid_ids}",
            file=sys.stderr,
        )
        sys.exit(1)

    chapter_index = next(i for i, ch in enumerate(chapters) if ch["id"] == args.chapter)
    prompt = build_chapter_prompt(
        project_data=params,
        chapter=chapter,
        chapter_index=chapter_index,
        total_chapters=len(chapters),
    )
    print(prompt)


if __name__ == "__main__":
    main()
