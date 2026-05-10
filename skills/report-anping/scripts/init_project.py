from __future__ import annotations

"""Initialize a new report-anping project workspace.

Creates the required directory structure and writes an initial params.json
template.  Hermes calls this script at the very start of a new project to
ensure all expected paths exist before any other script runs.

Usage:
    python scripts/init_project.py --out-dir /path/to/project
    python scripts/init_project.py          # current directory

Idempotent: re-running on an existing workspace does not overwrite params.json
unless --force is passed.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DIRS: tuple[str, ...] = ("chapters", "exports", "data", "assets/generated")

PARAMS_TEMPLATE: dict = {
    "name": "",
    "level": "II",
    "engineering_type": "",
    "location": "",
    "coordinate_lon": "",
    "coordinate_lat": "",
    "building_height": 0,
    "construction_unit": "",
    "survey_unit": "",
    "evaluation_unit": "",
    "exceedance_probs": {
        "50_year": [63, 10, 5, 2],
        "100_year": [10, 5, 2, 1],
    },
    "report_date": "",
    "extra_notes": "",
    "historical_influences": [],
}

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def init_workspace(base_dir: Path, *, force: bool = False) -> dict[str, str]:
    """Initialize project workspace directories and params.json template.

    Args:
        base_dir: Root directory for the new project workspace.
        force: If True, overwrite existing params.json.

    Returns:
        Mapping from resource name to created/checked absolute path string.
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    created: dict[str, str] = {}

    for d in _DIRS:
        dir_path = base_dir / d
        dir_path.mkdir(parents=True, exist_ok=True)
        created[d] = str(dir_path)
        logger.debug("ensured directory: %s", dir_path)

    params_path = base_dir / "params.json"
    if params_path.exists() and not force:
        created["params.json"] = f"{params_path} (already exists — skipped, use --force to overwrite)"
        logger.info("params.json already exists, skipping write")
    else:
        params_path.write_text(
            json.dumps(PARAMS_TEMPLATE, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        created["params.json"] = str(params_path)
        logger.info("params.json template written: %s", params_path)

    return created


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entrypoint."""
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")

    parser = argparse.ArgumentParser(
        description="Initialize a new report-anping project workspace",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Project workspace root directory (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing params.json if present",
    )
    args = parser.parse_args()

    base_dir = Path(args.out_dir).resolve()
    created = init_workspace(base_dir, force=args.force)

    print(f"[OK] Workspace initialized: {base_dir}")
    print("\nCreated / verified:")
    for name, path in created.items():
        print(f"  {name}: {path}")

    params_json_path = base_dir / "params.json"
    print("\nNext steps:")
    print(f"  1. Edit params.json with project details: {params_json_path}")
    print("  2. python scripts/show_params.py")
    print(f"  3. python scripts/build_chapter_prompt.py --list-chapters --params {params_json_path}")


if __name__ == "__main__":
    main()
