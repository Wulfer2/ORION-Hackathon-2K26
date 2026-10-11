# Varuna Simulation — Contribution & Run Guide

## What I implemented

My contribution to the ORION UAV Design Challenge was the simulation environment and PX4–Gazebo integration. Ishaan Shankar developed the custom `thunderb_vtol` aircraft model; I developed the surrounding environment and control tools and integrated/tested the model.

- Created `simulation/worlds/varuna_mission.sdf`: ocean, island/vegetation, supply vessel, moving landing platform, physics settings and Gazebo plugins.
- Created `simulation/tools/wind_control.py`: GUI for changing wind speed/direction through Gazebo's wind topic.
- Created `simulation/tools/vessel_control.py`: GUI for repositioning the vessel and controlling landing-platform movement.
- Debugged Gazebo resource paths, communication partitions, and PX4/Gazebo sensor and launch configuration.
- Verified takeoff and approximately **10 seconds of stable hover** by the custom VTOL in the Varuna world. A screen recording is available.

**Scope:** this is a simulation milestone, not a completed autonomous island-to-vessel mission. Precision landing, full-route navigation, and flight performance at the maximum wind setting were not verified.

## Software used

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Sim 8.15.0 (Harmonic)
- PX4 Autopilot v1.17.0 (SITL)
- Python 3 / Tkinter, SDF, Gazebo CLI, Git

The custom aircraft files and setup notes are in `uav_model_sitl/`. Read `uav_model_sitl/README.md` before attempting the custom PX4 SITL launch.

## Get the repository

Install the prerequisites above first. PX4 SITL and Gazebo must be installed and working on the machine; cloning this repository alone does not install them.

```bash
git clone --branch simulation/prashanth https://github.com/Wulfer2/ORION-Hackathon-2K26.git
cd ORION-Hackathon-2K26
```

If the repository is private, GitHub access is required.

## Run the Varuna world

Open a terminal and run:

```bash
cd ORION-Hackathon-2K26
source /opt/ros/humble/setup.bash

export GZ_PARTITION=varuna_world_only
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
export QT_QPA_PLATFORM=xcb

export GZ_SIM_RESOURCE_PATH="$PWD/simulation/models:$HOME/PX4-Autopilot/Tools/simulation/gz/models"
export GZ_SIM_SYSTEM_PLUGIN_PATH="/usr/lib/x86_64-linux-gnu/gz-sim-8/plugins:$HOME/PX4-Autopilot/build/px4_sitl_default/src/modules/simulation/gz_plugins"

gz sim -r -v 3 "$PWD/simulation/worlds/varuna_mission.sdf"
```

Adjust the PX4 paths if PX4 is installed somewhere other than `~/PX4-Autopilot`. The NVIDIA environment variables are useful for the development laptop used for this project and may not be needed on other computers.

This command starts the **world only**. It does not launch PX4 or spawn the custom UAV.

## Run the control GUIs

With the Varuna world running, open separate terminals. In each terminal, go to the repository, source ROS 2, and use the same Gazebo partition:

```bash
cd ORION-Hackathon-2K26
source /opt/ros/humble/setup.bash
export GZ_PARTITION=varuna_world_only
python3 simulation/tools/wind_control.py
```

For the vessel and landing-platform controls, use another terminal:

```bash
cd ORION-Hackathon-2K26
source /opt/ros/humble/setup.bash
export GZ_PARTITION=varuna_world_only
python3 simulation/tools/vessel_control.py
```

Keep the partition consistent between Gazebo and the GUIs. A partition mismatch can prevent the controls from reaching the running world.

## Run the custom VTOL / PX4 SITL

Follow the setup and launch instructions in [`uav_model_sitl/README.md`](uav_model_sitl/README.md). The custom model and airframe configuration must be installed where the local PX4 build can find them, and the PX4/Gazebo versions and resource paths must be compatible. Do not assume that starting the world alone will start the aircraft.

The final recorded result was approximately 10 seconds of stable hover in the Varuna world. Results can vary with software versions, GPU/rendering setup, and local PX4/Gazebo configuration.

## Useful paths

| Path | Purpose |
|---|---|
| `simulation/worlds/varuna_mission.sdf` | Main maritime world |
| `simulation/tools/wind_control.py` | Wind control GUI |
| `simulation/tools/vessel_control.py` | Vessel/platform control GUI |
| `uav_model_sitl/` | Custom VTOL model, PX4 airframe file, wind-test world and model README |

## AI assistance

AI tools were used to assist with code drafting, configuration review, and troubleshooting. Changes were reviewed and tested in the local simulation. The hover result above reflects the functionality actually demonstrated; unverified mission capabilities are not claimed.
