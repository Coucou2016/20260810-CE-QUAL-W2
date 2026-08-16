#!/usr/bin/env python3
"""Build real offline watershed/regional basemaps for three W2 cases.

Downloads XYZ map tiles once (Esri World Imagery), caches them under
analysis/basemap_cache/, then redraws offline. Model planforms from PHI0/DLX
are placed with documented landmark registration (dam / mouth / source) —
never a blank continent outline or invented box-as-basemap.

Outputs: 05_REPRO_RUNS/<run_id>/analysis/*_watershed_basemap.png
Updates figure_manifest.json watershed_basemap entries.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Optional
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import mercantile
import numpy as np
import requests
from PIL import Image

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "CE-QUAL-W2-repro-basemap/1.0 (offline scientific report; local cache)"})

from make_visualizations import CASES, OUT_DIR, RUN_BASE, RUN_ID, parse_bathy
from river_alignment import (
    ControlPair,
    choose_best_registration,
    extract_reference_channel,
    fetch_osm_waterways,
    lateral_offset_stats,
    ref_endpoint_farthest_from,
    register_landmark_rigid,
    register_two_point_similarity,
)

ROOT = Path(r"I:\Projects\20260810-CE-QUAL-W2")
CACHE = OUT_DIR / "basemap_cache"
TILE_CACHE = CACHE / "xyz_tiles"
CACHE.mkdir(parents=True, exist_ok=True)
TILE_CACHE.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

USER_AGENT = "CE-QUAL-W2-repro-basemap/1.0 (offline scientific report; local cache)"

# Esri World Imagery — real satellite/aerial; cached locally after first fetch.
ESRI_IMAGERY = {
    "id": "Esri_WorldImagery",
    "name": "Esri World Imagery",
    "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "attribution": "Esri, Maxar, Earthstar Geographics",
}

# Esri World Topo Map — roads / hydro / place names (OSM tile CDN blocked us with 403).
ESRI_TOPO = {
    "id": "Esri_WorldTopoMap",
    "name": "Esri World Topo Map",
    "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    "attribution": "Esri, USGS, NOAA, and the GIS User Community",
}


@dataclass
class GeoRef:
    name: str
    lat: float
    lon: float
    role: str
    source: str


@dataclass
class SiteSpec:
    place: str
    # west, south, east, north — real geographic window around the named waterbody
    map_bbox: tuple[float, float, float, float]
    zoom: int
    refs: list[GeoRef]
    # which model endpoint is the primary landmark (start|end)
    model_anchor_end: str
    # primary landmark role in refs
    anchor_role: str
    # optional second landmark for rotation (role name); None = use mean heading to mid ref
    align_role: Optional[str]
    registration_kind: str  # "landmark_rigid" | "two_point_similarity" | "auto"
    baseline_registration_kind: str  # method used before this improvement pass
    osm_name_hints: list[str]
    extra_control_roles: list[str]  # roles beyond anchor/align for multi-point
    public_note: str


# Verifiable public coordinates (not invented segment endpoints).
#
# W2 branch convention: segment index increases upstream → downstream.
# Boundary segs at both ends have zero width; the deepest wet segment is at
# the downstream (dam) end for reservoir cases. Anchoring the *upstream*
# end at the dam landmark reverses the chord used for rotation and appears
# as a north–south (cross-track) mirror of the planform on the map.
SITES: dict[str, SiteSpec] = {
    "Long_Lake": SiteSpec(
        place="Long Lake / Lake Spokane, Spokane River, Washington, USA",
        map_bbox=(-118.02, 47.72, -117.48, 47.96),
        zoom=12,
        refs=[
            GeoRef("Long Lake Dam", 47.8372, -117.8397, "dam", "Wikipedia / GNIS Long Lake Dam"),
            # Upstream end of Lake Spokane reach ≈ Nine Mile Dam (Spokane River flows W into Long Lake Dam).
            GeoRef("Nine Mile Dam (US)", 47.77478, -117.54467, "source", "DamLookup / NID WA00068"),
            GeoRef("Lake Spokane center", 47.8315, -117.7626, "mid", "WDFW Lake Spokane"),
            GeoRef("w2_con LAT/LONG", 47.8, -117.8, "control", "case w2_con.csv solar site"),
        ],
        model_anchor_end="end",  # DS / deep end ≈ dam (seg36 wet); US/start ≈ Nine Mile
        anchor_role="dam",
        align_role="source",
        # Dam+US two-point: prior dam+rotate-to-mid left ~2–5 km north bias (PHI0 path ≠ shore).
        registration_kind="auto",
        baseline_registration_kind="two_point_similarity",
        osm_name_hints=["Spokane", "Long Lake", "Lake Spokane"],
        extra_control_roles=["mid"],
        public_note="多控制点相似/TPS 自动择优；PHI0/DLX 示意路径与真实弯道差异仍可能产生公里级几何残差",
    ),
    "DeGray": SiteSpec(
        place="DeGray Lake / Reservoir, Caddo River, Arkansas, USA",
        map_bbox=(-93.42, 34.08, -92.98, 34.40),
        zoom=12,
        refs=[
            GeoRef("DeGray Dam", 34.21398, -93.11129, "dam", "TopoQuest / USGS GNIS De Gray Dam"),
            # NW head of impoundment on Caddo River (OSM/NHD vicinity; not a surveyed segment endpoint).
            GeoRef("Caddo River head (NW)", 34.3520, -93.3480, "source", "OSM Caddo River / reservoir NW extent"),
            GeoRef("DeGray Lake (GNIS)", 34.25196, -93.19917, "mid", "TopoQuest / USGS GNIS De Gray Lake"),
            GeoRef("w2_con LAT/LONG", 34.2, -93.3, "control", "case w2_con.csv solar site"),
        ],
        model_anchor_end="end",  # DS / deep end ≈ dam (seg31 wet); US/start = NW headwaters
        anchor_role="dam",
        align_role="source",
        registration_kind="auto",
        baseline_registration_kind="landmark_rigid",
        osm_name_hints=["Caddo", "DeGray", "De Gray"],
        extra_control_roles=["mid"],
        public_note="坝+上游源头双端 + 库心/弧长控制点多点配准；刚性旋转已弃用",
    ),
    "Columbia_Slough": SiteSpec(
        place="Columbia Slough (Fairview Lake → Willamette), Portland, Oregon, USA",
        map_bbox=(-122.82, 45.48, -122.40, 45.70),
        zoom=12,
        refs=[
            GeoRef("Slough mouth (Willamette)", 45.6433, -122.7686, "mouth", "Wikipedia Columbia Slough"),
            GeoRef("Slough source (Fairview Lk)", 45.5500, -122.4567, "source", "Wikipedia Columbia Slough"),
            GeoRef("w2_con LAT/LONG", 45.6, -122.6, "control", "case w2_con.csv solar site"),
        ],
        model_anchor_end="end",  # DS end = Willamette mouth; start = Fairview source
        anchor_role="mouth",
        align_role="source",
        registration_kind="auto",
        baseline_registration_kind="two_point_similarity",
        osm_name_hints=["Columbia Slough", "Slough"],
        extra_control_roles=[],
        public_note="源-口双端 + OSM 弧长控制点多点配准；双分支 slough 几何与 PHI0 示意仍有残差",
    ),
}


@dataclass
class SiteGeo:
    lat: float
    lon_west_positive: float
    lon: float
    source: str
    note: str


def parse_w2_lat_lon(case_dir: Path) -> Optional[SiteGeo]:
    candidates = sorted(case_dir.glob("w2_con*.csv"))
    if not candidates:
        return None
    path = candidates[0]
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for i, line in enumerate(lines):
        if not line.upper().startswith("WB1"):
            continue
        nums = []
        for j in range(i + 1, min(i + 8, len(lines))):
            first = lines[j].split(",")[0].strip()
            if not first:
                continue
            try:
                nums.append(float(first))
            except ValueError:
                break
            if len(nums) >= 2:
                break
        if len(nums) < 2:
            continue
        lat, lon_mag = nums[0], nums[1]
        if 20.0 <= lat <= 70.0 and 60.0 <= lon_mag <= 130.0:
            return SiteGeo(
                lat=lat,
                lon_west_positive=lon_mag,
                lon=-abs(lon_mag),
                source=path.name,
                note="控制文件水体 LATITUDE/LONGITUDE（太阳辐射用单点，非分段端点）",
            )
    return None


def xy_geo_from_phi(dlx: np.ndarray, phi0: Optional[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Integrate planform in local east/north meters.

    CE-QUAL-W2 PHI0 is segment orientation in radians, clockwise from north
    (manual Fig. A-28 / wind convention). Bearing → EN:
        ΔE = DLX * sin(PHI0),  ΔN = DLX * cos(PHI0).
    Do not confuse with matplotlib image row order; geographic y is north-positive
    and imshow uses extent=(W,E,S,N) with origin='upper' so north stays up.
    """
    x = np.zeros(len(dlx))
    y = np.zeros(len(dlx))
    if phi0 is None or len(phi0) != len(dlx):
        x[0] = dlx[0] * 0.5
        for i in range(1, len(dlx)):
            x[i] = x[i - 1] + 0.5 * (dlx[i - 1] + dlx[i])
        return x, y
    for i in range(1, len(dlx)):
        ang = float(phi0[i - 1])
        x[i] = x[i - 1] + dlx[i - 1] * math.sin(ang)
        y[i] = y[i - 1] + dlx[i - 1] * math.cos(ang)
    return x, y


