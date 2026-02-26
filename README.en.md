# dxf2pdf (DXF to PDF Toolkit)

## Language / 语言

- English
- [中文](./README.md)

A lightweight toolkit for converting `.dxf` CAD drawings to PDF using Python scripts (command-line workflow). It supports both single-file and batch conversion and includes collision-triggered wrapping for dense Chinese MTEXT labels.

## Features

- Single-file DXF to PDF conversion
- Batch conversion for folders
- Command-line workflow (no launcher dependency)
- Collision-triggered wrapping for Chinese MTEXT labels (reduces overlap between adjacent labels)
- Data-free repository structure (`data/input`, `data/output`)

## Project Structure

```text
dxf-to-pdf-toolkit/
├── README.md
├── README.en.md
├── .gitignore
├── requirements.txt
├── data/
│   ├── input/                  # Default batch input folder
│   └── output/                 # Default batch output folder
└── scripts/
    ├── check_env.py            # Environment check
    ├── cad_to_pdf.py           # Single-file DXF -> PDF
    └── batch_cad_to_pdf.py     # Batch DXF -> PDF
```

## Quick Start (macOS / Linux)

### 1. Create and activate virtual environment

```bash
cd /path/to/dxf-to-pdf-toolkit
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt
```

### 2. Optional environment check

```bash
./.venv/bin/python scripts/check_env.py
```

### 3. Batch convert (default data folders)

```bash
./.venv/bin/python scripts/batch_cad_to_pdf.py \
  "./data/input" \
  -o "./data/output" \
  --layout modelspace \
  --bg "#FFFFFF" \
  --fg "#000000" \
  --mtext-line-spacing-scale 1.15 \
  --mtext-smart-wrap-cjk-collision \
  --mtext-smart-wrap-cjk-chars 10 \
  --force
```

### 4. Single-file convert

```bash
./.venv/bin/python scripts/cad_to_pdf.py \
  "/path/to/file.dxf" \
  -o "/path/to/file.pdf" \
  --layout modelspace \
  --bg "#FFFFFF" \
  --fg "#000000" \
  --mtext-line-spacing-scale 1.15 \
  --mtext-smart-wrap-cjk-collision \
  --mtext-smart-wrap-cjk-chars 10 \
  --force
```

## Quick Start (Windows CMD)

### 1. Create virtual environment and install dependencies

```bat
cd /d C:\path\to\dxf-to-pdf-toolkit
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
```

If `py` is not available, replace `py -3` with `python`.

### 2. Optional environment check

```bat
.\.venv\Scripts\python scripts\check_env.py
```

### 3. Batch convert (default data folders)

```bat
.\.venv\Scripts\python scripts\batch_cad_to_pdf.py ".\\data\\input" -o ".\\data\\output" --layout modelspace --bg "#FFFFFF" --fg "#000000" --mtext-line-spacing-scale 1.15 --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars 10 --force
```

### 4. Single-file convert

```bat
.\.venv\Scripts\python scripts\cad_to_pdf.py "C:\path\to\file.dxf" -o "C:\path\to\file.pdf" --layout modelspace --bg "#FFFFFF" --fg "#000000" --mtext-line-spacing-scale 1.15 --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars 10 --force
```

## Quick Start (Windows PowerShell)

```powershell
cd C:\path\to\dxf-to-pdf-toolkit
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python .\scripts\batch_cad_to_pdf.py ".\data\input" -o ".\data\output" --layout modelspace --bg "#FFFFFF" --fg "#000000" --mtext-line-spacing-scale 1.15 --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars 10 --force
```

## Default Conversion Settings (Recommended)

These options are tuned for dense single-line / distribution diagrams:

- `--layout modelspace`
- `--bg "#FFFFFF" --fg "#000000"` (white background, black foreground)
- `--mtext-line-spacing-scale 1.15`
- `--mtext-smart-wrap-cjk-collision`
- `--mtext-smart-wrap-cjk-chars 10`

Note:
- Wrapping is only applied when same-row nearby labels are likely to collide.
- It is not a global forced wrap.

## Useful Batch Options

- `--skip-existing` Skip existing PDFs
- `--limit 10` Convert only the first 10 files
- `--match 桂花` Convert only files whose path contains the keyword
- `--size-inches 11x17` Set canvas size

Examples:

```bash
./.venv/bin/python scripts/batch_cad_to_pdf.py "./data/input" -o "./data/output" --match 桂花 --skip-existing --layout modelspace --bg "#FFFFFF" --fg "#000000" --mtext-line-spacing-scale 1.15 --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars 10 --force
```

```bash
./.venv/bin/python scripts/batch_cad_to_pdf.py "./data/input" -o "./data/output" --limit 10 --layout modelspace --bg "#FFFFFF" --fg "#000000" --mtext-line-spacing-scale 1.15 --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars 10 --force
```

## Outputs

- Single-file mode: same-name `.pdf` by default (or your `-o` path)
- Batch mode: PDFs written to the output folder
- Batch mode also writes a summary JSON:
  - `cad2pdf_batch_summary_YYYYMMDD_HHMMSS.json`

## Publishing to GitHub (No Data)

- Do not commit `data/input/`, `data/output/`, or `.venv/`
- Keep only the toolkit code and documentation

Typical commands:

```bash
git init
git add README.md README.en.md .gitignore requirements.txt scripts/ data/input/.gitkeep data/output/.gitkeep
git commit -m "Add DXF to PDF toolkit"
```

## Known Limitations

- Stable direct support is for `.dxf`; convert `.dwg` to `.dxf` first
- Font metrics (especially some Chinese CAD fonts) may differ from native CAD renderers
- If strict CTB/STB plotting fidelity is required, export PDF from native CAD software
