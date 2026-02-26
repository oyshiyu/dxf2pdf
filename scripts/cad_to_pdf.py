#!/usr/bin/env python3
"""Convert CAD drawings to PDF (direct DXF support, DWG fallback guidance)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Tuple


INSTALL_HINT = (
    "Missing Python dependencies. Install them in your working directory with:\n"
    "  python3 -m venv .cad2pdf-venv\n"
    "  ./.cad2pdf-venv/bin/pip install ezdxf matplotlib"
)


def parse_size_inches(text: str) -> Tuple[float, float]:
    for sep in ("x", "X", "*", ","):
        if sep in text:
            left, right = text.split(sep, 1)
            width = float(left.strip())
            height = float(right.strip())
            if width <= 0 or height <= 0:
                raise argparse.ArgumentTypeError("size values must be > 0")
            return (width, height)
    raise argparse.ArgumentTypeError("expected format WxH, e.g. 11x17")


def positive_float(text: str) -> float:
    try:
        value = float(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number") from exc
    if value <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return value


def nonnegative_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if value < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return value


def estimated_text_units(text: str) -> float:
    units = 0.0
    for ch in text:
        units += estimated_char_units(ch)
    return units


def estimated_char_units(ch: str) -> float:
    if is_cjk_char(ch):
        return 1.0
    if ch.isascii() and (ch.isalpha() or ch.isdigit()):
        return 0.62
    if ch in {"#", "/", "-", "_", ".", ":"}:
        return 0.45
    if ch.isspace():
        return 0.35
    return 0.8


def ensure_dxf_dependencies():
    try:
        import ezdxf  # type: ignore
        from ezdxf.addons.drawing import matplotlib as ezdxf_mpl  # type: ignore
    except ImportError as exc:  # pragma: no cover - runtime environment dependent
        raise RuntimeError(INSTALL_HINT) from exc
    return ezdxf, ezdxf_mpl


def parse_font_family_list(spec: Optional[str]) -> list[str]:
    if not spec:
        return []
    names: list[str] = []
    for part in spec.replace(";", ",").split(","):
        name = part.strip()
        if name and name not in names:
            names.append(name)
    return names


def default_cjk_font_families() -> list[str]:
    if sys.platform.startswith("win"):
        return [
            "Microsoft YaHei",
            "SimHei",
            "SimSun",
            "NSimSun",
            "KaiTi",
            "FangSong",
        ]
    if sys.platform == "darwin":
        return [
            "PingFang SC",
            "Hiragino Sans GB",
            "STHeiti",
            "Heiti SC",
            "Songti SC",
        ]
    return [
        "Noto Sans CJK SC",
        "WenQuanYi Zen Hei",
        "AR PL UKai CN",
        "AR PL UMing CN",
    ]


def configure_matplotlib_fonts(
    *,
    font_family_spec: Optional[str],
    font_file: Optional[Path],
) -> None:
    requested = parse_font_family_list(font_family_spec)
    auto_fallback = False

    if not requested and font_file is None and sys.platform.startswith("win"):
        requested = default_cjk_font_families()
        auto_fallback = True

    if not requested and font_file is None:
        return

    try:
        import matplotlib  # type: ignore
        from matplotlib import font_manager  # type: ignore
    except ImportError as exc:  # pragma: no cover - runtime environment dependent
        raise RuntimeError(INSTALL_HINT) from exc

    if font_file is not None:
        resolved = Path(font_file).expanduser()
        if not resolved.is_file():
            raise ValueError(f"Font file not found: {resolved}")
        try:
            font_manager.fontManager.addfont(str(resolved))
        except Exception as exc:
            raise ValueError(f"Failed to load font file: {resolved} ({exc})") from exc

        try:
            loaded_name = font_manager.FontProperties(fname=str(resolved)).get_name()
        except Exception:
            loaded_name = ""
        if loaded_name and loaded_name not in requested:
            requested.insert(0, loaded_name)
        elif not requested:
            raise ValueError(
                "Unable to determine font family name from --font-file. "
                "Please also pass --font-family."
            )

    if not requested:
        return

    existing_sans = matplotlib.rcParams.get("font.sans-serif", [])
    if isinstance(existing_sans, str):
        existing_sans_list = [existing_sans]
    else:
        existing_sans_list = [str(name) for name in existing_sans]

    merged: list[str] = []
    for name in requested + existing_sans_list:
        if name and name not in merged:
            merged.append(name)

    matplotlib.rcParams["font.family"] = ["sans-serif"]
    matplotlib.rcParams["font.sans-serif"] = merged
    matplotlib.rcParams["axes.unicode_minus"] = False

    installed_names = {entry.name for entry in font_manager.fontManager.ttflist}
    matched = [name for name in requested if name in installed_names]

    if auto_fallback:
        print(f"Auto font fallback (Windows): {', '.join(requested)}")
    else:
        print(f"Matplotlib font preference: {', '.join(requested)}")

    if matched:
        print(f"Matplotlib font matches: {', '.join(matched)}")
    else:
        print(
            "Warning: None of the requested fonts were found by matplotlib. "
            "Chinese text may not render correctly. Try --font-family or --font-file.",
            file=sys.stderr,
        )


def list_layouts(doc) -> list[str]:
    names = []
    for name in doc.layout_names_in_taborder():
        if name.lower() == "model":
            names.append("Model (modelspace)")
        else:
            names.append(f"{name} (paperspace)")
    return names


def choose_layout(doc, layout_spec: str):
    spec = layout_spec.strip().lower()
    if spec == "auto":
        for name in doc.layout_names_in_taborder():
            if name.lower() != "model":
                return doc.layouts.get(name)
        return doc.modelspace()
    if spec == "modelspace":
        return doc.modelspace()
    if spec == "paperspace":
        for name in doc.layout_names_in_taborder():
            if name.lower() != "model":
                return doc.layouts.get(name)
        raise ValueError("No paperspace layout found.")

    for name in doc.layout_names_in_taborder():
        if name == layout_spec or name.lower() == spec:
            if name.lower() == "model":
                return doc.modelspace()
            return doc.layouts.get(name)
    raise ValueError(
        f"Layout '{layout_spec}' not found. Run with --list-layouts to inspect choices."
    )


def describe_layout(layout) -> str:
    if getattr(layout, "is_modelspace", False):
        return "Model (modelspace)"
    return f"{getattr(layout, 'name', 'Unknown')} (paperspace)"


def dwg_message(input_path: Path) -> str:
    dxf_candidate = input_path.with_suffix(".dxf")
    lines = [
        f"DWG input is not converted directly by this script: {input_path}",
        "Recommended workflow:",
        "  1. Export or convert DWG to DXF using AutoCAD/BricsCAD/QCAD/ODA File Converter.",
        "  2. Run this script again on the resulting .dxf file.",
    ]
    if dxf_candidate.exists():
        lines.append(f"Detected sibling DXF candidate: {dxf_candidate}")
        lines.append("Try running the script with that DXF file.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert CAD drawings to PDF (DXF direct support; DWG fallback guidance)."
    )
    parser.add_argument("input", help="Path to .dxf or .dwg")
    parser.add_argument(
        "-o",
        "--output",
        help="Output PDF path (default: same basename as input)",
    )
    parser.add_argument(
        "--layout",
        default="auto",
        help="auto (default), modelspace, paperspace, or an exact layout name",
    )
    parser.add_argument(
        "--list-layouts",
        action="store_true",
        help="List layouts in a DXF and exit",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Render DPI for PDF export (default: 300)",
    )
    parser.add_argument(
        "--size-inches",
        type=parse_size_inches,
        help="Fixed canvas size in inches (e.g. 11x17).",
    )
    parser.add_argument(
        "--mtext-width-scale",
        type=positive_float,
        default=1.0,
        help=(
            "Scale MTEXT width before export (<1 wraps earlier into more lines, "
            ">1 wraps less). Default: 1.0"
        ),
    )
    parser.add_argument(
        "--mtext-line-spacing-scale",
        type=positive_float,
        default=1.0,
        help=(
            "Multiply MTEXT line spacing factor before export (e.g. 1.15). "
            "Default: 1.0"
        ),
    )
    parser.add_argument(
        "--mtext-force-wrap-cjk-chars",
        type=nonnegative_int,
        default=0,
        help=(
            "Force-wrap plain CJK MTEXT by character count (0 disables). "
            "Example: 10 or 12"
        ),
    )
    parser.add_argument(
        "--mtext-smart-wrap-cjk-collision",
        action="store_true",
        help=(
            "Only wrap plain CJK MTEXT when a nearby same-row label is likely to "
            "collide horizontally."
        ),
    )
    parser.add_argument(
        "--mtext-smart-wrap-cjk-chars",
        type=nonnegative_int,
        default=0,
        help=(
            "When smart collision wrapping triggers, wrap plain CJK MTEXT by this "
            "char count (0 = auto by estimated width)."
        ),
    )
    parser.add_argument(
        "--bg",
        help="Background color override (default: #FFFFFF; hex only, e.g. #FFFFFF)",
    )
    parser.add_argument(
        "--fg",
        help="Foreground color override for ACI=7 (requires --bg; hex only, e.g. #000000)",
    )
    parser.add_argument(
        "--font-family",
        help=(
            "Preferred matplotlib font family (or comma-separated fallbacks) for text "
            "rendering, e.g. 'Microsoft YaHei,SimSun'."
        ),
    )
    parser.add_argument(
        "--font-file",
        help=(
            "Path to a TTF/OTF/TTC font file to register before export. "
            "Use with --font-family if family detection fails."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing output PDF",
    )
    return parser


def convert_dxf(
    input_path: Path,
    output_path: Path,
    *,
    layout_spec: str,
    list_only: bool,
    dpi: int,
    size_inches: Optional[Tuple[float, float]],
    mtext_width_scale: float,
    mtext_line_spacing_scale: float,
    mtext_force_wrap_cjk_chars: int,
    mtext_smart_wrap_cjk_collision: bool,
    mtext_smart_wrap_cjk_chars: int,
    bg: Optional[str],
    fg: Optional[str],
    font_family: Optional[str],
    font_file: Optional[Path],
    force: bool,
) -> int:
    ezdxf, ezdxf_mpl = ensure_dxf_dependencies()

    try:
        doc = ezdxf.readfile(input_path)
    except FileNotFoundError:
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Failed to read DXF: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"DXF parsing failed: {exc}", file=sys.stderr)
        return 2

    if list_only:
        print("Layouts:")
        for name in list_layouts(doc):
            print(f"  - {name}")
        return 0

    if output_path.exists() and not force:
        print(f"Output exists: {output_path} (use --force to overwrite)", file=sys.stderr)
        return 3

    try:
        layout = choose_layout(doc, layout_spec)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 4

    print(f"Using layout: {describe_layout(layout)}")

    adjusted_mtext, forced_wraps, smart_wraps = tune_mtext_for_export(
        layout,
        width_scale=mtext_width_scale,
        line_spacing_scale=mtext_line_spacing_scale,
        force_wrap_cjk_chars=mtext_force_wrap_cjk_chars,
        smart_wrap_cjk_collision=mtext_smart_wrap_cjk_collision,
        smart_wrap_cjk_chars=mtext_smart_wrap_cjk_chars,
    )
    if adjusted_mtext:
        print(
            "Adjusted MTEXT entities: "
            f"{adjusted_mtext} "
            f"(width x{mtext_width_scale:g}, line-spacing x{mtext_line_spacing_scale:g})"
        )
    if forced_wraps:
        print(
            "Forced CJK wraps in MTEXT: "
            f"{forced_wraps} (max chars per line={mtext_force_wrap_cjk_chars})"
        )
    if smart_wraps:
        msg = f"Collision-triggered CJK wraps in MTEXT: {smart_wraps}"
        if mtext_smart_wrap_cjk_chars > 0:
            msg += f" (wrap chars={mtext_smart_wrap_cjk_chars})"
        print(msg)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    effective_bg = "#FFFFFF" if bg is None else bg
    try:
        configure_matplotlib_fonts(
            font_family_spec=font_family,
            font_file=font_file,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 4
    try:
        ezdxf_mpl.qsave(
            layout,
            output_path,
            dpi=dpi,
            bg=effective_bg,
            fg=fg,
            size_inches=size_inches,
        )
    except Exception as exc:
        print(f"PDF export failed: {exc}", file=sys.stderr)
        return 5

    size = output_path.stat().st_size if output_path.exists() else 0
    print(f"Exported PDF: {output_path} ({size} bytes)")
    return 0


def is_cjk_char(ch: str) -> bool:
    code = ord(ch)
    return (
        0x3400 <= code <= 0x4DBF  # CJK Ext-A
        or 0x4E00 <= code <= 0x9FFF  # CJK Unified
        or 0xF900 <= code <= 0xFAFF  # CJK Compatibility
    )


def contains_cjk(text: str) -> bool:
    return any(is_cjk_char(ch) for ch in text)


def is_plain_cjk_wrap_candidate(entity) -> bool:
    if float(getattr(entity.dxf, "rotation", 0.0) or 0.0) != 0.0:
        return False
    raw_text = getattr(entity, "text", None)
    if not isinstance(raw_text, str):
        return False
    if "\\" in raw_text:
        # Skip formatted MTEXT (\P, \U+, etc.) to avoid breaking formatting codes.
        return False
    if not raw_text or not contains_cjk(raw_text):
        return False
    if "\n" in raw_text or "\r" in raw_text:
        return False
    return True


def wrap_plain_text_by_chars(text: str, max_chars: int) -> tuple[str, bool]:
    if max_chars <= 0 or len(text) <= max_chars:
        return text, False
    if "\n" in text or "\r" in text:
        return text, False

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        end = adjust_wrap_break_index(text, start, end)
        chunks.append(text[start:end])
        start = end

    if len(chunks) <= 1:
        return text, False
    return "\\P".join(chunks), True


def adjust_wrap_break_index(text: str, start: int, end: int) -> int:
    if end >= len(text):
        return end
    # Prefer breaking before delimiters close to the boundary (e.g. "#3").
    search_start = max(start + 1, end - 4)
    preferred = None
    for idx in range(end, search_start - 1, -1):
        ch = text[idx - 1]
        if ch in {"#", "（", "(", "）", ")", "/", "-", " "}:
            preferred = idx - 1
            break
    if preferred is not None and preferred > start:
        return preferred
    return end


def wrap_plain_text_by_available_units(
    text: str,
    *,
    max_units_per_line: float,
    max_chars_per_line: int = 0,
) -> tuple[str, bool]:
    """Wrap plain text by estimated rendered width.

    Use `max_chars_per_line` as an optional cap (0 disables the cap).
    """
    if max_units_per_line <= 0:
        return text, False
    if "\n" in text or "\r" in text:
        return text, False

    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        units = 0.0
        count = 0
        end = start
        while end < n:
            ch = text[end]
            next_units = units + estimated_char_units(ch)
            next_count = count + 1
            if count > 0 and next_units > max_units_per_line:
                break
            if max_chars_per_line > 0 and count > 0 and next_count > max_chars_per_line:
                break
            units = next_units
            count = next_count
            end += 1

        if end == start:
            # Always advance at least one character to avoid infinite loops.
            end = start + 1
        else:
            end = adjust_wrap_break_index(text, start, end)
            if end <= start:
                end = start + 1

        chunks.append(text[start:end])
        start = end

    if len(chunks) <= 1:
        return text, False
    return "\\P".join(chunks), True


def tune_mtext_for_export(
    layout,
    *,
    width_scale: float,
    line_spacing_scale: float,
    force_wrap_cjk_chars: int,
    smart_wrap_cjk_collision: bool,
    smart_wrap_cjk_chars: int,
) -> tuple[int, int, int]:
    if (
        width_scale == 1.0
        and line_spacing_scale == 1.0
        and force_wrap_cjk_chars == 0
        and not smart_wrap_cjk_collision
    ):
        return 0, 0, 0

    changed = 0
    wrapped = 0
    smart_wrapped = 0
    try:
        entities = list(layout.query("MTEXT"))
    except Exception:
        return 0, 0, 0

    if smart_wrap_cjk_collision:
        smart_wrapped = smart_wrap_mtext_on_collision(
            entities,
            smart_wrap_cjk_chars=smart_wrap_cjk_chars,
        )

    for entity in entities:
        touched = False

        if width_scale != 1.0:
            width = float(getattr(entity.dxf, "width", 0.0) or 0.0)
            if width > 0:
                entity.dxf.width = width * width_scale
                touched = True

        if line_spacing_scale != 1.0:
            factor = float(getattr(entity.dxf, "line_spacing_factor", 1.0) or 1.0)
            # Keep values in a reasonable range for readability.
            new_factor = max(0.25, min(4.0, factor * line_spacing_scale))
            entity.dxf.line_spacing_factor = new_factor
            touched = True

        if force_wrap_cjk_chars > 0:
            raw_text = getattr(entity, "text", None)
            if isinstance(raw_text, str):
                # Only rewrite plain MTEXT text safely; skip formatted MTEXT (e.g. \P, \U+).
                if "\\" not in raw_text and contains_cjk(raw_text):
                    new_raw, did_wrap = wrap_plain_text_by_chars(
                        raw_text,
                        force_wrap_cjk_chars,
                    )
                    if did_wrap and new_raw != raw_text:
                        entity.text = new_raw
                        touched = True
                        wrapped += 1

        if touched:
            changed += 1

    return changed, wrapped, smart_wrapped


def smart_wrap_mtext_on_collision(entities, *, smart_wrap_cjk_chars: int = 0) -> int:
    """Wrap plain CJK MTEXT only when likely to collide with a nearby right-side label."""
    candidates = []
    for entity in entities:
        if not is_plain_cjk_wrap_candidate(entity):
            continue
        insert = getattr(entity.dxf, "insert", None)
        if insert is None:
            continue
        char_h = float(getattr(entity.dxf, "char_height", 0.0) or 0.0)
        if char_h <= 0:
            continue
        x = float(insert[0])
        y = float(insert[1])
        text = entity.text
        candidates.append((x, y, char_h, entity, text))

    # Deterministic order for processing/logging; neighbor lookup scans all candidates.
    candidates.sort(key=lambda item: (-item[1], item[0]))

    wrapped = 0
    for i, (x, y, char_h, entity, raw_text) in enumerate(candidates):
        # Skip if already multiline due to previous smart wrap/other processing.
        if "\\P" in getattr(entity, "text", ""):
            continue

        # Find nearest right neighbor on the same row.
        neighbor = None
        row_tol = char_h * 0.8
        for j, (nx, ny, nh, nent, _) in enumerate(candidates):
            if j == i:
                continue
            if nx <= x:
                continue
            if abs(ny - y) <= max(row_tol, nh * 0.8):
                gap = nx - x
                if neighbor is None or gap < (neighbor[0] - x):
                    neighbor = (nx, ny, nh, nent)
        if neighbor is None:
            continue

        nx, _ny, _nh, _nent = neighbor
        gap = nx - x
        if gap <= char_h * 2.0:
            continue

        text_units = estimated_text_units(raw_text)
        # Empirical factor for matplotlib CJK width estimation in this workflow.
        est_line_width = text_units * char_h * 0.95

        mtext_box_width = float(getattr(entity.dxf, "width", 0.0) or 0.0)
        available_width = gap - char_h * 0.4  # reserve some visual gap between labels
        if mtext_box_width > 0:
            available_width = min(available_width, mtext_box_width)

        if available_width <= char_h * 2.0:
            continue
        if est_line_width <= available_width:
            continue

        allowed_units = available_width / (char_h * 0.95)
        if allowed_units <= 2.0:
            continue

        new_raw, did_wrap = wrap_plain_text_by_available_units(
            raw_text,
            max_units_per_line=allowed_units,
            max_chars_per_line=smart_wrap_cjk_chars,
        )
        if did_wrap and new_raw != raw_text:
            entity.text = new_raw
            wrapped += 1

    return wrapped


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input).expanduser()
    ext = input_path.suffix.lower()

    output_path = (
        Path(args.output).expanduser()
        if args.output
        else input_path.with_suffix(".pdf")
    )

    if ext == ".dwg":
        print(dwg_message(input_path), file=sys.stderr)
        return 6
    if ext != ".dxf":
        print(f"Unsupported input type: {ext or '(no extension)'}", file=sys.stderr)
        print(
            "This script currently exports DXF directly and provides DWG guidance.",
            file=sys.stderr,
        )
        return 1

    try:
        return convert_dxf(
            input_path=input_path,
            output_path=output_path,
            layout_spec=args.layout,
            list_only=args.list_layouts,
            dpi=args.dpi,
            size_inches=args.size_inches,
            mtext_width_scale=args.mtext_width_scale,
            mtext_line_spacing_scale=args.mtext_line_spacing_scale,
            mtext_force_wrap_cjk_chars=args.mtext_force_wrap_cjk_chars,
            mtext_smart_wrap_cjk_collision=args.mtext_smart_wrap_cjk_collision,
            mtext_smart_wrap_cjk_chars=args.mtext_smart_wrap_cjk_chars,
            bg=args.bg,
            fg=args.fg,
            font_family=args.font_family,
            font_file=(Path(args.font_file).expanduser() if args.font_file else None),
            force=args.force,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 7


if __name__ == "__main__":
    raise SystemExit(main())