def meters_per_deg(lat0: float) -> tuple[float, float]:
    m_lat = 110540.0
    m_lon = 111320.0 * math.cos(math.radians(lat0))
    return m_lon, m_lat


def lonlat_to_local_m(lon: float, lat: float, lon0: float, lat0: float) -> tuple[float, float]:
    m_lon, m_lat = meters_per_deg(lat0)
    return (lon - lon0) * m_lon, (lat - lat0) * m_lat


def local_m_to_lonlat(xe: np.ndarray, yn: np.ndarray, lon0: float, lat0: float) -> tuple[np.ndarray, np.ndarray]:
    m_lon, m_lat = meters_per_deg(lat0)
    return lon0 + xe / m_lon, lat0 + yn / m_lat


def _rot(xe: np.ndarray, yn: np.ndarray, ang: float) -> tuple[np.ndarray, np.ndarray]:
    c, s = math.cos(ang), math.sin(ang)
    return c * xe - s * yn, s * xe + c * yn


def register_planform(
    x_e: np.ndarray,
    y_n: np.ndarray,
    site: SiteSpec,
    short: str,
) -> dict:
    """Register local east/north meters to lon/lat using public landmarks + OSM reference."""
    refs = {r.role: r for r in site.refs}
    anchor = refs[site.anchor_role]
    align = refs[site.align_role] if site.align_role and site.align_role in refs else None

    if site.model_anchor_end == "start":
        i_a, i_b = 0, len(x_e) - 1
    else:
        i_a, i_b = len(x_e) - 1, 0

    if align is None:
        raise ValueError(f"{short}: missing align role {site.align_role}")

    refs_by_role = {r.role: r for r in site.refs}

    # OSM reference channel (cached)
    osm_path = CACHE / short / "osm_waterways.geojson"
    geojson = fetch_osm_waterways(site.map_bbox, osm_path)
    ref_coords, ref_label = extract_reference_channel(
        geojson,
        anchor.lon,
        anchor.lat,
        align.lon,
        align.lat,
        name_hints=site.osm_name_hints,
    )

    # DeGray: OSM Caddo may not reach published NW head; use river upstream endpoint for align.
    align_lon, align_lat = align.lon, align.lat
    align_note = align.name
    if short == "DeGray" and len(ref_coords) >= 2:
        up_lon, up_lat = ref_endpoint_farthest_from(ref_coords, anchor.lon, anchor.lat)
        dist_pub = math.hypot((align.lon - up_lon) * 111320, (align.lat - up_lat) * 110540)
        if dist_pub > 5000:
            align_lon, align_lat = up_lon, up_lat
            align_note = f"Caddo OSM upstream endpoint ({up_lat:.4f}, {up_lon:.4f})"

    # Baseline for before/after comparison (previous method per case)
    baseline_kind = site.baseline_registration_kind
    if baseline_kind == "landmark_rigid":
        # DeGray legacy: rotate toward mid landmark, not source
        mid = refs_by_role.get("mid")
        align_for_rigid = mid if mid is not None else align
        base_reg = register_landmark_rigid(
            x_e, y_n, i_a, i_b, anchor.lon, anchor.lat, align_for_rigid.lon, align_for_rigid.lat
        )
    else:
        base_reg = register_two_point_similarity(
            x_e, y_n, i_a, i_b, anchor.lon, anchor.lat, align_lon, align_lat
        )
    base_stats = lateral_offset_stats(base_reg.lon, base_reg.lat, ref_coords, ref_label)

    extra_pairs: list[ControlPair] = []
    n = len(x_e)
    for role in site.extra_control_roles:
        if role not in refs_by_role:
            continue
        r = refs_by_role[role]
        extra_pairs.append(ControlPair(n // 2, r.lon, r.lat, r.name, weight=2.0))

    if site.registration_kind == "auto":
        reg_result, lat_stats, cmp_info = choose_best_registration(
            x_e,
            y_n,
            ref_coords,
            ref_label,
            i_a,
            i_b,
            anchor.lon,
            anchor.lat,
            align_lon,
            align_lat,
            extra_pairs,
            baseline_kind=site.baseline_registration_kind,
        )
    elif site.registration_kind == "landmark_rigid":
        reg_result = register_landmark_rigid(
            x_e, y_n, i_a, i_b, anchor.lon, anchor.lat, align.lon, align.lat
        )
        lat_stats = lateral_offset_stats(reg_result.lon, reg_result.lat, ref_coords, ref_label)
        cmp_info = {"selected": "landmark_rigid", "baseline": {}, "improved": {}, "all_methods": {}, "ref_source": ref_label}
    else:
        reg_result = register_two_point_similarity(
            x_e, y_n, i_a, i_b, anchor.lon, anchor.lat, align.lon, align.lat
        )
        lat_stats = lateral_offset_stats(reg_result.lon, reg_result.lat, ref_coords, ref_label)
        cmp_info = {"selected": "two_point_similarity", "baseline": {}, "improved": {}, "all_methods": {}, "ref_source": ref_label}

    lon, lat = reg_result.lon, reg_result.lat
    ang = reg_result.angle_deg
    scale = reg_result.scale

    # Mid residual toward align landmark (if not endpoint)
    residual_m = float("nan")
    if align is not None and site.align_role not in {site.anchor_role}:
        imid = n // 2
        lat0, lon0 = anchor.lat, anchor.lon
        rx, ry = lonlat_to_local_m(float(lon[imid]), float(lat[imid]), lon0, lat0)
        gx, gy = lonlat_to_local_m(align.lon, align.lat, lon0, lat0)
        if site.align_role != site.anchor_role and site.registration_kind == "landmark_rigid":
            residual_m = math.hypot(rx - gx, ry - gy)

    return {
        "lon": lon,
        "lat": lat,
        "anchor": anchor,
        "align": align,
        "angle_deg": ang if ang == ang else 0.0,
        "scale": scale if scale == scale else 1.0,
        "kind": reg_result.kind,
        "precision_label": f"OSM参考+{reg_result.kind}；非精密岸线 GIS",
        "residual_mid_m": residual_m,
        "lon0": anchor.lon,
        "lat0": anchor.lat,
        "i_anchor": i_a,
        "ref_coords": ref_coords,
        "ref_label": ref_label,
        "lateral_stats": lat_stats,
        "alignment_comparison": cmp_info,
        "baseline_lateral": {
            "mean_m": round(base_stats.mean_m, 1),
            "max_m": round(base_stats.max_m, 1),
            "p95_m": round(base_stats.p95_m, 1),
            "rmse_m": round(base_stats.rmse_m, 1),
        },
        "improved_lateral": {
            "mean_m": round(lat_stats.mean_m, 1),
            "max_m": round(lat_stats.max_m, 1),
            "p95_m": round(lat_stats.p95_m, 1),
            "rmse_m": round(lat_stats.rmse_m, 1),
        },
    }


def fetch_url(url: str, retries: int = 4) -> bytes:
    last_err: Optional[Exception] = None
    for k in range(retries):
        try:
            resp = SESSION.get(url, timeout=90)
            resp.raise_for_status()
            if len(resp.content) < 50:
                raise RuntimeError(f"tiny response ({len(resp.content)} bytes)")
            return resp.content
        except Exception as e:  # noqa: BLE001 — network; retry then raise
            last_err = e
            time.sleep(1.5 * (k + 1))
    raise RuntimeError(f"tile download failed: {url} ({last_err})")


def tile_path(provider_id: str, z: int, x: int, y: int) -> Path:
    p = TILE_CACHE / provider_id / str(z) / str(x) / f"{y}.png"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def get_tile(provider: dict, z: int, x: int, y: int) -> Image.Image:
    path = tile_path(provider["id"], z, x, y)
    if path.exists() and path.stat().st_size > 100:
        return Image.open(path).convert("RGB")
    url = provider["url"].format(z=z, x=x, y=y)
    data = fetch_url(url)
    img = Image.open(BytesIO(data)).convert("RGB")
    img.save(path, format="PNG")
    return img

def mosaic_tiles(
    provider: dict,
    west: float,
    south: float,
    east: float,
    north: float,
    zoom: int,
) -> tuple[np.ndarray, tuple[float, float, float, float]]:
    """Return RGB array and geographic extent (W,E,S,N) matching the mosaic."""
    tiles = list(mercantile.tiles(west, south, east, north, zooms=zoom))
    if not tiles:
        raise RuntimeError("no tiles for bbox")
    xmin = min(t.x for t in tiles)
    xmax = max(t.x for t in tiles)
    ymin = min(t.y for t in tiles)
    ymax = max(t.y for t in tiles)
    # sample size
    sample = get_tile(provider, zoom, tiles[0].x, tiles[0].y)
    tw, th = sample.size
    cols = xmax - xmin + 1
    rows = ymax - ymin + 1
    canvas = Image.new("RGB", (cols * tw, rows * th))
    for t in tiles:
        img = get_tile(provider, t.z, t.x, t.y)
        canvas.paste(img, ((t.x - xmin) * tw, (t.y - ymin) * th))
    # bounds of full tile grid
    ul = mercantile.ul(xmin, ymin, zoom)
    # lower-right corner of bottom-right tile
    br = mercantile.ul(xmax + 1, ymax + 1, zoom)
    # mercantile.ul is upper-left; br of next tile = SE corner of mosaic
    extent = (ul.lng, br.lng, br.lat, ul.lat)  # left, right, bottom, top for imshow
    return np.asarray(canvas), extent


def cache_basemap_raster(short: str, site: SiteSpec, provider: dict) -> dict:
    """Download (or reuse) a regional mosaic; write PNG + sidecar JSON."""
    case_dir = CACHE / short
    case_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{provider['id']}_z{site.zoom}"
    png = case_dir / f"{stem}.png"
    meta_path = case_dir / f"{stem}.json"
    w, s, e, n = site.map_bbox

    if png.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("extent_left_right_bottom_top") and meta.get("provider") == provider["id"]:
            print(f"  cache hit: {png.name}")
            return meta

    print(f"  downloading {provider['name']} tiles z={site.zoom} for {short} ...")
    arr, extent = mosaic_tiles(provider, w, s, e, n, site.zoom)
    Image.fromarray(arr).save(png, optimize=True)
    meta = {
        "case": short,
        "provider": provider["id"],
        "provider_name": provider["name"],
        "attribution": provider["attribution"],
        "zoom": site.zoom,
        "request_bbox_wsen": [w, s, e, n],
        "extent_left_right_bottom_top": list(extent),
        "png": str(png),
        # Tiles are Web Mercator; mosaic is displayed with lon/lat corner bounds.
        # Within this ~0.3° window the linear-lonlat vs true-Mercator pixel mismatch is ~20 m
        # (see diagnosis) — negligible vs km-scale schematic planform residuals.
        "crs": "EPSG:3857 tiles → geographic extent (W,E,S,N); approx. linear lon/lat display",
        "display_note": (
            "imshow(extent=lon/lat of mosaic corners). Not a full Mercator→geographic resample; "
            "max landmark shift in this bbox ≈20–25 m."
        ),
        "downloaded_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tile_cache": str(TILE_CACHE / provider["id"]),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote {png} ({png.stat().st_size // 1024} KB)")
    return meta


def load_cached_rgb(meta: dict) -> tuple[np.ndarray, tuple[float, float, float, float]]:
    arr = np.asarray(Image.open(meta["png"]).convert("RGB"))
    ext = tuple(meta["extent_left_right_bottom_top"])
    return arr, ext  # type: ignore[return-value]


def add_scale_bar(ax, lat_ref: float, length_km: float = 5.0, loc: str = "lower left") -> None:
    m_lon, _ = meters_per_deg(lat_ref)
    dx = (length_km * 1000.0) / m_lon
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    if loc == "lower left":
        sx = x0 + 0.05 * (x1 - x0)
        sy = y0 + 0.07 * (y1 - y0)
    else:
        sx = x1 - 0.05 * (x1 - x0) - dx
        sy = y0 + 0.07 * (y1 - y0)
    ax.plot([sx, sx + dx], [sy, sy], color="white", lw=4, zorder=20, solid_capstyle="butt")
    ax.plot([sx, sx + dx], [sy, sy], color="black", lw=2, zorder=21, solid_capstyle="butt")
    ax.text(
        sx + dx / 2,
        sy + 0.015 * (y1 - y0),
        f"{length_km:.0f} km",
        ha="center",
        va="bottom",
        color="white",
        fontsize=8,
        fontweight="bold",
        zorder=22,
        path_effects=[],
    )
    # black outline via twin text
    ax.text(
        sx + dx / 2,
        sy + 0.015 * (y1 - y0),
        f"{length_km:.0f} km",
        ha="center",
        va="bottom",
        color="black",
        fontsize=8,
        zorder=21,
        alpha=0.85,
    )


def plot_alignment_error(
    short: str,
    case_name: str,
    lon_c: np.ndarray,
    lat_c: np.ndarray,
    reg: dict,
    bathy: dict,
) -> str:
    """Along-channel lateral offset vs OSM reference (m)."""
    stats = reg["lateral_stats"]
    dists = stats.per_point_m
    dist_along = np.concatenate([[0.0], np.cumsum(bathy["dlx"][:-1])]) / 1000.0

    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.fill_between(dist_along, 0, dists / 1000.0, color="#f97316", alpha=0.25)
    ax.plot(dist_along, dists / 1000.0, color="#ea580c", lw=1.8, label="侧向偏移")
    ax.axhline(stats.mean_m / 1000.0, color="#2563eb", ls="--", lw=1.2, label=f"均值 {stats.mean_m/1000:.2f} km")
    ax.axhline(stats.p95_m / 1000.0, color="#7c3aed", ls=":", lw=1.2, label=f"P95 {stats.p95_m/1000:.2f} km")
    ax.set_xlabel("沿程距离 (km)")
    ax.set_ylabel("侧向偏移 (km)")
    base = reg.get("baseline_lateral", {})
    imp = reg.get("improved_lateral", {})
    ax.set_title(
        f"{case_name} — 模型中心线相对参考河道侧向偏移\n"
        f"参考：{reg['ref_label']} ｜ 配准：{reg['kind']} ｜ "
        f"改进前均值 {base.get('mean_m', '?')} m → 改进后 {imp.get('mean_m', '?')} m"
    )
    ax.grid(True, alpha=0.35)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    out = OUT_DIR / f"{short}_alignment_error.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return str(out)


def plot_case_basemap(short: str, case_name: str, case_dir: Path, geo: SiteGeo, bathy: dict) -> dict:
    site = SITES[short]
    x_e, y_n = xy_geo_from_phi(bathy["dlx"], bathy["phi0"])
    reg = register_planform(x_e, y_n, site, short)
    lon_c, lat_c = reg["lon"], reg["lat"]

    half = np.nan_to_num(bathy["surface_width"], nan=0.0) * 0.5
    if bathy["phi0"] is not None:
        # bank offsets in local frame before registration — approximate by converting
        # perpendicular in lon/lat via small local offset at each point using same rigid params
        nx = -np.cos(bathy["phi0"])
        ny = np.sin(bathy["phi0"])
    else:
        nx = np.zeros_like(x_e)
        ny = np.ones_like(y_n)
    # Rebuild banks with same registration: shift local, then apply same transform as centerline
    # Simpler: offset in geographic meters after registration using heading from consecutive points.
    lon_l = lon_c.copy()
    lat_l = lat_c.copy()
    lon_r = lon_c.copy()
    lat_r = lat_c.copy()
    for i in range(len(lon_c)):
        if i < len(lon_c) - 1:
            dlon = float(lon_c[i + 1] - lon_c[i])
            dlat = float(lat_c[i + 1] - lat_c[i])
        else:
            dlon = float(lon_c[i] - lon_c[i - 1])
            dlat = float(lat_c[i] - lat_c[i - 1])
        m_lon, m_lat = meters_per_deg(float(lat_c[i]))
        ex, ey = dlon * m_lon, dlat * m_lat
        elen = math.hypot(ex, ey) or 1.0
        # left normal
        lx, ly = -ey / elen, ex / elen
        w = float(half[i])
        lon_l[i] = lon_c[i] + (lx * w) / m_lon
        lat_l[i] = lat_c[i] + (ly * w) / m_lat
        lon_r[i] = lon_c[i] - (lx * w) / m_lon
        lat_r[i] = lat_c[i] - (ly * w) / m_lat

    # Cache real basemaps (imagery + topo with place names)
    meta_img = cache_basemap_raster(short, site, ESRI_IMAGERY)
    meta_topo = cache_basemap_raster(short, site, ESRI_TOPO)
    rgb_img, ext_img = load_cached_rgb(meta_img)
    rgb_topo, ext_topo = load_cached_rgb(meta_topo)

    fig, axes = plt.subplots(1, 2, figsize=(14.0, 6.8))

    # --- Left: regional satellite ---
    ax = axes[0]
    ax.imshow(rgb_img, extent=ext_img, origin="upper", interpolation="bilinear", zorder=0)
    ax.set_xlim(site.map_bbox[0], site.map_bbox[2])
    ax.set_ylim(site.map_bbox[1], site.map_bbox[3])
    ax.set_aspect(1.0 / max(math.cos(math.radians(site.map_bbox[1])), 0.2))
    ax.plot(lon_c, lat_c, color="#fbbf24", lw=2.2, zorder=5, label="模型中心线（配准叠置）")
    ax.plot(lon_c, lat_c, color="#111827", lw=0.7, zorder=5, alpha=0.8)
    for r in site.refs:
        marker = {"dam": "s", "mouth": "s", "source": "^", "mid": "o", "control": "x"}.get(r.role, "o")
        color = {"dam": "#ef4444", "mouth": "#ef4444", "source": "#22c55e", "mid": "#38bdf8", "control": "#f97316"}.get(
            r.role, "white"
        )
        ax.scatter([r.lon], [r.lat], c=color, marker=marker, s=55, zorder=7, edgecolors="k", linewidths=0.6)
        ax.annotate(
            r.name,
            (r.lon, r.lat),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=7.5,
            color="white",
            fontweight="bold",
            zorder=8,
        )
    ax.grid(True, color="white", alpha=0.35, linestyle=":")
    ax.set_xlabel("经度 Longitude (°)")
    ax.set_ylabel("纬度 Latitude (°)")
    ax.set_title(f"真实卫星底图（{ESRI_IMAGERY['name']} 本地缓存）")
    add_scale_bar(ax, float(np.mean(lat_c)), length_km=5.0 if short != "Columbia_Slough" else 3.0)
    handles = [
        Line2D([0], [0], color="#fbbf24", lw=2.2, label="模型中心线（示意叠置）"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#ef4444", markersize=8, label="坝/河口参考点"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="#22c55e", markersize=8, label="上游/源头参考"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#38bdf8", markersize=8, label="库区/中段参考"),
        Line2D([0], [0], marker="x", color="#f97316", markersize=8, label="w2_con LAT/LONG（非配准）"),
    ]
    ax.legend(handles=handles, loc="upper right", fontsize=7.5, framealpha=0.9)

    # --- Right: topo/named map + zoomed channel ---
    ax2 = axes[1]
    ax2.imshow(rgb_topo, extent=ext_topo, origin="upper", interpolation="bilinear", zorder=0)
    # zoom around registered channel + refs
    pad_lon = max(float(np.ptp(lon_c)) * 0.35, 0.03)
    pad_lat = max(float(np.ptp(lat_c)) * 0.35, 0.02)
    ref_lons = [r.lon for r in site.refs] + list(lon_c)
    ref_lats = [r.lat for r in site.refs] + list(lat_c)
    ax2.set_xlim(min(ref_lons) - pad_lon, max(ref_lons) + pad_lon)
    ax2.set_ylim(min(ref_lats) - pad_lat, max(ref_lats) + pad_lat)
    ax2.set_aspect(1.0 / max(math.cos(math.radians(float(np.mean(lat_c)))), 0.2))
    ax2.plot(lon_l, lat_l, color="#0ea5e9", lw=1.0, alpha=0.9, label="近似左岸")
    ax2.plot(lon_r, lat_r, color="#0ea5e9", lw=1.0, alpha=0.9, label="近似右岸")
    sc = ax2.scatter(
        lon_c,
        lat_c,
        c=bathy["depth_m"],
        cmap="viridis",
        s=28,
        zorder=6,
        edgecolors="k",
        linewidths=0.2,
    )
    ax2.plot(lon_c, lat_c, color="k", lw=0.8, alpha=0.7, zorder=5)
    segs = bathy["seg"]
    for idx in sorted({0, len(segs) // 2, len(segs) - 1}):
        ax2.annotate(
            f"seg{int(segs[idx])}",
            (lon_c[idx], lat_c[idx]),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=8,
            color="#111827",
            fontweight="bold",
            zorder=9,
        )
    for r in site.refs:
        if r.role == "control":
            continue
        ax2.scatter([r.lon], [r.lat], c="#ef4444", s=40, zorder=7, edgecolors="white", linewidths=0.8)
        ax2.annotate(r.name, (r.lon, r.lat), textcoords="offset points", xytext=(4, -10), fontsize=7, color="#7f1d1d")
    ax2.grid(True, alpha=0.35, linestyle=":")
    ax2.set_xlabel("经度 Longitude (°)")
    ax2.set_ylabel("纬度 Latitude (°)")
    ax2.set_title(f"地形/地名底图 + 分段叠置（{reg['precision_label']}）")
    cb = fig.colorbar(sc, ax=ax2, fraction=0.046, pad=0.02)
    cb.set_label("近似水深 (m)")
    add_scale_bar(ax2, float(np.mean(lat_c)), length_km=2.0 if short == "Columbia_Slough" else 3.0)
    ax2.legend(loc="best", fontsize=7.5, framealpha=0.92)

    resid = reg["residual_mid_m"]
    base_lat = reg.get("baseline_lateral", {})
    imp_lat = reg.get("improved_lateral", {})
    if base_lat and imp_lat:
        resid_txt = (
            f"侧向偏移（OSM参考）：改进前 均值{base_lat['mean_m']:.0f}m P95{base_lat['p95_m']:.0f}m → "
            f"改进后 均值{imp_lat['mean_m']:.0f}m P95{imp_lat['p95_m']:.0f}m"
        )
    elif reg["kind"].startswith("two_point") or "similarity" in reg["kind"]:
        resid_txt = "端点拟合到坝/口与上游参考；中间弯道残差=PHI0示意路径≠真实岸线"
    elif resid == resid:
        resid_txt = (
            f"模型中点相对库心参考≈{resid/1000:.1f} km"
            f"（刚性只锚坝+旋弦；库心≠模型中点，属示意误差量级）"
        )
    else:
        resid_txt = "n/a"
    i_deep = int(np.nanargmax(np.nan_to_num(bathy["depth_m"], nan=-1.0)))
    deep_near_anchor = abs(i_deep - reg["i_anchor"]) <= max(2, len(bathy["seg"]) // 10)
    orient_note = (
        f"锚点={'下游/end' if site.model_anchor_end == 'end' else '上游/start'}@"
        f"seg{int(bathy['seg'][reg['i_anchor']])}；最深seg{int(bathy['seg'][i_deep])}"
        + ("（与坝/口端一致）" if deep_near_anchor or site.anchor_role in {"mouth", "source"} else "（⚠与锚点远离）")
    )
    fig.suptitle(
        f"{case_name} — 真实区域底图与模型河道叠置（示意配准，非精密 GIS）\n"
        f"地点：{site.place} ｜ 配准：{reg['kind']} ｜ 旋转 {reg['angle_deg']:.1f}° ｜ "
        f"尺度×{reg['scale']:.3f} ｜ {resid_txt}\n{orient_note}",
        fontsize=10.5,
    )
    fig.text(
        0.5,
        0.008,
        f"底图：{ESRI_IMAGERY['name']} + {ESRI_TOPO['name']}（basemap_cache/{short}/；报告 Base64）。"
        f" 投影核验：Esri XYZ 为 Web Mercator，本图用瓦片角点 lon/lat 作 imshow extent；"
        f"本窗口内线性经纬度相对真墨卡托像素错位≈20–25 m，不是公里级偏航原因。"
        f" 偏差主因：PHI0/DLX 积分路径为模型几何示意 + 有限控制点配准。"
        f" {site.public_note}。"
        f" w2_con LAT/LONG 仅为太阳辐射单点（{geo.lat:.1f}°N, {abs(geo.lon):.1f}°W），不是分段坐标。"
        f" Attribution: {ESRI_IMAGERY['attribution']}; {ESRI_TOPO['attribution']}。",
        ha="center",
        va="bottom",
        fontsize=6.8,
        color="#374151",
    )
    fig.tight_layout(rect=[0, 0.045, 1, 0.88])
    out = OUT_DIR / f"{short}_watershed_basemap.png"
    fig.savefig(out, dpi=170)
    plt.close(fig)

    align_out = plot_alignment_error(short, case_name, lon_c, lat_c, reg, bathy)

    cmp_info = reg.get("alignment_comparison", {})
    return {
        "status": "ok",
        "file": str(out),
        "lat": geo.lat,
        "lon_west_positive": geo.lon_west_positive,
        "lon_signed": geo.lon,
        "geo_source": geo.source,
        "geo_note": geo.note,
        "place": site.place,
        "public_refs": [f"{r.name} ~{r.lat:.4f}, {r.lon:.4f} ({r.source})" for r in site.refs],
        "segments": int(len(bathy["seg"])),
        "bathy": Path(bathy["path"]).name,
        "basemap": (
            f"{ESRI_IMAGERY['name']} + {ESRI_TOPO['name']} "
            f"(local cache: basemap_cache/{short}/)"
        ),
        "basemap_cache_dir": str(CACHE / short),
        "tile_cache_dir": str(TILE_CACHE),
        "registration": reg["kind"],
        "registration_detail": {
            "angle_deg": round(reg["angle_deg"], 3) if reg["angle_deg"] == reg["angle_deg"] else None,
            "scale": round(reg["scale"], 5) if reg["scale"] == reg["scale"] else None,
            "residual_mid_m": None if resid != resid else round(float(resid), 1),
            "precision_label": reg["precision_label"],
            "anchor": f"{reg['anchor'].name} ({reg['anchor'].lat}, {reg['anchor'].lon})",
            "align": None
            if reg["align"] is None
            else f"{reg['align'].name} ({reg['align'].lat}, {reg['align'].lon})",
            "model_anchor_end": site.model_anchor_end,
            "i_anchor": int(reg["i_anchor"]),
            "i_deepest": int(i_deep),
            "deep_near_anchor": bool(deep_near_anchor),
            "reference_channel": reg["ref_label"],
            "baseline_lateral_m": reg.get("baseline_lateral"),
            "improved_lateral_m": reg.get("improved_lateral"),
            "alignment_method_selected": cmp_info.get("selected"),
            "alignment_all_methods": cmp_info.get("all_methods"),
            "phi0_convention": "clockwise from north (rad); ΔE=DLX·sin(PHI0), ΔN=DLX·cos(PHI0)",
            "residual_note": (
                "几何形状残差：PHI0/DLX 积分路径为模型示意，弯道幅度不必等于真实河道。"
                "配准残差：有限控制点相似/TPS 无法同时贴合端点与全路径。"
            ),
            "projection_check": (
                "Esri XYZ tiles are Web Mercator. Mosaic is shown with lon/lat corner "
                "extent (not full resample). Linear-lonlat vs true Mercator landmark mismatch ≈20–25 m."
            ),
        },
        "alignment_error_plot": align_out,
        "precision_status": (
            "示意叠置（真实底图 + OSM 参考河道 + 多控制点配准）。"
            "可信任：区域是否正确、端点方位是否大致合理、侧向偏移量级（相对 OSM）。"
            "不可信任：弯道与岸线的精密贴合、米级绝对位置。"
        ),
        "pending_gis": "分段端点实测大地坐标 / 官方模型 GIS 导出仍待补充（当前 OSM 河道 + 公开坝址）",
    }


def main() -> None:
    manifest_path = OUT_DIR / "figure_manifest.json"
    if manifest_path.exists():
        all_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        all_manifest = {"run_id": RUN_ID, "cases": {}}

    for case in CASES:
        case_dir = RUN_BASE / case.name
        man = all_manifest.setdefault("cases", {}).setdefault(case.short, {"case": case.name})
        if not case_dir.exists():
            man["watershed_basemap"] = {"status": "missing_case_dir"}
            continue
        geo = parse_w2_lat_lon(case_dir)
        bathy = parse_bathy(case_dir)
        if geo is None:
            man["watershed_basemap"] = {
                "status": "latlon_待补充",
                "note": "控制文件未解析到可用 LATITUDE/LONGITUDE",
            }
            print(f"{case.short}: LAT/LONG 待补充")
            continue
        if bathy is None:
            man["watershed_basemap"] = {"status": "missing_bathy"}
            continue
        print(f"basemap: {case.short}")
        info = plot_case_basemap(case.short, case.name, case_dir, geo, bathy)
        man["watershed_basemap"] = info
        print(f"  -> {info['file']}")

    all_manifest["run_id"] = RUN_ID
    all_manifest["basemap_method"] = {
        "primary": ESRI_IMAGERY["name"],
        "secondary": ESRI_TOPO["name"],
        "cache": str(CACHE),
        "offline_after_download": True,
        "note": "OSM tile CDN returned 403; using Esri World Topo Map for labeled panel",
    }
    manifest_path.write_text(json.dumps(all_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"WROTE {manifest_path}")


if __name__ == "__main__":
    main()
