# DXF to PDF Toolkit

一个可直接上传到 GitHub 的轻量工具包，用于将 CAD 图纸（主要是 `.dxf`）转换为 PDF，支持：

- 单文件转换
- 批量转换文件夹
- macOS 一键运行（`.command`）
- Windows 一键运行（`.bat`）
- 中文 MTEXT 的“碰撞触发换行”优化（避免相邻标签横向重叠）

说明：仓库默认不包含任何业务数据文件，采用通用目录命名（`data/input`、`data/output`），更适合团队协作和公开仓库。

## 建议仓库名

建议使用：`dxf-to-pdf-toolkit`

如果你更强调批量场景，也可以用：

- `dxf-to-pdf-batch-converter`
- `cad-dxf-pdf-toolkit`

## 目录结构

```text
dxf-to-pdf-toolkit/
├── README.md
├── .gitignore
├── requirements.txt
├── run_dxf_to_pdf.command      # macOS 一键运行（单文件/批量二合一）
├── run_dxf_to_pdf.bat          # Windows 一键运行（单文件/批量二合一）
├── data/
│   ├── input/                  # 放 DXF 输入文件（默认批量入口）
│   └── output/                 # 批量输出 PDF（默认输出目录）
└── scripts/
    ├── check_env.py            # 环境检测
    ├── cad_to_pdf.py           # 单文件 DXF -> PDF
    └── batch_cad_to_pdf.py     # 批量 DXF -> PDF
```

## 默认行为（非常重要）

`run_dxf_to_pdf.command` / `run_dxf_to_pdf.bat` 的默认模式是 **批量**：

- 如果直接双击运行（不传参数）
- 会批量转换当前目录下的 `data/input/`
- 输出到 `data/output/`

控制方式：

- 不传参数：批量（默认）
- 第 1 个参数是文件夹：批量转换该文件夹
- 第 1 个参数是文件：单文件转换该 `.dxf`

## 使用前准备

1. 安装 Python 3（建议 3.9+）
2. 将本工具包放到一个单独目录
3. 放置数据文件：
   - 批量模式：把 `.dxf` 放到 `data/input/`
   - 单文件模式：任意路径都可以（拖拽或命令行传参）

首次运行会自动：

- 创建虚拟环境 `.cad2pdf-venv`
- 安装依赖（`ezdxf`, `matplotlib`）

## macOS（一键运行）

### 方式 1：双击（默认批量）

双击：

- `run_dxf_to_pdf.command`

要求：当前目录中存在 `data/input/` 文件夹（已预置空目录）。

### 方式 2：拖拽文件（单文件）

把 `.dxf` 文件拖到 `run_dxf_to_pdf.command` 上，会自动按单文件模式转换。

### 方式 3：拖拽文件夹（批量）

把某个文件夹拖到 `run_dxf_to_pdf.command` 上，会自动按批量模式转换该文件夹。

### 方式 4：终端运行

```bash
cd /path/to/dxf-to-pdf-toolkit
./run_dxf_to_pdf.command
```

单文件：

```bash
./run_dxf_to_pdf.command "/path/to/file.dxf"
```

指定批量输入与输出文件夹：

```bash
./run_dxf_to_pdf.command "/path/to/input_folder" "/path/to/output_folder"
```

## Windows（一键运行）

### 方式 1：双击（默认批量）

双击：

- `run_dxf_to_pdf.bat`

要求：当前目录中存在 `data\\input\\` 文件夹（已预置空目录）。

### 方式 2：拖拽文件（单文件）

把 `.dxf` 文件拖到 `run_dxf_to_pdf.bat` 上。

### 方式 3：拖拽文件夹（批量）

把某个文件夹拖到 `run_dxf_to_pdf.bat` 上。

### 方式 4：CMD 命令行运行

```bat
cd C:\path\to\dxf-to-pdf-toolkit
run_dxf_to_pdf.bat
```

单文件：

```bat
run_dxf_to_pdf.bat "C:\path\to\file.dxf"
```

批量指定输入与输出：

```bat
run_dxf_to_pdf.bat "C:\path\to\input_folder" "C:\path\to\output_folder"
```

## 默认转换参数（已内置）

默认参数针对配电/单线图场景做了优化：

- `--layout modelspace`
- 白底黑线：`--bg "#FFFFFF" --fg "#000000"`
- `--mtext-line-spacing-scale 1.15`
- 启用中文碰撞触发换行：`--mtext-smart-wrap-cjk-collision`
- 碰撞后按最多 10 字符换行：`--mtext-smart-wrap-cjk-chars 10`

说明：只有检测到“同排邻近文字可能横向重叠”时，才会触发换行，不会全局无脑换行。

## 可选环境变量（进阶）

你可以在运行前设置这些环境变量（主要影响批量模式，也可影响单文件模式）：

- `CAD2PDF_LIMIT`：只处理前 N 个文件（批量）
- `CAD2PDF_MATCH`：仅处理路径中包含指定关键词的文件（批量）
- `CAD2PDF_SKIP_EXISTING=1`：跳过已有 PDF（批量）
- `CAD2PDF_LAYOUT`：`modelspace` / `paperspace` / 布局名
- `CAD2PDF_SIZE_INCHES`：例如 `11x17`
- `CAD2PDF_SMART_WRAP_CJK_CHARS`：碰撞换行字符上限（默认 `10`）
- `CAD2PDF_MTEXT_LINE_SPACING_SCALE`：默认 `1.15`
- `CAD2PDF_MTEXT_WIDTH_SCALE`：默认 `1.0`

### macOS 示例

```bash
CAD2PDF_LIMIT=10 CAD2PDF_MATCH=桂花 ./run_dxf_to_pdf.command
```

### Windows 示例（CMD）

```bat
set CAD2PDF_LIMIT=10
set CAD2PDF_MATCH=桂花
run_dxf_to_pdf.bat
```

## 输出结果

- 单文件模式：默认输出为同名 `.pdf`
- 批量模式：默认输出到 `data/output/`（或你指定的输出目录）
- 批量模式会额外输出汇总 JSON：
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

建议做法：

1. 将本目录作为 Git 仓库根目录（或拷贝到你的仓库目录）
2. 确认 `.gitignore` 存在（已配置忽略数据和输出）
3. 不要把 `data/input/`、`data/output/`、`.cad2pdf-venv/` 提交到仓库

常见命令：

```bash
git init
git add README.md .gitignore requirements.txt run_dxf_to_pdf.command run_dxf_to_pdf.bat scripts/ data/input/.gitkeep data/output/.gitkeep
git commit -m "Add DXF to PDF toolkit"
```

## 已知限制

- 目前直接稳定支持 `.dxf`；`.dwg` 建议先转换成 `.dxf`
- 某些 CAD 字体（尤其中文字体）在非原生 CAD 渲染器下可能仍有显示差异
- 若严格依赖 CTB/STB 出图样式，建议使用原生 CAD 软件导出 PDF
