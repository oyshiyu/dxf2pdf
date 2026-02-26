#!/usr/bin/env python3
"""Batch convert DXF files under a folder to PDF using cad_to_pdf.py."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def parse_size_inches(text: str) -> tuple[float, float]:
    for sep in ("x", "X", "*", ","):
        if sep in text:
            left, right = text.split(sep, 1)
            w = float(left.strip())
            h = float(right.strip())
            if w <= 0 or h <= 0:
                raise argparse.ArgumentTypeError("size values must be > 0")
            return (w, h)
    raise argparse.ArgumentTypeError("expected format WxH, e.g. 11x17")


@dataclass
class Stats:
    total: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0


def load_single_converter(script_path: Path):
    spec = importlib.util.spec_from_file_location("cad_to_pdf_single", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load converter script: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_dxf_files(root: Path, recursive: bool) -> list[Path]:
    iterator = root.rglob("*") if recursive else root.glob("*")
    files = [p for p in iterator if p.is_file() and p.suffix.lower() == ".dxf"]
    files.sort(key=lambda p: str(p))
    return files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch convert all DXF files in a folder to PDF."
    )
    parser.add_argument("input_dir", help="Folder containing DXF files")
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Output root folder (default: <input_dir>_pdf)",
    )
    parser.add_argument(
        "--recursive",
        dest="recursive",
        action="store_true",
        default=True,
        help="Recurse into subfolders (default: on)",
    )
    parser.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="Only convert files directly inside input_dir",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Convert only the first N files (0 = no limit)",
    )
    parser.add_argument(
        "--match",
        help="Only convert files whose path contains this substring",
    )
    parser.add_argument(
        "--layout",
        default="modelspace",
        help="Layout mode/name passed to cad_to_pdf.py (default: modelspace)",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Render DPI (default: 300)")
    parser.add_argument(
        "--size-inches",
        type=parse_size_inches,
        help="Fixed canvas size in inches (e.g. 11x17)",
    )
    parser.add_argument(
        "--mtext-width-scale",
        type=float,
        default=1.0,
        help="MTEXT width scaling (<1 wraps earlier). Default: 1.0",
    )
    parser.add_argument(
        "--mtext-line-spacing-scale",
        type=float,
        default=1.15,
        help="MTEXT line spacing scaling. Default: 1.15",
    )
    parser.add_argument(
        "--mtext-force-wrap-cjk-chars",
        type=int,
        default=0,
        help="Force-wrap plain CJK MTEXT by char count (0 disables).",
    )
    parser.add_argument(
        "--mtext-smart-wrap-cjk-collision",
        action="store_true",
        help="Only wrap CJK MTEXT when same-row labels likely collide.",
    )
    parser.add_argument(
        "--mtext-smart-wrap-cjk-chars",
        type=int,
        default=0,
        help="Wrap chars used only when smart collision wrapping triggers (0 = auto).",
    )
    parser.add_argument(
        "--bg",
        default="#FFFFFF",
        help="Background color hex (default: #FFFFFF)",
    )
    parser.add_argument(
        "--fg",
        default="#000000",
        help="Foreground color hex (default: #000000)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing PDFs",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files whose target PDF already exists",
    )
    parser.add_argument(
        "--summary-json",
        help="Write summary JSON to this path",
    )
    return parser


def write_summary(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    if not input_dir.is_dir():
        print(f"Input folder not found: {input_dir}", file=sys.stderr)
        return 2

    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else input_dir.parent / f"{input_dir.name}_pdf"
    )

    script_path = Path(__file__).with_name("cad_to_pdf.py")
    converter = load_single_converter(script_path)

    files = find_dxf_files(input_dir, recursive=args.recursive)
    if args.match:
        files = [p for p in files if args.match in str(p)]
    if args.limit and args.limit > 0:
        files = files[: args.limit]

    stats = Stats(total=len(files))
    failures: list[dict] = []

    print(f"Input folder: {input_dir}")
    print(f"Output folder: {output_dir}")
    print(f"DXF files found: {len(files)}")
    if args.match:
        print(f"Path filter: {args.match}")
    if args.limit:
        print(f"Limit: {args.limit}")
    print()

    if not files:
        print("No DXF files matched.")
        if args.summary_json:
            write_summary(
                Path(args.summary_json).expanduser(),
                {
                    "input_dir": str(input_dir),
                    "output_dir": str(output_dir),
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "skipped": 0,
                    "failures": [],
                },
            )
        return 0

    start_time = time.time()
    for index, src in enumerate(files, start=1):
        rel = src.relative_to(input_dir)
        dst = output_dir / rel.with_suffix(".pdf")

        if args.skip_existing and dst.exists():
            stats.skipped += 1
            print(f"[{index}/{stats.total}] SKIP exists: {rel}")
            continue

        print(f"[{index}/{stats.total}] Converting: {rel}")
        rc = converter.convert_dxf(
            input_path=src,
            output_path=dst,
            layout_spec=args.layout,
            list_only=False,
            dpi=args.dpi,
            size_inches=args.size_inches,
            mtext_width_scale=args.mtext_width_scale,
            mtext_line_spacing_scale=args.mtext_line_spacing_scale,
            mtext_force_wrap_cjk_chars=args.mtext_force_wrap_cjk_chars,
            mtext_smart_wrap_cjk_collision=args.mtext_smart_wrap_cjk_collision,
            mtext_smart_wrap_cjk_chars=args.mtext_smart_wrap_cjk_chars,
            bg=args.bg,
            fg=args.fg,
            force=args.force,
        )
        if rc == 0:
            stats.success += 1
        else:
            stats.failed += 1
            failures.append({"file": str(src), "output": str(dst), "code": rc})
            print(f"[{index}/{stats.total}] FAILED rc={rc}: {rel}", file=sys.stderr)
        print()

    elapsed = round(time.time() - start_time, 2)
    summary = {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "total": stats.total,
        "success": stats.success,
        "failed": stats.failed,
        "skipped": stats.skipped,
        "elapsed_seconds": elapsed,
        "failures": failures,
    }

    print("Batch conversion summary")
    print(f"  total:   {stats.total}")
    print(f"  success: {stats.success}")
    print(f"  failed:  {stats.failed}")
    print(f"  skipped: {stats.skipped}")
    print(f"  elapsed: {elapsed}s")

    if args.summary_json:
        summary_path = Path(args.summary_json).expanduser().resolve()
        write_summary(summary_path, summary)
        print(f"  summary_json: {summary_path}")

    return 0 if stats.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
