from __future__ import annotations

"""Build M-T chart from CEIC earthquake catalog export.

Expected workflow:
1) Export earthquake catalog from CEIC website to CSV/JSON
2) Run this script to produce report-ready M-T chart image
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.chart_builder import generate_mt_chart, load_catalog_records


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Generate M-T chart from CEIC catalog CSV/JSON")
    parser.add_argument("--catalog", required=True, help="CEIC catalog file (.csv or .json)")
    parser.add_argument("--out", default="assets/generated/mt_chart.png", help="Output image path")
    parser.add_argument("--title", default="Regional Earthquake M-T Chart", help="Chart title")
    parser.add_argument("--min-mag", type=float, default=4.7, help="Minimum magnitude filter")
    args = parser.parse_args()

    catalog = Path(args.catalog)
    if not catalog.exists():
        print(f"[ERROR] catalog file not found: {catalog}", file=sys.stderr)
        sys.exit(1)

    records = load_catalog_records(catalog)
    if not records:
        print("[ERROR] no valid events found in catalog", file=sys.stderr)
        sys.exit(2)

    out_path = Path(args.out)
    generate_mt_chart(records, out_path, title=args.title, min_magnitude=args.min_mag)
    print(f"[OK] M-T chart generated: {out_path}")


if __name__ == "__main__":
    main()
