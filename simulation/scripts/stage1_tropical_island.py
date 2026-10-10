import math
import random
import xml.etree.ElementTree as ET
from pathlib import Path

WORLD_PATH = Path.home() / "hack/simulation/worlds/varuna_mission.sdf"

ISLAND_CENTER_X = -30.0
ISLAND_RADIUS = 38.0
VESSEL_X = 100.0
TREE_COUNT = 45

random.seed(26)

tree = ET.parse(WORLD_PATH)
root = tree.getroot()
world = root.find("world")

if world is None:
    raise RuntimeError("World element not found")

for name in ("island",):
    model = world.find(f"./model[@name='{name}']")
    if model is not None:
        world.remove(model)

island = ET.SubElement(world, "model", {"name": "island"})
ET.SubElement(island, "static").text = "true"
ET.SubElement(island, "pose").text = f"{ISLAND_CENTER_X} 0 0 0 0 0"

land = ET.SubElement(island, "link", {"name": "land"})

def add_geometry(parent, name, pose, geometry_xml, color):
    visual = ET.SubElement(parent, "visual", {"name": name})
    ET.SubElement(visual, "pose").text = pose
    visual.append(ET.fromstring(geometry_xml))

    material = ET.SubElement(visual, "material")
    ET.SubElement(material, "ambient").text = color
    ET.SubElement(material, "diffuse").text = color

def add_land_section(name, x, y, radius, length=6.0):
    pose = f"{x} {y} {-length / 2} 0 0 0"
    geometry = (
        f"<geometry><cylinder><radius>{radius}</radius>"
        f"<length>{length}</length></cylinder></geometry>"
    )

    collision = ET.SubElement(land, "collision", {"name": f"{name}_collision"})
    ET.SubElement(collision, "pose").text = pose
    collision.append(ET.fromstring(geometry))

    add_geometry(
        land,
        f"{name}_visual",
        pose,
        geometry,
        "0.34 0.43 0.23 1"
    )

add_land_section("main_land", 0, 0, 38)
add_land_section("north_land", -12, 17, 23)
add_land_section("south_land", -15, -18, 25)
add_land_section("west_land", -31, 0, 25)

pad_x = -ISLAND_CENTER_X

add_geometry(
    land,
    "landing_pad",
    f"{pad_x} 0 0.07 0 0 0",
    "<geometry><cylinder><radius>7</radius><length>0.12</length></cylinder></geometry>",
    "0.17 0.19 0.20 1"
)

add_geometry(
    land,
    "landing_H_vertical_left",
    f"{pad_x - 1.6} 0 0.145 0 0 0",
    "<geometry><box><size>0.7 3.8 0.02</size></box></geometry>",
    "0.95 0.95 0.9 1"
)

add_geometry(
    land,
    "landing_H_vertical_right",
    f"{pad_x + 1.6} 0 0.145 0 0 0",
    "<geometry><box><size>0.7 3.8 0.02</size></box></geometry>",
    "0.95 0.95 0.9 1"
)

add_geometry(
    land,
    "landing_H_crossbar",
    f"{pad_x} 0 0.145 0 0 0",
    "<geometry><box><size>3.8 0.7 0.02</size></box></geometry>",
    "0.95 0.95 0.9 1"
)

for i in range(TREE_COUNT):
    for attempt in range(100):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(12, 34)

        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        world_x = ISLAND_CENTER_X + x

        if math.hypot(world_x, y) < 12:
            continue

        if world_x > -4 and abs(y) < 14:
            continue

        if math.hypot(x + 12, y - 17) < 5:
            continue

        if math.hypot(x + 15, y + 18) < 5:
            continue

        if math.hypot(x + 31, y) < 5:
            continue

        break
    else:
        continue

    height = random.uniform(5.0, 9.0)
    trunk_radius = random.uniform(0.16, 0.24)
    trunk_top = height * 0.72
    crown_z = height * 0.82
    leaf_length = random.uniform(2.0, 3.2)

    add_geometry(
        land,
        f"palm_{i:02d}_trunk",
        f"{x:.3f} {y:.3f} {trunk_top / 2:.3f} 0 0 0",
        f"<geometry><cylinder><radius>{trunk_radius:.3f}</radius>"
        f"<length>{trunk_top:.3f}</length></cylinder></geometry>",
        "0.34 0.20 0.10 1"
    )

    add_geometry(
        land,
        f"palm_{i:02d}_crown",
        f"{x:.3f} {y:.3f} {crown_z:.3f} 0 0 0",
        "<geometry><sphere><radius>0.32</radius></sphere></geometry>",
        "0.12 0.28 0.08 1"
    )

    for j in range(7):
        angle = 2 * math.pi * j / 7 + random.uniform(-0.12, 0.12)
        leaf_x = x + math.cos(angle) * leaf_length * 0.35
        leaf_y = y + math.sin(angle) * leaf_length * 0.35
        pitch = random.uniform(-0.45, 0.15)
        yaw = angle

        leaf_geometry = (
            f"<geometry><box><size>{leaf_length:.2f} "
            f"0.22 0.10</size></box></geometry>"
        )

        add_geometry(
            land,
            f"palm_{i:02d}_leaf_{j:02d}",
            f"{leaf_x:.3f} {leaf_y:.3f} "
            f"{crown_z + pitch:.3f} 0 0 {yaw:.3f}",
            leaf_geometry,
            "0.12 0.36 0.10 1"
        )

vessel = world.find("./model[@name='supply_vessel']")
if vessel is not None:
    vessel.find("pose").text = f"{VESSEL_X} 0 0 0 0 0"

platform = world.find("./model[@name='moving_landing_platform']")
if platform is not None:
    platform.find("pose").text = f"{VESSEL_X} 0 2.4 0 0 0"

ET.indent(tree, space="  ")
tree.write(WORLD_PATH, encoding="utf-8", xml_declaration=True)

print("Tropical island generated.")
print("Takeoff pad: (0, 0, 0)")
print(f"Island centre: ({ISLAND_CENTER_X}, 0, 0)")
print(f"Vessel reference position: ({VESSEL_X}, 0, 0)")
print(f"Generated palm trees: {TREE_COUNT}")
print(f"Updated world: {WORLD_PATH}")
