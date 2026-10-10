#!/usr/bin/env bash
set -eo pipefail

PROJECT="$HOME/hack"
PX4="$HOME/PX4-Autopilot"

source /opt/ros/humble/setup.bash

export GZ_SIM_RESOURCE_PATH="$PROJECT/simulation/models:$PX4/Tools/simulation/gz/models${GZ_SIM_RESOURCE_PATH:+:$GZ_SIM_RESOURCE_PATH}"
export GZ_SIM_SYSTEM_PLUGIN_PATH="$PX4/build/px4_sitl_default/src/modules/simulation/gz_plugins${GZ_SIM_SYSTEM_PLUGIN_PATH:+:$GZ_SIM_SYSTEM_PLUGIN_PATH}"
export PX4_GZ_WORLD="varuna_mission"
export PX4_GZ_WORLDS="$PROJECT/simulation/worlds"
export PX4_GZ_PLATFORM_VEL="${PX4_GZ_PLATFORM_VEL:-2.0}"
export PX4_GZ_PLATFORM_HEADING_DEG="${PX4_GZ_PLATFORM_HEADING_DEG:-0}"

python3 "$PROJECT/simulation/scripts/build_world.py"

cd "$PX4"
exec make px4_sitl gz_x500
