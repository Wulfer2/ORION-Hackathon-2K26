import math
import random
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT = Path.home() / "hack"
WORLD_PATH = PROJECT / "simulation/worlds/varuna_mission.sdf"
MODEL_DIR = PROJECT / "simulation/models/island"
MESH_PATH = MODEL_DIR / "island_terrain.obj"
MTL_PATH = MODEL_DIR / "island_terrain.mtl"

random.seed(42)

CENTER_X = -45.0
CENTER_Y = 0.0
RADIUS = 62.0
TREE_COUNT = 42

def terrain_height(x, y):
    distance = math.hypot(x, y)

    if math.hypot(x - 45.0, y) <= 9.0:
        return 1.8

    edge_factor = max(0.0, min(1.0, (RADIUS - distance) / 18.0))

    hills = (
        2.2 * math.sin(x * 0.075 + y * 0.025)
        + 1.4 * math.sin(y * 0.11 - x * 0.035)
        + 0.8 * math.sin(x * 0.16 + y * 0.12)
    )

    transition = max(
        0.0,
        min(1.0, (math.hypot(x - 45.0, y) - 9.0) / 7.0)
    )

    height = 1.8 + transition * (2.5 + hills) * edge_factor

    if distance > RADIUS - 5.0:
        height = min(height, 1.8 * edge_factor)

    return height

tree = ET.parse(WORLD_PATH)
root = tree.getroot()
world = root.find("world")
island = world.find("./model[@name='island']")

if island is None:
    raise RuntimeError("Island model not found")

link = island.find("./link[@name='terrain']")

if link is None:
    raise RuntimeError("Island terrain link not found")

for visual in list(link.findall("visual")):
    if visual.get("name", "").startswith("palm_"):
        link.remove(visual)

MTL_PATH.write_text(
    "newmtl IslandGrass\n"
    "Ka 0.22 0.30 0.13\n"
    "Kd 0.34 0.46 0.23\n"
    "Ks 0.05 0.05 0.05\n"
    "Ns 12\n"
)

mesh_text = MESH_PATH.read_text()

if "mtllib island_terrain.mtl" not in mesh_text:
    mesh_text = mesh_text.replace(
        "o tropical_island\n",
        "mtllib island_terrain.mtl\n"
        "o tropical_island\n"
        "usemtl IslandGrass\n",
        1
    )
    MESH_PATH.write_text(mesh_text)

visual = link.find("./visual[@name='terrain_visual']")

if visual is not None:
    material = visual.find("material")

    if material is None:
        material = ET.SubElement(visual, "material")

    for tag, value in (
        ("ambient", "0.22 0.30 0.13 1"),
        ("diffuse", "0.34 0.46 0.23 1"),
        ("specular", "0.05 0.05 0.05 1"),
    ):
        element = material.find(tag)

        if element is None:
            element = ET.SubElement(material, tag)

        element.text = value

    pbr = material.find("pbr")

    if pbr is None:
        pbr = ET.SubElement(material, "pbr")

    metal = pbr.find("metal")

    if metal is None:
        metal = ET.SubElement(pbr, "metal")

    roughness = metal.find("roughness")

    if roughness is None:
        roughness = ET.SubElement(metal, "roughness")

    roughness.text = "0.9"

def add_visual(name, pose, geometry_xml, color):
    visual = ET.SubElement(link, "visual", {"name": name})
    ET.SubElement(visual, "pose").text = pose
    visual.append(ET.fromstring(geometry_xml))

    material = ET.SubElement(visual, "material")
    ET.SubElement(material, "ambient").text = color
    ET.SubElement(material, "diffuse").text = color

for i in range(TREE_COUNT):
    for attempt in range(200):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(18.0, 53.0)

        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        distance_to_pad = math.hypot(x - 45.0, y)

        if distance_to_pad < 13.0:
            continue

        if x > 42.0 and abs(y) < 15.0:
            continue

        if math.hypot(x, y) > 56.0:
            continue

        break
    else:
        continue

    ground_z = terrain_height(x, y)
    height = random.uniform(5.0, 8.5)
    trunk_height = height * 0.72
    trunk_radius = random.uniform(0.14, 0.22)
    crown_z = ground_z + trunk_height
    trunk_color = "0.34 0.19 0.09 1"
    leaf_color = "0.10 0.34 0.10 1"

    add_visual(
        f"palm_{i:02d}_trunk",
        f"{x:.3f} {y:.3f} {ground_z + trunk_height / 2:.3f} 0 0 0",
        f"<geometry><cylinder><radius>{trunk_radius:.3f}</radius>"
        f"<length>{trunk_height:.3f}</length></cylinder></geometry>",
        trunk_color
    )

    add_visual(
        f"palm_{i:02d}_crown",
        f"{x:.3f} {y:.3f} {crown_z + 0.15:.3f} 0 0 0",
        "<geometry><sphere><radius>0.32</radius></sphere></geometry>",
        leaf_color
    )

    for j in range(8):
        leaf_angle = 2 * math.pi * j / 8 + random.uniform(-0.15, 0.15)
        leaf_length = random.uniform(2.0, 3.2)
        leaf_width = random.uniform(0.16, 0.24)

        leaf_x = x + math.cos(leaf_angle) * leaf_length * 0.38
        leaf_y = y + math.sin(leaf_angle) * leaf_length * 0.38
        leaf_z = crown_z + random.uniform(-0.25, 0.25)
        pitch = random.uniform(-0.25, 0.35)

        add_visual(
            f"palm_{i:02d}_leaf_{j:02d}",
            f"{leaf_x:.3f} {leaf_y:.3f} {leaf_z:.3f} "
            f"0 {pitch:.3f} {leaf_angle:.3f}",
            f"<geometry><box><size>{leaf_length:.2f} "
            f"{leaf_width:.2f} 0.08</size></box></geometry>",
            leaf_color
        )

ET.indent(tree, space="  ")
tree.write(WORLD_PATH, encoding="utf-8", xml_declaration=True)

print("Island material and coconut palms updated.")
print(f"Terrain mesh: {MESH_PATH}")
print(f"Mesh material: {MTL_PATH}")
print(f"Requested palm count: {TREE_COUNT}")
print("Trees remain visual-only.")
print("Takeoff pad and vessel positions were not changed.")

