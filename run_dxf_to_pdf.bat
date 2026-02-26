@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "WORKDIR=%SCRIPT_DIR%"
set "VENV_DIR=%WORKDIR%\.cad2pdf-venv"
set "PYTHON_BIN=%VENV_DIR%\Scripts\python.exe"
set "PIP_BIN=%VENV_DIR%\Scripts\pip.exe"
set "CHECK_ENV_SCRIPT=%WORKDIR%\scripts\check_env.py"
set "SINGLE_SCRIPT=%WORKDIR%\scripts\cad_to_pdf.py"
set "BATCH_SCRIPT=%WORKDIR%\scripts\batch_cad_to_pdf.py"
set "REQUIREMENTS_FILE=%WORKDIR%\requirements.txt"
set "DEFAULT_BATCH_INPUT=%WORKDIR%\data\input"
set "DEFAULT_BATCH_OUTPUT=%WORKDIR%\data\output"

if not defined CAD2PDF_LAYOUT set "CAD2PDF_LAYOUT=modelspace"
if not defined CAD2PDF_BG set "CAD2PDF_BG=#FFFFFF"
if not defined CAD2PDF_FG set "CAD2PDF_FG=#000000"
if not defined CAD2PDF_MTEXT_WIDTH_SCALE set "CAD2PDF_MTEXT_WIDTH_SCALE=1.0"
if not defined CAD2PDF_MTEXT_LINE_SPACING_SCALE set "CAD2PDF_MTEXT_LINE_SPACING_SCALE=1.15"
if not defined CAD2PDF_SMART_WRAP_CJK_CHARS set "CAD2PDF_SMART_WRAP_CJK_CHARS=10"

cd /d "%WORKDIR%"
echo Working directory: %WORKDIR%

if "%~1"=="" (
  call :run_batch "%DEFAULT_BATCH_INPUT%" "%DEFAULT_BATCH_OUTPUT%"
  goto :end
)

if exist "%~1\\" (
  call :run_batch "%~1" "%~2"
  goto :end
)

if exist "%~1" (
  call :run_single "%~1" "%~2"
  goto :end
)

echo ERROR: Argument is neither a file nor a folder: %~1
call :show_usage
set "EXIT_CODE=2"
goto :end

:show_usage
echo Usage (Windows):
echo   1^) Double-click this file to batch convert .\data\input ^> .\data\output
echo   2^) Drag a .dxf file onto this file to convert a single file
echo   3^) Drag a folder onto this file to batch convert that folder
echo.
echo CMD examples:
echo   run_dxf_to_pdf.bat
echo   run_dxf_to_pdf.bat "C:\path\file.dxf"
echo   run_dxf_to_pdf.bat "C:\path\folder" "C:\path\output_folder"
echo.
echo Optional env vars:
echo   set CAD2PDF_LIMIT=10
echo   set CAD2PDF_MATCH=桂花
echo   set CAD2PDF_SKIP_EXISTING=1
echo   set CAD2PDF_SMART_WRAP_CJK_CHARS=10
goto :eof

:ensure_python_env
if exist "%PYTHON_BIN%" goto :check_deps

echo Creating local virtual environment...
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -m venv "%VENV_DIR%"
) else (
  where python >nul 2>nul
  if not %errorlevel%==0 (
    echo ERROR: Python not found. Install Python 3 and re-run.
    exit /b 3
  )
  python -m venv "%VENV_DIR%"
)

:check_deps
"%PYTHON_BIN%" -c "import ezdxf, matplotlib" >nul 2>nul
if %errorlevel%==0 goto :eof

echo Installing dependencies from requirements.txt...
"%PIP_BIN%" install -r "%REQUIREMENTS_FILE%"
exit /b %errorlevel%

:run_single
set "INPUT_PATH=%~1"
set "OUTPUT_PATH=%~2"
if "%OUTPUT_PATH%"=="" set "OUTPUT_PATH=%~dpn1.pdf"

echo Mode: single
echo Input: %INPUT_PATH%
echo Output: %OUTPUT_PATH%

if not exist "%SINGLE_SCRIPT%" (
  echo ERROR: Script not found: %SINGLE_SCRIPT%
  set "EXIT_CODE=1"
  goto :eof
)
if not exist "%INPUT_PATH%" (
  echo ERROR: Input DXF not found: %INPUT_PATH%
  set "EXIT_CODE=2"
  goto :eof
)

