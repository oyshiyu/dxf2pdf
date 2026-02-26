#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKDIR="$SCRIPT_DIR"
VENV_DIR="$WORKDIR/.cad2pdf-venv"
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"
CHECK_ENV_SCRIPT="$WORKDIR/scripts/check_env.py"
SINGLE_SCRIPT="$WORKDIR/scripts/cad_to_pdf.py"
BATCH_SCRIPT="$WORKDIR/scripts/batch_cad_to_pdf.py"
REQUIREMENTS_FILE="$WORKDIR/requirements.txt"
DEFAULT_BATCH_INPUT="$WORKDIR/data/input"
DEFAULT_BATCH_OUTPUT="$WORKDIR/data/output"

show_usage() {
  cat <<USAGE
Usage (macOS):
  1) Double-click this file to batch convert ./data/input -> ./data/output
  2) Drag a .dxf file onto this file to convert a single file
  3) Drag a folder onto this file to batch convert that folder

Terminal examples:
  ./run_dxf_to_pdf.command
  ./run_dxf_to_pdf.command "/path/to/file.dxf"
  ./run_dxf_to_pdf.command "/path/to/folder" "/path/to/output_folder"

Optional env vars:
  CAD2PDF_LIMIT=10           # batch only, convert first N files
  CAD2PDF_MATCH=桂花         # batch only, path substring filter
  CAD2PDF_SKIP_EXISTING=1    # batch only, skip existing PDFs
  CAD2PDF_LAYOUT=modelspace|paperspace|Layout1
  CAD2PDF_SMART_WRAP_CJK_CHARS=10
USAGE
}

ensure_python_env() {
  if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Creating local virtual environment..."
    python3 -m venv "$VENV_DIR"
  fi

  if ! "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import ezdxf, matplotlib  # noqa: F401
PY
  then
    echo "Installing dependencies from requirements.txt..."
    "$PIP_BIN" install -r "$REQUIREMENTS_FILE"
  fi
}

run_single() {
  local input_path="$1"
  local output_path="$2"
  local layout_opt="${CAD2PDF_LAYOUT:-modelspace}"
  local bg_opt="${CAD2PDF_BG:-#FFFFFF}"
  local fg_opt="${CAD2PDF_FG:-#000000}"
  local width_scale_opt="${CAD2PDF_MTEXT_WIDTH_SCALE:-1.0}"
  local line_spacing_opt="${CAD2PDF_MTEXT_LINE_SPACING_SCALE:-1.15}"
  local smart_wrap_chars_opt="${CAD2PDF_SMART_WRAP_CJK_CHARS:-10}"

  echo "Mode: single"
  echo "Input: $input_path"
  echo "Output: $output_path"

  if [[ ! -f "$SINGLE_SCRIPT" ]]; then
    echo "ERROR: Script not found: $SINGLE_SCRIPT" >&2
    return 1
  fi
  if [[ ! -f "$input_path" ]]; then
    echo "ERROR: Input DXF not found: $input_path" >&2
    return 2
  fi

  ensure_python_env

  "$PYTHON_BIN" "$SINGLE_SCRIPT" \
    "$input_path" \
    -o "$output_path" \
    --layout "$layout_opt" \
    --bg "$bg_opt" \
    --fg "$fg_opt" \
    --mtext-width-scale "$width_scale_opt" \
    --mtext-line-spacing-scale "$line_spacing_opt" \
    --mtext-smart-wrap-cjk-collision \
    --mtext-smart-wrap-cjk-chars "$smart_wrap_chars_opt" \
    --force

  echo
  [[ -f "$output_path" ]] && echo "Done: $output_path"
}

run_batch() {
  local input_dir="$1"
  local output_dir="${2:-}"
  local layout_opt="${CAD2PDF_LAYOUT:-modelspace}"
  local bg_opt="${CAD2PDF_BG:-#FFFFFF}"
  local fg_opt="${CAD2PDF_FG:-#000000}"
  local width_scale_opt="${CAD2PDF_MTEXT_WIDTH_SCALE:-1.0}"
  local line_spacing_opt="${CAD2PDF_MTEXT_LINE_SPACING_SCALE:-1.15}"
  local smart_wrap_chars_opt="${CAD2PDF_SMART_WRAP_CJK_CHARS:-10}"
  local timestamp="$(date +%Y%m%d_%H%M%S)"
  local summary_json
  local -a cmd

  echo "Mode: batch"
  echo "Input folder: $input_dir"

  if [[ ! -f "$BATCH_SCRIPT" ]]; then
    echo "ERROR: Script not found: $BATCH_SCRIPT" >&2
    return 1
  fi
  if [[ ! -d "$input_dir" ]]; then
    echo "ERROR: Input folder not found: $input_dir" >&2
    echo "Tip: place DXF files under '$DEFAULT_BATCH_INPUT', or drag a folder onto this script." >&2
    echo
    show_usage
    return 2
  fi

  ensure_python_env

  if [[ -z "$output_dir" ]]; then
    output_dir="${input_dir%/}_pdf"
  fi
  summary_json="$output_dir/cad2pdf_batch_summary_${timestamp}.json"

  cmd=(
    "$PYTHON_BIN" "$BATCH_SCRIPT"
    "$input_dir"
    -o "$output_dir"
    --layout "$layout_opt"
    --bg "$bg_opt"
    --fg "$fg_opt"
    --mtext-width-scale "$width_scale_opt"
    --mtext-line-spacing-scale "$line_spacing_opt"
    --mtext-smart-wrap-cjk-collision
    --mtext-smart-wrap-cjk-chars "$smart_wrap_chars_opt"
    --summary-json "$summary_json"
  )

  if [[ "${CAD2PDF_SKIP_EXISTING:-0}" == "1" ]]; then
    cmd+=(--skip-existing)
  else
    cmd+=(--force)
  fi
  [[ -n "${CAD2PDF_LIMIT:-}" ]] && cmd+=(--limit "$CAD2PDF_LIMIT")
  [[ -n "${CAD2PDF_MATCH:-}" ]] && cmd+=(--match "$CAD2PDF_MATCH")
  [[ -n "${CAD2PDF_SIZE_INCHES:-}" ]] && cmd+=(--size-inches "$CAD2PDF_SIZE_INCHES")

  echo "Output folder: $output_dir"
  echo "Summary JSON: $summary_json"
  [[ -n "${CAD2PDF_LIMIT:-}" ]] && echo "Limit: $CAD2PDF_LIMIT"
  [[ -n "${CAD2PDF_MATCH:-}" ]] && echo "Match: $CAD2PDF_MATCH"
  echo

  "${cmd[@]}"

  echo
  echo "Batch finished. PDFs: $output_dir"
  echo "Summary: $summary_json"
}

main() {
  cd "$WORKDIR"
  echo "Working directory: $WORKDIR"

  if [[ $# -eq 0 ]]; then
    run_batch "$DEFAULT_BATCH_INPUT" "$DEFAULT_BATCH_OUTPUT"
    return
  fi

  if [[ -d "$1" ]]; then
    run_batch "$1" "${2:-}"
    return
  fi

  if [[ -f "$1" ]]; then
    local input_path="$1"
    local output_path="${2:-${input_path:r}.pdf}"
    run_single "$input_path" "$output_path"
    return
  fi

  echo "ERROR: Argument is neither a file nor a folder: $1" >&2
  echo
  show_usage
  return 2
}

main "$@"

if [[ -t 0 ]]; then
  echo
  read 'reply?Press Enter to exit... '
fi
