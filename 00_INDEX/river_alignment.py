#!/usr/bin/env python3
"""Reference-channel alignment: OSM fetch, lateral offset metrics, multi-point registration.

Pure numpy/scipy (PyPy-compatible; no geopandas). Reference polylines cached under
analysis/basemap_cache/<case>/osm_waterways.geojson for offline reproducibility.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import requests
from scipy.interpolate import Rbf

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "CE-QUAL-W2-repro-alignment/1.1 (scientific; local cache)"})


@dataclass
class ControlPair:
    model_idx: int
    lon: float
    lat: float
    name: str
    weight: float = 1.0


@dataclass
class RegistrationResult:
    kind: str
    lon: np.ndarray
    lat: np.ndarray
    angle_deg: float
    scale: float
    params: dict = field(default_factory=dict)


@dataclass
class LateralStats:
    mean_m: float
    max_m: float
    p95_m: float
    rmse_m: float
    n: int
    per_point_m: np.ndarray
    ref_source: str


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


def fetch_osm_waterways(bbox: tuple[float, float, float, float], cache_path: Path) -> dict:
    """Download OSM waterway ways in bbox via Overpass; cache GeoJSON FeatureCollection."""
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    west, south, east, north = bbox
    query = f"""
    [out:json][timeout:90];
    (
      way["waterway"~"river|stream|canal|ditch"]({south},{west},{north},{east});
    );
    out body;
    >;
    out skel qt;
    """
    url = "https://overpass-api.de/api/interpreter"
    last_err: Optional[Exception] = None
    for attempt in range(4):
        try:
            resp = SESSION.post(url, data={"data": query}, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            break
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(2.0 * (attempt + 1))
    else:
        raise RuntimeError(f"Overpass failed: {last_err}")

    nodes = {el["id"]: (el["lon"], el["lat"]) for el in data.get("elements", []) if el["type"] == "node"}
    features = []
    for el in data.get("elements", []):
        if el["type"] != "way":
            continue
        coords = []
        for nid in el.get("nodes", []):
            if nid in nodes:
                lon, lat = nodes[nid]
                coords.append([lon, lat])
        if len(coords) >= 2:
            props = el.get("tags", {})
            props["osm_id"] = el["id"]
            features.append({"type": "Feature", "properties": props, "geometry": {"type": "LineString", "coordinates": coords}})

    fc = {
        "type": "FeatureCollection",
        "properties": {
            "source": "OpenStreetMap Overpass API",
            "bbox_wsen": list(bbox),
            "downloaded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "query": "waterway~river|stream|canal|ditch",
        },
        "features": features,
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(fc, ensure_ascii=False, indent=2), encoding="utf-8")
    return fc


def _polyline_length(coords: np.ndarray) -> float:
    if len(coords) < 2:
        return 0.0
    d = np.diff(coords, axis=0)
    return float(np.sum(np.hypot(d[:, 0], d[:, 1])))


def _point_line_dist_m(px: float, py: float, line_xy: np.ndarray, m_lon: float, m_lat: float) -> float:
    """Minimum distance from point (lon,lat) to polyline in local meters."""
    best = float("inf")
    for i in range(len(line_xy) - 1):
        x1, y1 = line_xy[i]
        x2, y2 = line_xy[i + 1]
        dx = (x2 - x1) * m_lon
        dy = (y2 - y1) * m_lat
        lx = (px - x1) * m_lon
        ly = (py - y1) * m_lat
        seg_len2 = dx * dx + dy * dy
        if seg_len2 < 1e-6:
            d = math.hypot(lx, ly)
        else:
            t = max(0.0, min(1.0, (lx * dx + ly * dy) / seg_len2))
            d = math.hypot(lx - t * dx, ly - t * dy)
        best = min(best, d)
    return best


def _merge_named_features(geojson: dict, name_hints: list[str]) -> Optional[np.ndarray]:
    """Merge OSM LineString features whose name matches any hint (case-insensitive)."""
    hints = [h.lower() for h in name_hints]
    segments: list[np.ndarray] = []
    for feat in geojson.get("features", []):
        props = feat.get("properties", {})
        name = str(props.get("name", "") or "").lower()
        if not any(h in name for h in hints):
            continue
        coords = np.array(feat["geometry"]["coordinates"], dtype=float)
        if len(coords) >= 2:
            segments.append(coords)

    if not segments:
        return None

    merged = segments.pop(0)
    while segments:
        best_i, best_d, best_mode = -1, float("inf"), "tail"
        for i, seg in enumerate(segments):
            candidates = [
                (math.hypot(*(merged[-1] - seg[0])), "tail"),
                (math.hypot(*(merged[-1] - seg[-1])), "tail_rev"),
                (math.hypot(*(merged[0] - seg[-1])), "head"),
                (math.hypot(*(merged[0] - seg[0])), "head_rev"),
            ]
            for dist, mode in candidates:
                if dist < best_d:
                    best_d, best_i, best_mode = dist, i, mode
        if best_i < 0:
            break
        seg = segments.pop(best_i)
        if best_mode == "tail":
            merged = np.vstack([merged, seg[1:]])
        elif best_mode == "tail_rev":
            merged = np.vstack([merged, seg[-2::-1]])
        elif best_mode == "head":
            merged = np.vstack([seg[:-1], merged])
        else:
            merged = np.vstack([seg[1:][::-1], merged])
    return merged


def _clip_polyline_between(
    coords: np.ndarray,
    anchor_lon: float,
    anchor_lat: float,
    align_lon: float,
    align_lat: float,
) -> np.ndarray:
    """Trim polyline to section between closest indices to two landmarks."""
    if len(coords) < 2:
        return coords
    d_a = np.hypot(coords[:, 0] - anchor_lon, coords[:, 1] - anchor_lat)
    d_b = np.hypot(coords[:, 0] - align_lon, coords[:, 1] - align_lat)
    ia, ib = int(np.argmin(d_a)), int(np.argmin(d_b))
    if ia <= ib:
        return coords[ia : ib + 1]
    return coords[ib : ia + 1][::-1]


def ref_endpoint_farthest_from(
    coords: np.ndarray,
    lon: float,
    lat: float,
) -> tuple[float, float]:
    """Return polyline endpoint (start or end) farther from a landmark."""
    d0 = math.hypot(coords[0, 0] - lon, coords[0, 1] - lat)
    d1 = math.hypot(coords[-1, 0] - lon, coords[-1, 1] - lat)
    if d0 >= d1:
        return float(coords[0, 0]), float(coords[0, 1])
    return float(coords[-1, 0]), float(coords[-1, 1])


def extract_reference_channel(
    geojson: dict,
    anchor_lon: float,
    anchor_lat: float,
    align_lon: float,
    align_lat: float,
    name_hints: Optional[list[str]] = None,
) -> tuple[np.ndarray, str]:
    """Pick best OSM LineString near both anchor and align landmarks."""
    name_hints = name_hints or []

    merged = _merge_named_features(geojson, name_hints)
    if merged is not None and len(merged) >= 2:
        lon_c, lat_c = merged[:, 0], merged[:, 1]
        d_anchor = float(np.min(np.hypot(lon_c - anchor_lon, lat_c - anchor_lat)))
        d_align = float(np.min(np.hypot(lon_c - align_lon, lat_c - align_lat)))
        # Named waterway: accept if dam/anchor end is near
        if d_anchor < 0.25 or d_align < 0.25:
            if d_align < 0.25:
                clipped = _clip_polyline_between(merged, anchor_lon, anchor_lat, align_lon, align_lat)
                if len(clipped) >= 2:
                    label = f"OSM merged {'/'.join(name_hints)} ({len(clipped)} pts clipped)"
                    return clipped, label
            label = f"OSM merged {'/'.join(name_hints)} ({len(merged)} pts)"
            return merged, label
    best_coords = None
    best_score = -1.0
    best_label = "none"

    for feat in geojson.get("features", []):
        coords = np.array(feat["geometry"]["coordinates"], dtype=float)
        if len(coords) < 2:
            continue
        props = feat.get("properties", {})
        name = str(props.get("name", "") or props.get("waterway", "waterway"))
        lon_c, lat_c = coords[:, 0], coords[:, 1]
        d_anchor = float(np.min(np.hypot(lon_c - anchor_lon, lat_c - anchor_lat)))
        d_align = float(np.min(np.hypot(lon_c - align_lon, lat_c - align_lat)))
        if d_anchor > 0.08 or d_align > 0.08:
            continue
        length = _polyline_length(coords)
        hint_bonus = 3.0 if any(h in name.lower() for h in [h.lower() for h in name_hints]) else 1.0
        score = length * hint_bonus / (1.0 + 100.0 * (d_anchor + d_align))
        if score > best_score:
            best_score = score
            best_coords = coords
            best_label = f"OSM {name} (id={props.get('osm_id', '?')})"

    if best_coords is None:
        segments = []
        for feat in geojson.get("features", []):
            coords = np.array(feat["geometry"]["coordinates"], dtype=float)
            if len(coords) < 2:
                continue
            lon_c, lat_c = coords[:, 0], coords[:, 1]
            if float(np.min(np.hypot(lon_c - anchor_lon, lat_c - anchor_lat))) < 0.15:
                segments.append(coords)
        if segments:
            best_coords = max(segments, key=len)
            best_label = "OSM merged nearby waterways"
        else:
            best_coords = np.array([[align_lon, align_lat], [anchor_lon, anchor_lat]])
            best_label = "landmark chord (no OSM match)"

    return best_coords, best_label


def sample_polyline_by_fraction(coords: np.ndarray, fractions: np.ndarray) -> np.ndarray:
    """Return (lon,lat) at arc-length fractions along polyline."""
    seg_len = []
    for i in range(len(coords) - 1):
        seg_len.append(math.hypot(coords[i + 1, 0] - coords[i, 0], coords[i + 1, 1] - coords[i, 1]))
    cum = np.concatenate([[0.0], np.cumsum(seg_len)])
    total = cum[-1] if cum[-1] > 0 else 1.0
    out = np.zeros((len(fractions), 2))
    for j, f in enumerate(fractions):
        target = f * total
        idx = int(np.searchsorted(cum, target, side="right") - 1)
        idx = max(0, min(idx, len(coords) - 2))
        seg_f = (target - cum[idx]) / max(cum[idx + 1] - cum[idx], 1e-12)
        out[j] = coords[idx] * (1 - seg_f) + coords[idx + 1] * seg_f
    return out


def lateral_offset_stats(
    lon: np.ndarray,
    lat: np.ndarray,
    ref_coords: np.ndarray,
    ref_label: str,
) -> LateralStats:
    lat0 = float(np.mean(lat))
    m_lon, m_lat = meters_per_deg(lat0)
    dists = np.array([_point_line_dist_m(float(lon[i]), float(lat[i]), ref_coords, m_lon, m_lat) for i in range(len(lon))])
    return LateralStats(
        mean_m=float(np.mean(dists)),
        max_m=float(np.max(dists)),
        p95_m=float(np.percentile(dists, 95)),
        rmse_m=float(np.sqrt(np.mean(dists**2))),
        n=len(dists),
        per_point_m=dists,
        ref_source=ref_label,
    )


def register_two_point_similarity(
    x_e: np.ndarray,
    y_n: np.ndarray,
    i_anchor: int,
    i_align: int,
    anchor_lon: float,
    anchor_lat: float,
    align_lon: float,
    align_lat: float,
) -> RegistrationResult:
    lon0, lat0 = anchor_lon, anchor_lat
    xa, ya = float(x_e[i_anchor]), float(y_n[i_anchor])
    xb, yb = float(x_e[i_align]), float(y_n[i_align])
    gx, gy = lonlat_to_local_m(align_lon, align_lat, lon0, lat0)
    mx, my = xb - xa, yb - ya
    m_len = math.hypot(mx, my)
    g_len = math.hypot(gx, gy)
    ang = math.atan2(gy, gx) - math.atan2(my, mx) if m_len > 1 else 0.0
    scale = g_len / m_len if m_len > 1 else 1.0
    xs, ys = x_e - xa, y_n - ya
    xr, yr = _rot(xs * scale, ys * scale, ang)
    lon, lat = local_m_to_lonlat(xr, yr, lon0, lat0)
    return RegistrationResult(
        kind="two_point_similarity",
        lon=lon,
        lat=lat,
        angle_deg=math.degrees(ang),
        scale=scale,
        params={"i_anchor": i_anchor, "i_align": i_align},
    )


def register_landmark_rigid(
    x_e: np.ndarray,
    y_n: np.ndarray,
    i_anchor: int,
    i_align: int,
    anchor_lon: float,
    anchor_lat: float,
    align_lon: float,
    align_lat: float,
) -> RegistrationResult:
    lon0, lat0 = anchor_lon, anchor_lat
    xa, ya = float(x_e[i_anchor]), float(y_n[i_anchor])
    xb, yb = float(x_e[i_align]), float(y_n[i_align])
    gx, gy = lonlat_to_local_m(align_lon, align_lat, lon0, lat0)
    mx, my = xb - xa, yb - ya
    ang = math.atan2(gy, gx) - math.atan2(my, mx) if math.hypot(mx, my) > 1 else 0.0
    xs, ys = x_e - xa, y_n - ya
    xr, yr = _rot(xs, ys, ang)
    lon, lat = local_m_to_lonlat(xr, yr, lon0, lat0)
    return RegistrationResult(
        kind="landmark_rigid",
        lon=lon,
        lat=lat,
        angle_deg=math.degrees(ang),
        scale=1.0,
        params={"i_anchor": i_anchor, "i_align": i_align},
    )


def register_multi_similarity(
    x_e: np.ndarray,
    y_n: np.ndarray,
    pairs: list[ControlPair],
    lon0: float,
    lat0: float,
) -> RegistrationResult:
    """Least-squares 2D similarity from weighted control pairs."""
    src = []
    dst = []
    wts = []
    for p in pairs:
        src.append([float(x_e[p.model_idx]), float(y_n[p.model_idx])])
        xe, ye = lonlat_to_local_m(p.lon, p.lat, lon0, lat0)
        dst.append([xe, ye])
        wts.append(p.weight)
    src = np.array(src)
    dst = np.array(dst)
    wts = np.array(wts)
    wts = wts / np.sum(wts)

    # centroid
    cs = np.average(src, axis=0, weights=wts)
    cd = np.average(dst, axis=0, weights=wts)
    src_c = src - cs
    dst_c = dst - cd

    # Procrustes for similarity
    h = (src_c * wts[:, None]).T @ dst_c
    u, svals, vt = np.linalg.svd(h)
    r = vt.T @ u.T
    if np.linalg.det(r) < 0:
        vt[-1, :] *= -1
        r = vt.T @ u.T
    var_src = np.sum(wts * np.sum(src_c**2, axis=1))
    scale = float(np.sum(svals) / var_src) if var_src > 1e-9 else 1.0
    ang = math.atan2(r[1, 0], r[0, 0])

    xs = x_e - cs[0]
    ys = y_n - cs[1]
    xr, yr = _rot(xs * scale, ys * scale, ang)
    xr = xr + cd[0]
    yr = yr + cd[1]
    lon, lat = local_m_to_lonlat(xr, yr, lon0, lat0)
    return RegistrationResult(
        kind=f"multi_similarity_{len(pairs)}pt",
        lon=lon,
        lat=lat,
        angle_deg=math.degrees(ang),
        scale=scale,
        params={"n_control": len(pairs), "control_names": [p.name for p in pairs]},
    )


def register_tps(
    x_e: np.ndarray,
    y_n: np.ndarray,
    pairs: list[ControlPair],
    lon0: float,
    lat0: float,
    smooth: float = 0.5,
) -> RegistrationResult:
    """Thin-plate spline warp (scipy Rbf) from model local EN to geo local EN."""
    src_x = np.array([float(x_e[p.model_idx]) for p in pairs])
    src_y = np.array([float(y_n[p.model_idx]) for p in pairs])
    dst_x = []
    dst_y = []
    for p in pairs:
        xe, ye = lonlat_to_local_m(p.lon, p.lat, lon0, lat0)
        dst_x.append(xe)
        dst_y.append(ye)
    dst_x = np.array(dst_x)
    dst_y = np.array(dst_y)

    rbf_x = Rbf(src_x, src_y, dst_x, function="thin_plate", smooth=smooth)
    rbf_y = Rbf(src_x, src_y, dst_y, function="thin_plate", smooth=smooth)
    xr = rbf_x(x_e, y_n)
    yr = rbf_y(x_e, y_n)
    lon, lat = local_m_to_lonlat(xr, yr, lon0, lat0)
    return RegistrationResult(
        kind=f"tps_{len(pairs)}pt",
        lon=lon,
        lat=lat,
        angle_deg=float("nan"),
        scale=float("nan"),
        params={"n_control": len(pairs), "smooth": smooth, "control_names": [p.name for p in pairs]},
    )


def endpoint_errors_m(
    lon: np.ndarray,
    lat: np.ndarray,
    i_a: int,
    i_b: int,
    lon_a: float,
    lat_a: float,
    lon_b: float,
    lat_b: float,
) -> tuple[float, float]:
    lat0 = float(np.mean(lat))
    m_lon, m_lat = meters_per_deg(lat0)
    ea = math.hypot((lon[i_a] - lon_a) * m_lon, (lat[i_a] - lat_a) * m_lat)
    eb = math.hypot((lon[i_b] - lon_b) * m_lon, (lat[i_b] - lat_b) * m_lat)
    return ea, eb


def choose_best_registration(
    x_e: np.ndarray,
    y_n: np.ndarray,
    ref_coords: np.ndarray,
    ref_label: str,
    i_anchor: int,
    i_align: int,
    anchor_lon: float,
    anchor_lat: float,
    align_lon: float,
    align_lat: float,
    extra_pairs: list[ControlPair],
    baseline_kind: str,
) -> tuple[RegistrationResult, LateralStats, dict]:
    """Try several methods; pick lowest mean lateral offset with endpoint error < 800 m."""
    candidates: list[tuple[RegistrationResult, str]] = []

    if baseline_kind == "landmark_rigid":
        candidates.append((
            register_landmark_rigid(x_e, y_n, i_anchor, i_align, anchor_lon, anchor_lat, align_lon, align_lat),
            "baseline_rigid",
        ))
    else:
        candidates.append((
            register_two_point_similarity(x_e, y_n, i_anchor, i_align, anchor_lon, anchor_lat, align_lon, align_lat),
            "baseline_two_point",
        ))

    lon0, lat0 = anchor_lon, anchor_lat
    # 3-point: anchor + align + mid landmark
    if extra_pairs:
        pairs3 = [
            ControlPair(i_anchor, anchor_lon, anchor_lat, "anchor", weight=3.0),
            ControlPair(i_align, align_lon, align_lat, "align", weight=3.0),
        ]
        for p in extra_pairs[:1]:
            pairs3.append(p)
        candidates.append((register_multi_similarity(x_e, y_n, pairs3, lon0, lat0), "multi_3pt"))

        pairs_all = [
            ControlPair(i_anchor, anchor_lon, anchor_lat, "anchor", weight=3.0),
            ControlPair(i_align, align_lon, align_lat, "align", weight=3.0),
        ] + extra_pairs
        if len(pairs_all) >= 3:
            candidates.append((register_multi_similarity(x_e, y_n, pairs_all, lon0, lat0), "multi_all"))
            if len(pairs_all) >= 4:
                candidates.append((register_tps(x_e, y_n, pairs_all, lon0, lat0, smooth=1.0), "tps"))

    # Arc-length matched pairs from reference channel (interior shape)
    n = len(x_e)
    fracs = np.array([0.25, 0.5, 0.75])
    ref_pts = sample_polyline_by_fraction(ref_coords, fracs)
    arc_pairs = [
        ControlPair(i_anchor, anchor_lon, anchor_lat, "anchor", weight=4.0),
        ControlPair(i_align, align_lon, align_lat, "align", weight=4.0),
    ]
    for f, (rlon, rlat) in zip(fracs, ref_pts):
        idx = int(round(f * (n - 1)))
        arc_pairs.append(ControlPair(idx, float(rlon), float(rlat), f"arc_{f:.2f}", weight=1.5))
    candidates.append((register_multi_similarity(x_e, y_n, arc_pairs, lon0, lat0), "multi_arc"))
    if len(arc_pairs) >= 5:
        candidates.append((register_tps(x_e, y_n, arc_pairs, lon0, lat0, smooth=2.0), "tps_arc"))

    best_reg = candidates[0][0]
    best_stats = lateral_offset_stats(best_reg.lon, best_reg.lat, ref_coords, ref_label)
    best_tag = candidates[0][1]
    baseline_reg = candidates[0][0]
    baseline_stats = best_stats

    comparison = {}
    for reg, tag in candidates:
        stats = lateral_offset_stats(reg.lon, reg.lat, ref_coords, ref_label)
        ea, eb = endpoint_errors_m(
            reg.lon, reg.lat, i_anchor, i_align,
            anchor_lon, anchor_lat, align_lon, align_lat,
        )
        comparison[tag] = {
            "kind": reg.kind,
            "mean_m": round(stats.mean_m, 1),
            "max_m": round(stats.max_m, 1),
            "p95_m": round(stats.p95_m, 1),
            "rmse_m": round(stats.rmse_m, 1),
            "endpoint_err_a_m": round(ea, 1),
            "endpoint_err_b_m": round(eb, 1),
        }
        # Prefer lower mean lateral if endpoints stay within 800 m (hard anchors weighted heavily)
        endpoint_ok = ea < 800 and eb < 800
        score = stats.mean_m + 0.3 * stats.p95_m + (500.0 if not endpoint_ok else 0.0)
        best_score = best_stats.mean_m + 0.3 * best_stats.p95_m + (
            500.0 if endpoint_errors_m(best_reg.lon, best_reg.lat, i_anchor, i_align, anchor_lon, anchor_lat, align_lon, align_lat)[0] >= 800
            else 0.0
        )
        if score < best_score:
            best_reg, best_stats, best_tag = reg, stats, tag

    return best_reg, best_stats, {
        "selected": best_tag,
        "baseline": {
            "kind": baseline_reg.kind,
            "mean_m": round(baseline_stats.mean_m, 1),
            "max_m": round(baseline_stats.max_m, 1),
            "p95_m": round(baseline_stats.p95_m, 1),
        },
        "improved": {
            "kind": best_reg.kind,
            "mean_m": round(best_stats.mean_m, 1),
            "max_m": round(best_stats.max_m, 1),
            "p95_m": round(best_stats.p95_m, 1),
        },
        "all_methods": comparison,
        "ref_source": ref_label,
    }
