#!/usr/bin/env bash
# Source this file; it only selects the deployed workspace, never starts nodes.
BOARD_TRIAL_ROOT="$(cd "${BASH_SOURCE[0]%/*}/../.." && pwd)"
source /opt/ros/noetic/setup.bash
source "$BOARD_TRIAL_ROOT/vision_ws/devel/setup.bash"
source "$BOARD_TRIAL_ROOT/patrol_uav_ws-patrol_planner/devel/setup.bash" --extend
export UAV_VISION_RKNN_MODEL_PATH="$BOARD_TRIAL_ROOT/runtime_models/flight_5cls_20260928_fp16.rknn"
