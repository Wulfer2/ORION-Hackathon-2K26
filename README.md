# ORION-Hackathon-2K26
This repository contains all the required documents for the hackathon

Day - 01:

**SHIP-TO-SHORE and Island Supply Drone**
The problem statement requries our team to design a drone that will be capable of the following:
1. Deliver 5 kg of supplies between a vessel and an island. (We assume here the task involved would be picking and dropping the payload both to and from the island).
2. 15 km each way. (Generally, a vessel that far into the sea may not be visible to a anyone viewing the horizon from the shoreline. The only way to view an oncoming vessel is if they gain a 30m elevation atop a lighthouse.)
3. Landing on or dropping to a moving platform. (The drone has to autonomously detect the target position, which it shall reach using GPS navigation. Using the sensors/camera on board, it'll have to slowly lower the 5kg payload onto a moving platform)

Following are the requirements for the drone:
1. Corrosion resistant materials and sealing. (Due to the spray of salt-water or the occasional shoreline storm, the UAV should be durable enough to withstand all that)
2. Resist winds to about 12m/s plus platform motion of up to 2m/s.
3. Energy reserve for the round-trip.
4. Failsafes built-in in case of lost comms, discharged battery, or adverse conditions.

The justification needs to be provided for all the decisions that are taken, majorly:
1. VTOL v/s multirotor.
2. Landing or winch method to deliver the package.
3. Corrosion protection strategy.

The branches that have been updated by day 1:
1. simulations/prashanth
2. Aerodynamic design constraints
3. cad models
4. uav model simulation
