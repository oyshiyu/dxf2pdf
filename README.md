# dxf2pdf (DXF to PDF Toolkit)

## Language / 语言

- English
- [中文](./README.zh-CN.md)

A lightweight toolkit for converting `.dxf` CAD drawings to PDF. It supports single-file and batch workflows and includes one-click launchers for macOS and Windows.

## Features

- Single-file conversion
- Batch conversion for folders
- One-click macOS launcher (`.command`)
- One-click Windows launcher (`.bat`)
- Collision-triggered wrapping for Chinese MTEXT labels (to reduce overlap between adjacent labels)

Note:
- The repository is data-free by default and uses generic directories: `data/input` and `data/output`.

## Project Structure

```text
dxf-to-pdf-toolkit/
├── README.md
├── README.zh-CN.md
├── .gitignore
├── requirements.txt
├── run_dxf_to_pdf.command      # macOS launcher (single + batch)
├── run_dxf_to_pdf.bat          # Windows launcher (single + batch)
├── data/
│   ├── input/                  # Default batch input folder
│   └── output/                 # Default batch output folder
└── scripts/
    ├── check_env.py            # Environment check
    ├── cad_to_pdf.py           # Single-file DXF -> PDF
    └── batch_cad_to_pdf.py     # Batch DXF -> PDF
```

## Default Behavior (Important)

`run_dxf_to_pdf.command` and `run_dxf_to_pdf.bat` default to batch mode:

- No arguments: batch convert `data/input/` -> `data/output/`
- First argument is a folder: batch convert that folder
- First argument is a file: convert that `.dxf` file as a single-file job

## Before First Run

1. Install Python 3 (recommended 3.9+)
2. Put the toolkit in its own directory
3. Place your files:
   - Batch mode: put `.dxf` files into `data/input/`
   - Single-file mode: any path works (drag-and-drop or command-line arguments)

On first run, the launcher will automatically:

- Create `.cad2pdf-venv`
- Install `ezdxf` and `matplotlib`

## macOS (One-Click)

### Double-click (Default Batch)

- Double-click `run_dxf_to_pdf.command`
- Default batch folders: `data/input/` -> `data/output/`

### Drag a File (Single)

- Drag a `.dxf` file onto `run_dxf_to_pdf.command`

### Drag a Folder (Batch)

- Drag a folder onto `run_dxf_to_pdf.command`

### Terminal Usage

```bash
cd /path/to/dxf-to-pdf-toolkit
./run_dxf_to_pdf.command
```

Single file:

```bash
./run_dxf_to_pdf.command "/path/to/file.dxf"
```

Custom batch input and output:

```bash
./run_dxf_to_pdf.command "/path/to/input_folder" "/path/to/output_folder"
```

## Windows (One-Click)

### Double-click (Default Batch)

- Double-click `run_dxf_to_pdf.bat`
- Default batch folders: `data\\input\\` -> `data\\output\\`

### Drag a File (Single)

- Drag a `.dxf` file onto `run_dxf_to_pdf.bat`

### Drag a Folder (Batch)

- Drag a folder onto `run_dxf_to_pdf.bat`

### CMD Usage

```bat
cd C:\path\to\dxf-to-pdf-toolkit
run_dxf_to_pdf.bat
```

Single file:

```bat
run_dxf_to_pdf.bat "C:\path\to\file.dxf"
```

Custom batch input and output:

```bat
run_dxf_to_pdf.bat "C:\path\to\input_folder" "C:\path\to\output_folder"
```

## Default Conversion Settings (Built-in)

Defaults are tuned for distribution / single-line drawings with dense labels:

- `--layout modelspace`
- `--bg "#FFFFFF" --fg "#000000"` (white background, black foreground)
- `--mtext-line-spacing-scale 1.15`
- `--mtext-smart-wrap-cjk-collision` (collision-triggered wrapping)
- `--mtext-smart-wrap-cjk-chars 10` (max 10 chars per wrapped line when smart wrapping triggers)

Note: Wrapping is only applied when nearby same-row labels are likely to collide; it is not a global forced wrap.

## Optional Environment Variables

- `CAD2PDF_LIMIT`: Convert only the first N files (batch)
- `CAD2PDF_MATCH`: Path substring filter (batch)
- `CAD2PDF_SKIP_EXISTING=1`: Skip existing PDFs (batch)
- `CAD2PDF_LAYOUT`: `modelspace` / `paperspace` / layout name
- `CAD2PDF_SIZE_INCHES`: e.g. `11x17`
- `CAD2PDF_SMART_WRAP_CJK_CHARS`: Smart-wrap char cap (default `10`)
- `CAD2PDF_MTEXT_LINE_SPACING_SCALE`: Default `1.15`
- `CAD2PDF_MTEXT_WIDTH_SCALE`: Default `1.0`

macOS example:

```bash
CAD2PDF_LIMIT=10 CAD2PDF_MATCH=桂花 ./run_dxf_to_pdf.command
```

Windows example (CMD):

```bat
set CAD2PDF_LIMIT=10
set CAD2PDF_MATCH=桂花
run_dxf_to_pdf.bat
```

## Outputs

- Single-file mode: outputs a same-name `.pdf` by default
- Batch mode: outputs to `data/output/` by default (or your custom output folder)
- Batch mode writes a summary JSON:
  - `cad2pdf_batch_summary_YYYYMMDD_HHMMSS.json`

## Manual Python Usage (Optional)

Environment check:

```bash
python3 scripts/check_env.py
```

Single-file conversion:

```bash
python3 scripts/cad_to_pdf.py "/path/to/file.dxf" -o "/path/to/file.pdf" --layout modelspace --force
```

Batch conversion:

```bash
python3 scripts/batch_cad_to_pdf.py "./data/input" -o "./data/output" --layout modelspace --force
```

## GitHub Publishing (Without Data)

- Do not commit `data/input/`, `data/output/`, or `.cad2pdf-venv/`

Typical commands:

```bash
git init
git add README.md README.zh-CN.md .gitignore requirements.txt run_dxf_to_pdf.command run_dxf_to_pdf.bat scripts/ data/input/.gitkeep data/output/.gitkeep
git commit -m "Add DXF to PDF toolkit"
```

## Known Limitations

- Direct support is stable for `.dxf`; convert `.dwg` to `.dxf` first
- Some fonts/text layouts (especially Chinese CAD fonts) may differ from native CAD renderers
- If strict CTB/STB plotting fidelity is required, export PDF from native CAD software
