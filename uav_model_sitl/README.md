Installation

1. Copy the models/thunderb_vtol folder into your PX4-Autopilot/Tools/simulation/gz/models/ directory.

2. Copy the worlds/wind_test.sdf file into PX4-Autopilot/Tools/simulation/gz/worlds/.

3. Copy the init.d/4050_thunderb_vtol script into PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes/.

4. To run the simulation, execute: make px4_sitl gz_thunderb_vtol
