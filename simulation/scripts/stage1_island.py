import math
import xml.etree.ElementTree as ET
from pathlib import Path

world_path = Path.home() / "hack/simulation/worlds/varuna_mission.sdf"

tree = ET.parse(world_path)
root = tree.getroot()
world = root.find("world")
island = world.find("./model[@name='island']")
land = island.find("./link[@name='land']")

if island is None or land is None:
    raise RuntimeError("Could not find the existing island and land link")

for visual in list(land.findall("visual")):
    if visual.get("name", "").startswith("stage1_"):
        land.remove(visual)

def add_visual(name, pose, geometry, material):
    visual = ET.SubElement(land, "visual", {"name": name})
    ET.SubElement(visual, "pose").text = pose
    visual.append(ET.fromstring(geometry))

    mat = ET.SubElement(visual, "material")
    ET.SubElement(mat, "ambient").text = material
    ET.SubElement(mat, "diffuse").text = material

add_visual(
    "stage1_landing_pad",
    "0 0 6.07 0 0 0",
    "<geometry><cylinder><radius>7</radius><length>0.12</length></cylinder></geometry>",
    "0.18 0.2 0.22 1"
)

add_visual(
    "stage1_landing_h_left",
    "0 0 6.145 0 0 0",
    "<geometry><box><size>0.8 4 0.02</size></box></geometry>",
    "0.95 0.95 0.9 1"
)

add_visual(
    "stage1_landing_h_right",
    "0 0 6.145 0 0 0",
    "<geometry><box><size>0.8 4 0.02</size></box></geometry>",
    "0.95 0.95 0.9 1"
)

for name, x in [("stage1_h_bar_top", -1.6), ("stage1_h_bar_bottom", 1.6)]:
    add_visual(
        name,
        f"{x} 0 6.145 0 0 0",
        "<geometry><box><size>4 0.65 0.02</size></box></geometry>",
        "0.95 0.95 0.9 1"
    )

for i in range(12):
    angle = 2 * math.pi * i / 12
    radius = 19 if i % 2 == 0 else 23
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)

    trunk_height = 2.8
    canopy_radius = 1.8 if i % 3 else 2.2

    add_visual(
        f"stage1_tree_{i:02d}_trunk",
        f"{x:.3f} {y:.3f} {6 + trunk_height / 2:.3f} 0 0 0",
        f"<geometry><cylinder><radius>0.22</radius><length>{trunk_height}</length></cylinder></geometry>",
        "0.3 0.17 0.08 1"
    )

    add_visual(
        f"stage1_tree_{i:02d}_canopy",
        f"{x:.3f} {y:.3f} {9.1:.3f} 0 0 0",
        f"<geometry><sphere><radius>{canopy_radius}</radius></sphere></geometry>",
        "0.12 0.32 0.12 1"
    )

ET.indent(tree, space="  ")
tree.write(world_path, encoding="utf-8", xml_declaration=True)

print("Stage 1 island visuals added.")
print(f"Updated: {world_path}")
