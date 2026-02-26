# dxf2pdf（DXF 转 PDF 工具包）

## 语言 / Language

- 中文
- [English](./README.md)

一个用于将 `.dxf` CAD 图纸转换为 PDF 的轻量工具包，支持单文件与批量转换，并提供 macOS / Windows 一键运行脚本。

## 功能

- 单文件转换
- 批量转换文件夹
- macOS 一键运行（`.command`）
- Windows 一键运行（`.bat`）
- 中文 MTEXT 的碰撞触发换行优化（避免相邻标签横向重叠）

说明：
- 仓库默认不包含业务数据文件，使用通用目录命名：`data/input`、`data/output`。

## 目录结构

```text
dxf-to-pdf-toolkit/
├── README.md
├── README.zh-CN.md
├── .gitignore
├── requirements.txt
├── run_dxf_to_pdf.command      # macOS launcher (single + batch)
├── run_dxf_to_pdf.bat          # Windows launcher (single + batch)
├── data/
│   ├── input/                  # 默认批量输入目录
│   └── output/                 # 默认批量输出目录
└── scripts/
    ├── check_env.py            # 环境检测
    ├── cad_to_pdf.py           # 单文件 DXF -> PDF
    └── batch_cad_to_pdf.py     # 批量 DXF -> PDF
```

## 默认行为（重要）

`run_dxf_to_pdf.command` 和 `run_dxf_to_pdf.bat` 默认都是批量模式：

- 不传参数：批量转换 `data/input/` -> `data/output/`
- 第 1 个参数是文件夹：批量转换该文件夹
- 第 1 个参数是文件：单文件转换该 `.dxf`

## 使用前准备

1. 安装 Python 3（建议 3.9+）
2. 将工具包放在独立目录
3. 放置数据文件：
   - 批量模式：把 `.dxf` 放到 `data/input/`
   - 单文件模式：任意路径均可（拖拽或命令行传参）

首次运行会自动：

- 创建虚拟环境 `.cad2pdf-venv`
- 安装依赖 `ezdxf`, `matplotlib`

## macOS（一键运行）

### 双击（默认批量）

- 双击 `run_dxf_to_pdf.command`
- 默认批量目录：`data/input/` -> `data/output/`

### 拖拽文件（单文件）

- 将 `.dxf` 文件拖到 `run_dxf_to_pdf.command` 上

### 拖拽文件夹（批量）

- 将文件夹拖到 `run_dxf_to_pdf.command` 上

### 终端运行

```bash
cd /path/to/dxf-to-pdf-toolkit
./run_dxf_to_pdf.command
```

单文件：

```bash
./run_dxf_to_pdf.command "/path/to/file.dxf"
```

指定批量输入与输出目录：

```bash
./run_dxf_to_pdf.command "/path/to/input_folder" "/path/to/output_folder"
```

## Windows（一键运行）

### 双击（默认批量）

- 双击 `run_dxf_to_pdf.bat`
- 默认批量目录：`data\\input\\` -> `data\\output\\`

### 拖拽文件（单文件）

- 将 `.dxf` 文件拖到 `run_dxf_to_pdf.bat` 上

### 拖拽文件夹（批量）

- 将文件夹拖到 `run_dxf_to_pdf.bat` 上

### CMD 运行

```bat
cd C:\path\to\dxf-to-pdf-toolkit
run_dxf_to_pdf.bat
```

单文件：

```bat
run_dxf_to_pdf.bat "C:\path\to\file.dxf"
```

指定输入与输出目录：

```bat
run_dxf_to_pdf.bat "C:\path\to\input_folder" "C:\path\to\output_folder"
```

## 默认转换参数（内置）

默认参数针对配电/单线图类标注场景做了优化：

- `--layout modelspace`
- `--bg "#FFFFFF" --fg "#000000"`（白底黑线）
- `--mtext-line-spacing-scale 1.15`
- `--mtext-smart-wrap-cjk-collision`（碰撞触发换行）
- `--mtext-smart-wrap-cjk-chars 10`（碰撞触发后单行最多 10 字符）

说明：仅在检测到同排邻近文字可能横向重叠时才换行，不会全局强制换行。

## 可选环境变量（进阶）

- `CAD2PDF_LIMIT`：仅处理前 N 个文件（批量）
- `CAD2PDF_MATCH`：仅处理路径包含关键词的文件（批量）
- `CAD2PDF_SKIP_EXISTING=1`：跳过已有 PDF（批量）
- `CAD2PDF_LAYOUT`：`modelspace` / `paperspace` / 布局名
- `CAD2PDF_SIZE_INCHES`：例如 `11x17`
- `CAD2PDF_SMART_WRAP_CJK_CHARS`：碰撞换行字符上限（默认 `10`）
- `CAD2PDF_MTEXT_LINE_SPACING_SCALE`：默认 `1.15`
- `CAD2PDF_MTEXT_WIDTH_SCALE`：默认 `1.0`

macOS 示例：

```bash
CAD2PDF_LIMIT=10 CAD2PDF_MATCH=桂花 ./run_dxf_to_pdf.command
```

Windows 示例（CMD）：

```bat
set CAD2PDF_LIMIT=10
set CAD2PDF_MATCH=桂花
run_dxf_to_pdf.bat
```

## 输出结果

- 单文件模式：默认输出同名 `.pdf`
- 批量模式：默认输出到 `data/output/`（或指定输出目录）
- 批量模式会生成汇总 JSON：
  - `cad2pdf_batch_summary_YYYYMMDD_HHMMSS.json`

## 手动运行 Python 脚本（可选）

环境检测：

```bash
python3 scripts/check_env.py
```

单文件转换：

```bash
python3 scripts/cad_to_pdf.py "/path/to/file.dxf" -o "/path/to/file.pdf" --layout modelspace --force
```

批量转换：

```bash
python3 scripts/batch_cad_to_pdf.py "./data/input" -o "./data/output" --layout modelspace --force
```

## 上传到 GitHub（不上传数据）

- 不要提交 `data/input/`、`data/output/`、`.cad2pdf-venv/`

常见命令：

```bash
git init
git add README.md README.zh-CN.md .gitignore requirements.txt run_dxf_to_pdf.command run_dxf_to_pdf.bat scripts/ data/input/.gitkeep data/output/.gitkeep
git commit -m "Add DXF to PDF toolkit"
```

## 已知限制

- 目前直接稳定支持 `.dxf`；`.dwg` 建议先转换为 `.dxf`
- 非原生 CAD 渲染器下，中文字体/标注可能仍有差异
- 若依赖 CTB/STB 严格出图样式，建议使用原生 CAD 软件导出 PDF