call :ensure_python_env
if not %errorlevel%==0 (
  set "EXIT_CODE=%errorlevel%"
  goto :eof
)

"%PYTHON_BIN%" "%SINGLE_SCRIPT%" "%INPUT_PATH%" -o "%OUTPUT_PATH%" --layout "%CAD2PDF_LAYOUT%" --bg "%CAD2PDF_BG%" --fg "%CAD2PDF_FG%" --mtext-width-scale "%CAD2PDF_MTEXT_WIDTH_SCALE%" --mtext-line-spacing-scale "%CAD2PDF_MTEXT_LINE_SPACING_SCALE%" --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars "%CAD2PDF_SMART_WRAP_CJK_CHARS%" --force
set "EXIT_CODE=%errorlevel%"
if exist "%OUTPUT_PATH%" echo Done: %OUTPUT_PATH%
goto :eof

:run_batch
set "INPUT_DIR=%~1"
set "OUTPUT_DIR=%~2"
if "%OUTPUT_DIR%"=="" set "OUTPUT_DIR=%INPUT_DIR%_pdf"

if not exist "%BATCH_SCRIPT%" (
  echo ERROR: Script not found: %BATCH_SCRIPT%
  set "EXIT_CODE=1"
  goto :eof
)
if not exist "%INPUT_DIR%\\" (
  echo ERROR: Input folder not found: %INPUT_DIR%
  echo Tip: place DXF files under "%DEFAULT_BATCH_INPUT%", or drag a folder onto this script.
  echo.
  call :show_usage
  set "EXIT_CODE=2"
  goto :eof
)

call :ensure_python_env
if not %errorlevel%==0 (
  set "EXIT_CODE=%errorlevel%"
  goto :eof
)

for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "STAMP=%%I"
if not defined STAMP set "STAMP=summary"
set "SUMMARY_JSON=%OUTPUT_DIR%\cad2pdf_batch_summary_%STAMP%.json"

set "OPT_SKIP_OR_FORCE=--force"
if "%CAD2PDF_SKIP_EXISTING%"=="1" set "OPT_SKIP_OR_FORCE=--skip-existing"
set "OPT_LIMIT="
if defined CAD2PDF_LIMIT set "OPT_LIMIT=--limit %CAD2PDF_LIMIT%"
set "OPT_MATCH="
if defined CAD2PDF_MATCH set "OPT_MATCH=--match "%CAD2PDF_MATCH%""
set "OPT_SIZE="
if defined CAD2PDF_SIZE_INCHES set "OPT_SIZE=--size-inches %CAD2PDF_SIZE_INCHES%"

echo Mode: batch
echo Input folder: %INPUT_DIR%
echo Output folder: %OUTPUT_DIR%
echo Summary JSON: %SUMMARY_JSON%
if defined CAD2PDF_LIMIT echo Limit: %CAD2PDF_LIMIT%
if defined CAD2PDF_MATCH echo Match: %CAD2PDF_MATCH%
echo.

call "%PYTHON_BIN%" "%BATCH_SCRIPT%" "%INPUT_DIR%" -o "%OUTPUT_DIR%" --layout "%CAD2PDF_LAYOUT%" --bg "%CAD2PDF_BG%" --fg "%CAD2PDF_FG%" --mtext-width-scale "%CAD2PDF_MTEXT_WIDTH_SCALE%" --mtext-line-spacing-scale "%CAD2PDF_MTEXT_LINE_SPACING_SCALE%" --mtext-smart-wrap-cjk-collision --mtext-smart-wrap-cjk-chars "%CAD2PDF_SMART_WRAP_CJK_CHARS%" --summary-json "%SUMMARY_JSON%" %OPT_SKIP_OR_FORCE% %OPT_LIMIT% %OPT_MATCH% %OPT_SIZE%
set "EXIT_CODE=%errorlevel%"
echo.
echo Batch finished. PDFs: %OUTPUT_DIR%
echo Summary: %SUMMARY_JSON%
goto :eof

:end
if not defined EXIT_CODE set "EXIT_CODE=0"
if not "%CAD2PDF_NO_PAUSE%"=="1" pause
exit /b %EXIT_CODE%
