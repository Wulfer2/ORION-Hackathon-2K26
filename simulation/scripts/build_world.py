import xml.etree.ElementTree as ET
from pathlib import Path

px4 = Path.home() / "PX4-Autopilot"
project = Path.home() / "hack"
source = px4 / "Tools/simulation/gz/worlds/moving_platform.sdf"
wind_file = Path("/usr/share/gz/gz-sim8/worlds/wind.sdf")
output = project / "simulation/worlds/varuna_mission.sdf"

if not source.exists() or not wind_file.exists():
    raise SystemExit("Required Gazebo world files were not found.")

tree = ET.parse(source)
world = tree.getroot().find("world")
wind_world = ET.parse(wind_file).getroot().find("world")

if world is None or wind_world is None:
    raise SystemExit("Could not read the world files.")

# Use the existing PX4 moving-platform world.
world.set("name", "varuna_mission")

# Use the platform model stored in this project.
for include in world.findall("include"):
    uri = include.find("uri")
    if uri is not None and uri.text == "model://moving_platform":
        uri.text = str(project / "simulation/models/moving_platform/model.sdf")

plugin = next(
    (p for p in wind_world.findall("plugin")
     if "WindEffects" in p.get("name", "")),
    None
)

if plugin is None:
    raise SystemExit("WindEffects plugin was not found.")

plugin = ET.fromstring(ET.tostring(plugin))
plugin.set("name", "gz::sim::systems::WindEffects")
plugin.set("filename", "gz-sim-wind-effects-system")

horizontal = plugin.find("horizontal")

if horizontal is None:
    horizontal = ET.SubElement(plugin, "horizontal")

magnitude = horizontal.find("magnitude")
if magnitude is None:
    magnitude = ET.SubElement(horizontal, "magnitude")
magnitude.text = "12"

direction = horizontal.find("direction")
if direction is None:
    direction = ET.SubElement(horizontal, "direction")
direction.text = "0"

# Add the wind system to the world.
for old in list(world.findall("plugin")):
    if "WindEffects" in old.get("name", ""):
        world.remove(old)

world.append(plugin)

wind = world.find("wind")
if wind is None:
    wind = ET.SubElement(world, "wind")

velocity = wind.find("linear_velocity")
if velocity is None:
    velocity = ET.SubElement(wind, "linear_velocity")
velocity.text = "12 0 0"

ET.indent(tree, space="  ")
output.parent.mkdir(parents=True, exist_ok=True)
tree.write(output, encoding="utf-8", xml_declaration=True)

print(f"World created: {output}")
print("Wind: 12 m/s toward +X")
