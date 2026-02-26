#!/usr/bin/env python3
"""Check local CAD->PDF conversion capabilities."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path


PYTHON_MODULES = ("ezdxf", "matplotlib")
CLI_TOOLS = (
    "qcad",
    "qcadpro",
    "librecad",
    "inkscape",
    "soffice",
    "freecadcmd",
    "ODAFileConverter",
    "odafc",
    "TeighaFileConverter",
    "gs",
)


def have_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def have_tool(name: str) -> bool:
    return shutil.which(name) is not None


def detect() -> dict:
    modules = {name: have_module(name) for name in PYTHON_MODULES}
    tools = {name: have_tool(name) for name in CLI_TOOLS}

    dxf_ready = modules["ezdxf"] and modules["matplotlib"]
    dwg_helpers = [name for name, ok in tools.items() if ok and name != "gs"]

    return {
        "python_modules": modules,
        "cli_tools": tools,
        "dxf_python_backend_ready": dxf_ready,
        "dwg_helper_tools_found": dwg_helpers,
        "recommended_bootstrap": [
            "python3 -m venv .cad2pdf-venv",
            "./.cad2pdf-venv/bin/pip install ezdxf matplotlib",
        ],
    }


def print_text(report: dict) -> None:
    print("CAD -> PDF environment check")
    print()
    print("Python modules:")
    for name, ok in report["python_modules"].items():
        print(f"  - {name}: {'OK' if ok else 'MISSING'}")

    print()
    print("CLI tools:")
    for name, ok in report["cli_tools"].items():
        print(f"  - {name}: {'FOUND' if ok else 'not found'}")

    print()
    print(
        "DXF direct conversion (ezdxf + matplotlib): "
        + ("READY" if report["dxf_python_backend_ready"] else "NOT READY")
    )

    helpers = report["dwg_helper_tools_found"]
    if helpers:
        print("DWG helper tools available: " + ", ".join(helpers))
    else:
        print("DWG helper tools available: none detected")

    if not report["dxf_python_backend_ready"]:
        print()
        print("Recommended setup commands:")
        for cmd in report["recommended_bootstrap"]:
            print(f"  {cmd}")

    print()
    print(
        "Tip: use "
        + str(Path(__file__).with_name("cad_to_pdf.py"))
        + " for DXF conversion after dependencies are installed."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check local tools/modules for CAD to PDF conversion."
    )
    parser.add_argument("--json", action="store_true", help="Output JSON report.")
    parser.add_argument(
        "--require-dxf",
        action="store_true",
        help="Exit non-zero if the Python DXF backend is not ready.",
    )
    args = parser.parse_args()

    report = detect()
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_text(report)

    if args.require_dxf and not report["dxf_python_backend_ready"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
