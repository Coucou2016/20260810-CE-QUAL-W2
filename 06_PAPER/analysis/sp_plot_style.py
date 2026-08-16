"""Shared SciencePlots + Times New Roman style for P1 paper/report figures.

Uses ``science`` + ``no-latex`` so Windows hosts without a full TeX stack still
render. Latin text prefers Times New Roman; CJK glyphs fall back to YaHei/SimHei
when titles retain Chinese from legacy plotters.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cycler import cycler

# Colorblind-friendly (Okabe–Ito-ish) cycle
_CB_CYCLE = cycler(
    color=[
        "#0072B2",  # blue
        "#E69F00",  # orange
        "#009E73",  # green
        "#CC79A7",  # reddish purple
        "#56B4E9",  # sky blue
        "#D55E00",  # vermillion
        "#F0E442",  # yellow
        "#000000",  # black
    ]
)

_STYLE_APPLIED = False
_SAVEFIG_PATCHED = False
_SUBPLOTS_PATCHED = False


def apply_style(*, force: bool = False) -> None:
    """Apply SciencePlots (no-latex) + Times New Roman journal sizing."""
    global _STYLE_APPLIED
    if _STYLE_APPLIED and not force:
        # Still refresh rc in case a caller overwrote fonts.
        pass
    import scienceplots  # noqa: F401  — registers styles

    plt.style.use(["science", "no-latex"])
    # font.family as a list enables glyph-level fallback (mpl ≥3.6): Latin → TNR, CJK → YaHei.
    plt.rcParams.update(
        {
            "font.family": [
                "Times New Roman",
                "Microsoft YaHei",
                "SimHei",
                "DejaVu Serif",
            ],
            "font.serif": [
                "Times New Roman",
                "Times",
                "Microsoft YaHei",
                "SimHei",
                "DejaVu Serif",
            ],
            "font.sans-serif": [
                "Microsoft YaHei",
                "SimHei",
                "DejaVu Sans",
            ],
            "font.size": 9,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "figure.titlesize": 11,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "legend.title_fontsize": 9,
            "axes.unicode_minus": False,
            "axes.prop_cycle": _CB_CYCLE,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    _STYLE_APPLIED = True


def patch_pyplot_hooks() -> None:
    """Re-apply style on every figure creation; force dpi≥300 on save."""
    global _SAVEFIG_PATCHED, _SUBPLOTS_PATCHED
    apply_style()

    if not _SUBPLOTS_PATCHED:
        _subplots = plt.subplots
        _figure = plt.figure

        def subplots(*args, **kwargs):
            apply_style(force=True)
            return _subplots(*args, **kwargs)

        def figure(*args, **kwargs):
            apply_style(force=True)
            return _figure(*args, **kwargs)

        plt.subplots = subplots  # type: ignore[assignment]
        plt.figure = figure  # type: ignore[assignment]
        _SUBPLOTS_PATCHED = True

    if not _SAVEFIG_PATCHED:
        from matplotlib.figure import Figure

        _orig = Figure.savefig

        def savefig(self, fname, *args, **kwargs):
            dpi = kwargs.get("dpi", None)
            if dpi is None or (isinstance(dpi, (int, float)) and dpi < 300):
                kwargs["dpi"] = 300
            kwargs.setdefault("bbox_inches", "tight")
            return _orig(self, fname, *args, **kwargs)

        Figure.savefig = savefig  # type: ignore[method-assign]
        _SAVEFIG_PATCHED = True


def save_fig(fig: plt.Figure, path: Path | str, *, dpi: int = 300) -> Path:
    """Save figure at journal DPI and close."""
    apply_style(force=True)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=max(dpi, 300), bbox_inches="tight")
    plt.close(fig)
    return out
