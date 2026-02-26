# dxf2pdf (DXF to PDF Toolkit)

中文：一个用于将 `.dxf` CAD 图纸转换为 PDF 的轻量工具包，支持单文件与批量转换，提供 macOS / Windows 一键运行脚本。  
English: A lightweight toolkit for converting `.dxf` CAD drawings to PDF, supporting both single-file and batch workflows with one-click launchers for macOS and Windows.

## 功能 / Features

- 单文件转换 / Single-file conversion
- 批量转换文件夹 / Batch conversion for folders
- macOS 一键运行（`.command`）/ One-click macOS launcher (`.command`)
- Windows 一键运行（`.bat`）/ One-click Windows launcher (`.bat`)
- 中文 MTEXT 碰撞触发换行优化 / Collision-triggered wrapping for Chinese MTEXT labels

说明 / Note:
- 仓库默认不包含业务数据文件，使用通用目录命名：`data/input`、`data/output`。
- The repository is data-free by default and uses generic directories: `data/input` and `data/output`.

## 目录结构 / Project Structure

```text
dxf-to-pdf-toolkit/
├── README.md
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

## 默认行为 / Default Behavior

`run_dxf_to_pdf.command` 和 `run_dxf_to_pdf.bat` 默认都是批量模式。  
Both `run_dxf_to_pdf.command` and `run_dxf_to_pdf.bat` default to batch mode.

- 不传参数：批量转换 `data/input/` -> `data/output/`
- No arguments: batch convert `data/input/` -> `data/output/`
- 第 1 个参数是文件夹：批量转换该文件夹
- First argument is a folder: batch convert that folder
- 第 1 个参数是文件：单文件转换该 `.dxf`
- First argument is a file: convert that `.dxf` as a single-file job

## 使用前准备 / Before First Run

1. 安装 Python 3（建议 3.9+）/ Install Python 3 (recommended 3.9+)
2. 将工具包放在独立目录 / Put the toolkit in its own directory
3. 放置数据文件 / Place your data files:
   - 批量模式：放到 `data/input/` / Batch mode: put `.dxf` files into `data/input/`
   - 单文件模式：任意路径均可 / Single-file mode: any path works

首次运行会自动：  
On first run, the launcher will automatically:

- 创建虚拟环境 `.cad2pdf-venv` / Create `.cad2pdf-venv`
- 安装依赖 `ezdxf`, `matplotlib` / Install `ezdxf`, `matplotlib`

## macOS（一键运行）/ macOS (One-Click)

### 双击（默认批量）/ Double-click (Default Batch)

- 双击 `run_dxf_to_pdf.command`
- Double-click `run_dxf_to_pdf.command`

默认批量目录：`data/input/` -> `data/output/`  
Default batch folders: `data/input/` -> `data/output/`

### 拖拽文件（单文件）/ Drag a File (Single)

- 将 `.dxf` 文件拖到 `run_dxf_to_pdf.command` 上
- Drag a `.dxf` file onto `run_dxf_to_pdf.command`

### 拖拽文件夹（批量）/ Drag a Folder (Batch)

- 将文件夹拖到 `run_dxf_to_pdf.command` 上
- Drag a folder onto `run_dxf_to_pdf.command`

### 终端运行 / Terminal Usage

```bash
cd /path/to/dxf-to-pdf-toolkit
./run_dxf_to_pdf.command
```

单文件 / Single file:

```bash
./run_dxf_to_pdf.command "/path/to/file.dxf"
```

指定输入输出目录 / Custom batch input and output:

```bash
./run_dxf_to_pdf.command "/path/to/input_folder" "/path/to/output_folder"
```

## Windows（一键运行）/ Windows (One-Click)

### 双击（默认批量）/ Double-click (Default Batch)

- 双击 `run_dxf_to_pdf.bat`
- Double-click `run_dxf_to_pdf.bat`

默认批量目录：`data\\input\\` -> `data\\output\\`  
Default batch folders: `data\\input\\` -> `data\\output\\`

### 拖拽文件（单文件）/ Drag a File (Single)

- 将 `.dxf` 文件拖到 `run_dxf_to_pdf.bat` 上
- Drag a `.dxf` file onto `run_dxf_to_pdf.bat`

### 拖拽文件夹（批量）/ Drag a Folder (Batch)

- 将文件夹拖到 `run_dxf_to_pdf.bat` 上
- Drag a folder onto `run_dxf_to_pdf.bat`

### CMD 运行 / CMD Usage

```bat
cd C:\path\to\dxf-to-pdf-toolkit
run_dxf_to_pdf.bat
```

单文件 / Single file:

```bat
run_dxf_to_pdf.bat "C:\path\to\file.dxf"
```

指定输入输出目录 / Custom batch input and output:

```bat
run_dxf_to_pdf.bat "C:\path\to\input_folder" "C:\path\to\output_folder"
```

## 默认转换参数（内置）/ Default Conversion Settings (Built-in)

默认参数针对配电/单线图类标注场景做了优化。  
Defaults are tuned for distribution/single-line drawings with dense text labels.

- `--layout modelspace`
- `--bg "#FFFFFF" --fg "#000000"`（白底黑线 / white background, black foreground）
- `--mtext-line-spacing-scale 1.15`
- `--mtext-smart-wrap-cjk-collision`（碰撞触发换行 / collision-triggered wrapping）
- `--mtext-smart-wrap-cjk-chars 10`（碰撞触发后单行最多 10 字符 / max 10 chars per wrapped line when collision wrapping triggers）

说明 / Note:
- 仅在检测到同排邻近文字可能横向重叠时才换行，不会全局强制换行。
- Wrapping is only applied when nearby same-row labels are likely to collide; it is not a global forced wrap.

## 可选环境变量 / Optional Environment Variables

这些环境变量主要用于批量模式，也可影响单文件模式。  
These environment variables mainly affect batch mode, and some also affect single-file mode.

- `CAD2PDF_LIMIT`：仅处理前 N 个文件 / Convert only the first N files (batch)
- `CAD2PDF_MATCH`：仅处理路径包含关键词的文件 / Path substring filter (batch)
- `CAD2PDF_SKIP_EXISTING=1`：跳过已有 PDF / Skip existing PDFs (batch)
- `CAD2PDF_LAYOUT`：`modelspace` / `paperspace` / 布局名 / layout name
- `CAD2PDF_SIZE_INCHES`：例如 `11x17` / e.g. `11x17`
- `CAD2PDF_SMART_WRAP_CJK_CHARS`：碰撞换行字符上限（默认 `10`）/ smart-wrap char cap (default `10`)
- `CAD2PDF_MTEXT_LINE_SPACING_SCALE`：默认 `1.15` / default `1.15`
- `CAD2PDF_MTEXT_WIDTH_SCALE`：默认 `1.0` / default `1.0`

macOS 示例 / macOS example:

```bash
CAD2PDF_LIMIT=10 CAD2PDF_MATCH=桂花 ./run_dxf_to_pdf.command
```

Windows 示例（CMD）/ Windows example (CMD):

```bat
set CAD2PDF_LIMIT=10
set CAD2PDF_MATCH=桂花
run_dxf_to_pdf.bat
```

## 输出结果 / Outputs

- 单文件模式：默认输出同名 `.pdf` / Single-file mode: outputs a same-name `.pdf`
- 批量模式：默认输出到 `data/output/`（或你指定的目录）/ Batch mode: outputs to `data/output/` (or your custom output folder)
- 批量模式会生成汇总 JSON / Batch mode writes a summary JSON:
  - `cad2pdf_batch_summary_YYYYMMDD_HHMMSS.json`

## 手动运行 Python 脚本 / Manual Python Usage

环境检测 / Environment check:

```bash
python3 scripts/check_env.py
```

单文件转换 / Single-file conversion:

```bash
python3 scripts/cad_to_pdf.py "/path/to/file.dxf" -o "/path/to/file.pdf" --layout modelspace --force
```

批量转换 / Batch conversion:

```bash
python3 scripts/batch_cad_to_pdf.py "./data/input" -o "./data/output" --layout modelspace --force
```

## 上传到 GitHub（不上传数据）/ GitHub Publishing (Without Data)

- 不要提交 `data/input/`、`data/output/`、`.cad2pdf-venv/`
- Do not commit `data/input/`, `data/output/`, or `.cad2pdf-venv/`

常见命令 / Typical commands:

```bash
git init
git add README.md .gitignore requirements.txt run_dxf_to_pdf.command run_dxf_to_pdf.bat scripts/ data/input/.gitkeep data/output/.gitkeep
git commit -m "Add DXF to PDF toolkit"
```

## 已知限制 / Known Limitations

- 目前直接稳定支持 `.dxf`；`.dwg` 建议先转换为 `.dxf`
- Direct support is stable for `.dxf`; convert `.dwg` to `.dxf` first
- 非原生 CAD 渲染器下，中文字体/标注可能仍有差异
- Some fonts/text layouts (especially Chinese CAD fonts) may differ from native CAD renderers
- 若依赖 CTB/STB 严格出图样式，建议使用原生 CAD 软件导出 PDF
- If strict CTB/STB plotting fidelity is required, export PDF from native CAD software
