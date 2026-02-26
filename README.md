# dxf2pdf（DXF 转 PDF 工具包）

## 语言 / Language

- 中文
- [English](./README.en.md)

一个用于将 `.dxf` CAD 图纸转换为 PDF 的轻量工具包，采用 Python 命令行工作流（不依赖双击启动脚本）。支持单文件与批量转换，并内置中文 MTEXT 的碰撞触发换行优化，用于减少相邻标签重叠。

## 功能

- 单文件 DXF 转 PDF
- 批量转换文件夹
- 中文 MTEXT 碰撞触发换行（减少相邻标签横向重叠）
- 仓库默认不包含业务数据（使用 `data/input`、`data/output`）

## 目录结构

```text
dxf-to-pdf-toolkit/
├── README.md
├── README.en.md
├── .gitignore
├── requirements.txt
├── data/
│   ├── input/                  # 默认批量输入目录
│   └── output/                 # 默认批量输出目录
└── scripts/
    ├── check_env.py            # 环境检测
    ├── cad_to_pdf.py           # 单文件 DXF -> PDF
    └── batch_cad_to_pdf.py     # 批量 DXF -> PDF
```

## 快速开始（macOS / Linux）

### 1. 创建虚拟环境并安装依赖

```bash
cd /path/to/dxf2pdf
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt
```

### 2. 可选：环境检测

```bash
./.venv/bin/python scripts/check_env.py
```

### 3. 批量转换（默认数据目录）

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

### 4. 单文件转换

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

## 快速开始（Windows CMD）

### 1. 创建虚拟环境并安装依赖

```bat
cd /d C:\path\to\dxf2pdf
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
```

如果 `python` 不可用，请先安装 Python 并确保已加入 `PATH`。

### 2. 可选：环境检测

```bat
.\.venv\Scripts\python scripts\check_env.py
```

### 3. 批量转换（默认数据目录）

```bat
.\.venv\Scripts\python scripts\batch_cad_to_pdf.py ".\\data\\input" -o ".\\data\\output" --layout modelspace --bg "#FFFFFF" --fg "#000000" --mtext-line-spacing-scale 1.15 --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars 10 --font-family "Microsoft YaHei,SimSun,NSimSun" --force
```

### 4. 单文件转换

```bat
.\.venv\Scripts\python scripts\cad_to_pdf.py "C:\path\to\file.dxf" -o "C:\path\to\file.pdf" --layout modelspace --bg "#FFFFFF" --fg "#000000" --mtext-line-spacing-scale 1.15 --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars 10 --font-family "Microsoft YaHei,SimSun,NSimSun" --force
```

## 快速开始（Windows PowerShell）

```powershell
cd C:\path\to\dxf2pdf
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python .\scripts\batch_cad_to_pdf.py ".\data\input" -o ".\data\output" --layout modelspace --bg "#FFFFFF" --fg "#000000" --mtext-line-spacing-scale 1.15 --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars 10 --font-family "Microsoft YaHei,SimSun,NSimSun" --force
```

## 默认转换参数（推荐）

这些参数是针对配电/单线图类标注较密场景做的优化：

- `--layout modelspace`
- `--bg "#FFFFFF" --fg "#000000"`（白底黑线）
- `--mtext-line-spacing-scale 1.15`
- `--mtext-smart-wrap-cjk-collision`
- `--mtext-smart-wrap-cjk-chars 10`

说明：
- 仅在检测到同排邻近文字可能横向重叠时才换行。
- 不会对所有文字做全局强制换行。

## 批量常用参数

- `--skip-existing`：跳过已生成的 PDF
- `--limit 10`：只处理前 10 个文件
- `--match 桂花`：只处理路径包含关键词的文件
- `--size-inches 11x17`：指定画布尺寸
- `--font-family "Microsoft YaHei,SimSun"`：指定中文字体优先级
- `--font-file "C:\Windows\Fonts\msyh.ttc"`：注册字体文件（字体未被 matplotlib 识别时）

示例：

```bash
./.venv/bin/python scripts/batch_cad_to_pdf.py "./data/input" -o "./data/output" --match 桂花 --skip-existing --layout modelspace --bg "#FFFFFF" --fg "#000000" --mtext-line-spacing-scale 1.15 --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars 10 --force
```

```bash
./.venv/bin/python scripts/batch_cad_to_pdf.py "./data/input" -o "./data/output" --limit 10 --layout modelspace --bg "#FFFFFF" --fg "#000000" --mtext-line-spacing-scale 1.15 --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars 10 --force
```

## 输出结果

- 单文件模式：默认输出同名 `.pdf`（或你指定的 `-o` 路径）
- 批量模式：PDF 输出到目标输出目录
- 批量模式会同时生成汇总 JSON：
  - `cad2pdf_batch_summary_YYYYMMDD_HHMMSS.json`

## 已知限制

- 目前直接稳定支持 `.dxf`；`.dwg` 建议先转换为 `.dxf`
- 非原生 CAD 渲染器下，中文字体/标注可能仍有差异
- 若依赖 CTB/STB 严格出图样式，建议使用原生 CAD 软件导出 PDF
