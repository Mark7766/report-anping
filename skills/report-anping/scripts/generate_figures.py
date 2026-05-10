from __future__ import annotations

"""Generate deterministic figure assets for report chapters.

Usage:
    python scripts/generate_figures.py \
        --params params.json \
        --out-dir assets/generated \
        --catalog data/ceic_catalog.csv

If --catalog is omitted and data/ceic_catalog.csv exists in the project root,
it is used automatically for catalog-dependent charts.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.chart_builder import (
    generate_epicenter_map,
    generate_focal_depth_distribution,
    generate_intensity_bar_chart,
    generate_mt_chart,
    generate_pga_bar_chart,
    generate_response_spectrum_chart,
    load_catalog_records,
    generate_epicenter_map_fallback,
    generate_borehole_plan,
    generate_borehole_log,
)

# Default CEIC catalog path relative to the skill root
_DEFAULT_CATALOG = Path(__file__).parent.parent / "data" / "ceic_catalog.csv"


def generate_figures_manifest(
    params: dict,
    out_dir: Path,
    catalog_path: Path | None = None,
    min_magnitude: float = 4.7,
) -> dict[str, str]:
    """Generate figure files and return their relative paths.

    Args:
        params: Project params dictionary.
        out_dir: Output directory for generated figures.
        catalog_path: Optional earthquake catalog path.  If None and
            data/ceic_catalog.csv exists at the skill root, it is used
            automatically.
        min_magnitude: M-T minimum magnitude filter.

    Returns:
        Mapping from figure key to file path string.
    """
    # Auto-detect default catalog when not explicitly provided
    if catalog_path is None and _DEFAULT_CATALOG.exists():
        catalog_path = _DEFAULT_CATALOG

    out_dir.mkdir(parents=True, exist_ok=True)

    response_spectrum = out_dir / "response_spectrum.png"
    pga_bar = out_dir / "pga_comparison.png"

    generate_response_spectrum_chart(params, response_spectrum)
    generate_pga_bar_chart(params, pga_bar)

    manifest: dict[str, str] = {
        "response_spectrum": str(response_spectrum),
        "pga_comparison": str(pga_bar),
    }

    if catalog_path and catalog_path.exists():
        records = load_catalog_records(catalog_path)

        mt_chart = out_dir / "mt_chart.png"
        generate_mt_chart(records, mt_chart, title="Regional Earthquake M-T Chart", min_magnitude=min_magnitude)
        manifest["mt_chart"] = str(mt_chart)

        try:
            center_lon = float(params.get("coordinate_lon", 0))
            center_lat = float(params.get("coordinate_lat", 0))
        except (TypeError, ValueError):
            center_lon, center_lat = 0.0, 0.0

        site_name = str(params.get("name", "Site"))
        epicenter_map = out_dir / "epicenter_map.png"
        generate_epicenter_map(records, epicenter_map, center_lon, center_lat, site_name=site_name)
        manifest["epicenter_map"] = str(epicenter_map)

        focal_depth_chart = out_dir / "focal_depth_distribution.png"
        generate_focal_depth_distribution(records, focal_depth_chart)
        manifest["focal_depth_distribution"] = str(focal_depth_chart)
    else:
        # No CEIC catalog — generate a simplified epicentre map with
        # site marker + reference circles as a fallback.
        try:
            center_lon = float(params.get("coordinate_lon", 0))
            center_lat = float(params.get("coordinate_lat", 0))
        except (TypeError, ValueError):
            center_lon, center_lat = 0.0, 0.0

        site_name = str(params.get("name", "Site"))
        epicenter_map = out_dir / "epicenter_map.png"
        generate_epicenter_map_fallback(center_lon, center_lat, epicenter_map, site_name=site_name)
        manifest["epicenter_map"] = str(epicenter_map)

    # Always generate borehole schematic figures for engineering geology chapter
    borehole_plan = out_dir / "borehole_plan.png"
    generate_borehole_plan(params, borehole_plan)
    manifest["borehole_plan"] = str(borehole_plan)

    borehole_log = out_dir / "borehole_log.png"
    generate_borehole_log(params, borehole_log)
    manifest["borehole_log"] = str(borehole_log)

    historical_influences = params.get("historical_influences")
    if historical_influences and isinstance(historical_influences, list):
        site_name = str(params.get("name", "Site"))
        intensity_chart = out_dir / "intensity_bar_chart.png"
        generate_intensity_bar_chart(historical_influences, intensity_chart, site_name=site_name)
        manifest["intensity_bar_chart"] = str(intensity_chart)

    return manifest


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Generate report figure assets from params and optional catalog")
    parser.add_argument("--params", default="params.json", help="Path to params JSON (default: params.json)")
    parser.add_argument("--out-dir", default="assets/generated", help="Output figure directory")
    parser.add_argument(
        "--catalog",
        default=None,
        help="CEIC catalog CSV/JSON path (auto-detected from data/ceic_catalog.csv if omitted)",
    )
    parser.add_argument("--min-mag", type=float, default=4.7, help="Minimum magnitude for M-T chart")
    args = parser.parse_args()

    params_path = Path(args.params)
    if not params_path.exists():
        print(f"[ERROR] params file not found: {params_path}", file=sys.stderr)
        sys.exit(1)

    params = json.loads(params_path.read_text(encoding="utf-8"))
    catalog_path = Path(args.catalog) if args.catalog else None

    manifest = generate_figures_manifest(
        params=params,
        out_dir=Path(args.out_dir),
        catalog_path=catalog_path,
        min_magnitude=args.min_mag,
    )
    print(json.dumps({"figures": manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
