#!/usr/bin/env bash
set -euo pipefail
site_dir="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
trial="${1:-}"
mode="${2:-preview}"
case "$trial" in
  1|single) folder=01_visual_interrupt ;;
  2|multi) folder=05_low_multi ;;
  3|memory) folder=07_memory_only ;;
  4|revisit) folder=02_high_view_revisit ;;
  5|priority) folder=06_high_priority ;;
  *) echo "Usage: start_test.sh 1|2|3|4|5 [preview|flight]"; exit 2 ;;
esac
[[ $# -le 2 ]] || { echo "Use the explicit per-module start_real.sh for a separately prepared real release"; exit 2; }
exec bash "$site_dir/../board_trials_4x4/$folder/start.sh" "$mode" --site-config "$site_dir/test_area.yaml"
