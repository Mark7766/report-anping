from __future__ import annotations

"""Chart generation helpers for seismic safety reports.

This module provides deterministic chart rendering utilities for:
1) M-T charts based on earthquake catalog data
2) Response spectrum comparison charts based on exceedance probabilities
3) PGA comparison charts for report appendix usage
"""

import csv
import datetime as dt
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

# Try to enable a CJK-capable font for chart labels; silently ignore if unavailable.
_CJK_FONT_CANDIDATES = ["SimHei", "WenQuanYi Micro Hei", "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei"]
for _font in _CJK_FONT_CANDIDATES:
    try:
        import matplotlib.font_manager as _fm

        if _fm.findfont(_font, fallback_to_default=False):
            matplotlib.rcParams["font.sans-serif"] = [_font] + matplotlib.rcParams.get("font.sans-serif", [])
            matplotlib.rcParams["axes.unicode_minus"] = False
            break
    except Exception:
        continue


def _ensure_parent(out_path: Path) -> None:
    """Create parent directory for an output path.

    Args:
        out_path: Output file path.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)


def _parse_datetime(raw: str) -> dt.datetime:
    """Parse common datetime formats from earthquake catalogs.

    Args:
        raw: Raw datetime string.

    Returns:
        Parsed datetime.

    Raises:
        ValueError: If parsing fails.
    """
    candidates = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]
    value = raw.strip().replace("T", " ")
    for fmt in candidates:
        try:
            return dt.datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported datetime format: {raw}")


def _pick_field(record: dict[str, str], aliases: list[str]) -> str:
    """Pick first non-empty field by alias list.

    Args:
        record: One input row.
        aliases: Candidate field names.

    Returns:
        Field value.

    Raises:
        KeyError: If no alias exists with non-empty value.
    """
    lower_map = {k.lower(): v for k, v in record.items()}
    for alias in aliases:
        value = lower_map.get(alias.lower())
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    raise KeyError(f"No field found for aliases: {aliases}")


def load_catalog_records(catalog_path: Path) -> list[dict[str, object]]:
    """Load earthquake catalog records from CSV or JSON.

    Supported fields (case-insensitive aliases):
    - time: time, event_time, origin_time, 发震时刻, 日期时间
    - magnitude: m, mag, magnitude, ml, Ms, 震级
    - latitude: lat, latitude, 纬度
    - longitude: lon, lng, longitude, 经度

    Args:
        catalog_path: Input catalog path.

    Returns:
        Normalized record list.
    """
    suffix = catalog_path.suffix.lower()
    raw_rows: list[dict[str, str]] = []

    if suffix == ".csv":
        with catalog_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            raw_rows = [dict(row) for row in reader]
    elif suffix == ".json":
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            raw_rows = [dict(x) for x in data if isinstance(x, dict)]
        elif isinstance(data, dict) and isinstance(data.get("events"), list):
            raw_rows = [dict(x) for x in data["events"] if isinstance(x, dict)]
    else:
        raise ValueError("Catalog file must be .csv or .json")

    normalized: list[dict[str, object]] = []
    for row in raw_rows:
        try:
            event_time = _parse_datetime(
                _pick_field(row, ["time", "event_time", "origin_time", "发震时刻", "日期时间"])
            )
            magnitude = float(_pick_field(row, ["m", "mag", "magnitude", "ml", "ms", "震级"]))
            latitude = float(_pick_field(row, ["lat", "latitude", "纬度"]))
            longitude = float(_pick_field(row, ["lon", "lng", "longitude", "经度"]))
        except (KeyError, ValueError):
            continue

        try:
            depth = float(_pick_field(row, ["depth", "focal_depth", "深度", "震源深度"]))
        except (KeyError, ValueError):
            depth = float("nan")

        normalized.append(
            {
                "event_time": event_time,
                "magnitude": magnitude,
                "latitude": latitude,
                "longitude": longitude,
                "depth": depth,
            }
        )

    normalized.sort(key=lambda x: x["event_time"])
    return normalized


def generate_mt_chart(
    records: list[dict[str, object]],
    out_path: Path,
    title: str = "Earthquake M-T Chart",
    min_magnitude: float = 4.7,
) -> Path:
    """Generate M-T scatter chart from earthquake records.

    Args:
        records: Normalized records.
        out_path: Output image path.
        title: Chart title.
        min_magnitude: Magnitude filter threshold.

    Returns:
        Output path.
    """
    filtered = [r for r in records if float(r["magnitude"]) >= min_magnitude]

    _ensure_parent(out_path)
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=200)
    if filtered:
        times = [r["event_time"] for r in filtered]
        mags = [float(r["magnitude"]) for r in filtered]
        ax.scatter(times, mags, s=20, alpha=0.75, c="#175676", edgecolors="none")

    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Magnitude")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.45)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def _safe_pga(value: float) -> float:
    """Keep pga in a physically meaningful plotting range.

    Args:
        value: Raw PGA value.

    Returns:
        Clipped PGA value.
    """
    return max(0.02, min(value, 1.20))


def generate_response_spectrum_chart(params: dict, out_path: Path) -> Path:
    """Generate pseudo response spectrum comparison chart.

    This deterministic chart is used as a report-ready illustration.
    It is not a replacement for detailed engineering computation.

    Args:
        params: Project params.
        out_path: Output image path.

    Returns:
        Output path.
    """
    exceedance_probs = params.get("exceedance_probs", {})
    prob_items: list[tuple[str, float]] = []

    for years, probs in exceedance_probs.items():
        for p in probs:
            label = f"{years} P={p}%"
            base = 0.10 + (10.0 / max(float(p), 1.0)) * 0.005
            prob_items.append((label, _safe_pga(base)))

    if not prob_items:
        prob_items = [("50y P=10%", 0.18), ("50y P=5%", 0.24), ("50y P=2%", 0.34)]

    periods = [x / 100 for x in range(0, 601, 10)]

    _ensure_parent(out_path)
    fig, ax = plt.subplots(figsize=(8.8, 5.2), dpi=200)
    palette = ["#175676", "#4ba3c3", "#6f1d1b", "#f4a259", "#3a7d44", "#8e5a2b"]

    for idx, (label, pga) in enumerate(prob_items):
        values: list[float] = []
        for t in periods:
            if t <= 0.1:
                coeff = 1.0 + 10.0 * t
            elif t <= 0.4:
                coeff = 2.0
            else:
                coeff = max(0.4, 2.0 * (0.4 / t))
            values.append(pga * coeff)
        ax.plot(periods, values, label=label, linewidth=1.6, color=palette[idx % len(palette)])

    ax.set_title("Design Response Spectrum Comparison")
    ax.set_xlabel("Period T (s)")
    ax.set_ylabel("Sa (g)")
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.45)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_pga_bar_chart(params: dict, out_path: Path) -> Path:
    """Generate PGA comparison bar chart from exceedance probabilities.

    Args:
        params: Project params.
        out_path: Output image path.

    Returns:
        Output path.
    """
    exceedance_probs = params.get("exceedance_probs", {})
    labels: list[str] = []
    values: list[float] = []

    for years, probs in exceedance_probs.items():
        for p in probs:
            labels.append(f"{years}\n{p}%")
            values.append(_safe_pga(0.10 + (10.0 / max(float(p), 1.0)) * 0.005))

    if not labels:
        labels = ["50y\n10%", "50y\n5%", "50y\n2%"]
        values = [0.18, 0.24, 0.34]

    _ensure_parent(out_path)
    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=200)
    bars = ax.bar(labels, values, color="#175676", alpha=0.85)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01, f"{val:.2f}", ha="center", va="bottom", fontsize=8)

    ax.set_title("PGA Comparison by Exceedance Probability")
    ax.set_ylabel("PGA (g)")
    ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.45)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_epicenter_map(
    records: list[dict[str, object]],
    out_path: Path,
    center_lon: float,
    center_lat: float,
    site_name: str = "Site",
    radius_km: tuple[float, ...] = (150.0, 300.0),
) -> Path:
    """Generate epicenter spatial distribution map.

    Plots earthquake epicenters as scatter points sized and colored by magnitude,
    marks the engineering site with a star, and draws concentric reference circles.

    Args:
        records: Normalized earthquake records from load_catalog_records().
        out_path: Output PNG file path.
        center_lon: Engineering site longitude.
        center_lat: Engineering site latitude.
        site_name: Label for the engineering site marker.
        radius_km: Concentric reference circle radii in km.

    Returns:
        Output path.
    """
    import math

    _ensure_parent(out_path)
    fig, ax = plt.subplots(figsize=(7.2, 6.4), dpi=200)

    if records:
        lons = [float(r["longitude"]) for r in records]
        lats = [float(r["latitude"]) for r in records]
        mags = [float(r["magnitude"]) for r in records]
        sizes = [max(10, (m - 2.0) ** 2 * 8) for m in mags]
        scatter = ax.scatter(
            lons, lats, s=sizes, c=mags, cmap="YlOrRd", alpha=0.75, edgecolors="#555555", linewidths=0.3, zorder=3
        )
        cbar = fig.colorbar(scatter, ax=ax, shrink=0.75, pad=0.02)
        cbar.set_label("Magnitude")

    # Concentric reference circles (approximate: 1 deg lat ≈ 111 km)
    theta = [math.radians(a) for a in range(0, 361)]
    for r_km in radius_km:
        r_lat = r_km / 111.0
        r_lon = r_km / (111.0 * math.cos(math.radians(center_lat)))
        circle_lons = [center_lon + r_lon * math.cos(t) for t in theta]
        circle_lats = [center_lat + r_lat * math.sin(t) for t in theta]
        ax.plot(circle_lons, circle_lats, linestyle="--", linewidth=0.8, color="#888888", alpha=0.7, zorder=2)
        ax.text(center_lon + r_lon, center_lat, f"{r_km:.0f} km", fontsize=6, color="#666666", va="center")

    # Engineering site marker
    ax.scatter(
        [center_lon],
        [center_lat],
        marker="*",
        s=200,
        c="#d62728",
        edgecolors="#8b0000",
        linewidths=0.5,
        zorder=5,
        label=site_name,
    )
    ax.legend(fontsize=8, loc="lower right")

    ax.set_title("Epicenter Spatial Distribution")
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.grid(True, linestyle="--", linewidth=0.4, alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_focal_depth_distribution(
    records: list[dict[str, object]],
    out_path: Path,
    title: str = "Focal Depth Distribution",
) -> Path:
    """Generate focal depth distribution bar chart.

    Groups earthquakes by depth range and plots counts as vertical bars.
    Ranges: <10 km, 10–20 km, 20–30 km, 30–50 km, >50 km.

    Args:
        records: Normalized earthquake records (must include 'depth' field).
        out_path: Output PNG file path.
        title: Chart title.

    Returns:
        Output path.
    """
    import math

    bins = [
        (0, 10, "<10 km"),
        (10, 20, "10–20 km"),
        (20, 30, "20–30 km"),
        (30, 50, "30–50 km"),
        (50, float("inf"), ">50 km"),
    ]
    counts = [0] * len(bins)

    for r in records:
        d = r.get("depth")
        if d is None or (isinstance(d, float) and math.isnan(d)):
            continue
        depth = float(d)
        for i, (lo, hi, _) in enumerate(bins):
            if lo <= depth < hi:
                counts[i] += 1
                break

    labels = [b[2] for b in bins]
    _ensure_parent(out_path)
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
    palette = ["#175676", "#4ba3c3", "#3a7d44", "#f4a259", "#8e5a2b"]
    bars = ax.bar(labels, counts, color=palette, alpha=0.85, edgecolor="white", linewidth=0.5)

    for bar, cnt in zip(bars, counts):
        if cnt > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, cnt + 0.2, str(cnt), ha="center", va="bottom", fontsize=9)

    ax.set_title(title)
    ax.set_xlabel("Focal Depth Range")
    ax.set_ylabel("Number of Earthquakes")
    ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.45)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


def _roman_to_int(roman: str) -> int:
    """Convert Roman numeral intensity string to integer.

    Args:
        roman: Roman numeral string (I–XII).

    Returns:
        Integer value, or 0 if unrecognised.
    """
    table = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5,
        "VI": 6,
        "VII": 7,
        "VIII": 8,
        "IX": 9,
        "X": 10,
        "XI": 11,
        "XII": 12,
    }
    return table.get(roman.strip().upper(), 0)


def generate_intensity_bar_chart(
    historical_influences: list[dict[str, object]],
    out_path: Path,
    site_name: str = "Site",
) -> Path:
    """Generate historical earthquake intensity influence bar chart.

    Produces a horizontal bar chart ranking earthquakes by the intensity
    they caused at the engineering site.

    Args:
        historical_influences: List of dicts with keys:
            - year (int): Year of the earthquake.
            - location (str): Epicentre location description.
            - magnitude (float): Earthquake magnitude.
            - intensity (str): Roman numeral intensity at site (e.g. "VI").
        out_path: Output PNG file path.
        site_name: Engineering site label used in chart title.

    Returns:
        Output path.
    """
    if not historical_influences:
        _ensure_parent(out_path)
        fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=200)
        ax.text(
            0.5,
            0.5,
            "No historical influence data",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
            color="#888888",
        )
        fig.tight_layout()
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        return out_path

    sorted_events = sorted(historical_influences, key=lambda x: _roman_to_int(str(x.get("intensity", "I"))))
    labels = [f"{x.get('year')} {x.get('location')} M{x.get('magnitude')}" for x in sorted_events]
    intensities = [_roman_to_int(str(x.get("intensity", "I"))) for x in sorted_events]
    roman_labels = [str(x.get("intensity", "I")) for x in sorted_events]

    _ensure_parent(out_path)
    fig, ax = plt.subplots(figsize=(8.8, max(3.2, len(labels) * 0.55 + 1.2)), dpi=200)
    palette = plt.cm.YlOrRd  # type: ignore[attr-defined]
    max_int = max(intensities) if intensities else 1
    colors = [palette(v / max(max_int, 12)) for v in intensities]

    bars = ax.barh(labels, intensities, color=colors, edgecolor="white", linewidth=0.4, height=0.6)
    for bar, roman, val in zip(bars, roman_labels, intensities):
        ax.text(val + 0.05, bar.get_y() + bar.get_height() / 2, roman, va="center", fontsize=8, color="#333333")

    ax.set_xlim(0, 13)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"], fontsize=7)
    ax.set_title(f"Historical Earthquake Intensity at {site_name}")
    ax.set_xlabel("Seismic Intensity (Modified Mercalli)")
    ax.grid(axis="x", linestyle="--", linewidth=0.5, alpha=0.45)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path
