import math
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT = Path.home() / "hack"
WORLD_PATH = PROJECT / "simulation/worlds/varuna_mission.sdf"
MESH_PATH = PROJECT / "simulation/models/island/island_terrain.obj"

CENTER_X = -45.0
CENTER_Y = 0.0
BASE_Z = -4.0
PAD_Z = 1.8
RADIUS = 62.0
RADIAL_STEPS = 32
ANGLE_STEPS = 96

vertices = []
faces = []

def boundary_radius(angle):
    return RADIUS * (
        1.0
        + 0.045 * math.sin(3 * angle + 0.4)
        + 0.035 * math.sin(5 * angle - 0.8)
        + 0.020 * math.sin(8 * angle)
    )

def terrain_height(x, y):
    pad_distance = math.hypot(x - 45.0, y)

    if pad_distance <= 9.0:
        return PAD_Z

    edge_distance = math.hypot(x, y)
    edge_factor = max(0.0, min(1.0, (RADIUS - edge_distance) / 18.0))

    hills = (
        2.2 * math.sin(x * 0.075 + y * 0.025)
        + 1.4 * math.sin(y * 0.11 - x * 0.035)
        + 0.8 * math.sin(x * 0.16 + y * 0.12)
    )

    transition = max(0.0, min(1.0, (pad_distance - 9.0) / 7.0))
    height = PAD_Z + transition * (2.5 + hills) * edge_factor

    if edge_distance > RADIUS - 5.0:
        height = min(height, PAD_Z * edge_factor)

    return height

vertices.append((0.0, 0.0, terrain_height(0.0, 0.0)))

for ring in range(1, RADIAL_STEPS + 1):
    fraction = ring / RADIAL_STEPS

    for index in range(ANGLE_STEPS):
        angle = 2 * math.pi * index / ANGLE_STEPS
        radius = fraction * boundary_radius(angle)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = terrain_height(x, y)

        vertices.append((x, y, z))

def surface_index(ring, angle_index):
    return 1 + (ring - 1) * ANGLE_STEPS + (angle_index % ANGLE_STEPS)

for j in range(ANGLE_STEPS):
    faces.append((1, surface_index(1, j), surface_index(1, j + 1)))

for ring in range(1, RADIAL_STEPS):
    for j in range(ANGLE_STEPS):
        a = surface_index(ring, j)
        b = surface_index(ring + 1, j)
        c = surface_index(ring + 1, j + 1)
        d = surface_index(ring, j + 1)

        faces.append((a, b, c))
        faces.append((a, c, d))

top_vertex_count = len(vertices)

for index in range(ANGLE_STEPS):
    x, y, _ = vertices[surface_index(RADIAL_STEPS, index) - 1]
    vertices.append((x, y, BASE_Z))

bottom_center = len(vertices) + 1
vertices.append((0.0, 0.0, BASE_Z))

for j in range(ANGLE_STEPS):
    top_a = surface_index(RADIAL_STEPS, j)
    top_b = surface_index(RADIAL_STEPS, j + 1)
    bottom_a = top_vertex_count + j + 1
    bottom_b = top_vertex_count + ((j + 1) % ANGLE_STEPS) + 1

    faces.append((top_a, bottom_a, bottom_b))
    faces.append((top_a, bottom_b, top_b))
    faces.append((bottom_center, bottom_b, bottom_a))

MESH_PATH.parent.mkdir(parents=True, exist_ok=True)

with MESH_PATH.open("w") as mesh_file:
    mesh_file.write("o tropical_island\n")

    for x, y, z in vertices:
        mesh_file.write(f"v {x:.5f} {y:.5f} {z:.5f}\n")

    for a, b, c in faces:
        mesh_file.write(f"f {a} {b} {c}\n")

tree = ET.parse(WORLD_PATH)
root = tree.getroot()
world = root.find("world")

if world is None:
    raise RuntimeError("World element not found")

old_island = world.find("./model[@name='island']")

if old_island is None:
    raise RuntimeError("Island model not found")

world.remove(old_island)

island = ET.SubElement(world, "model", {"name": "island"})
ET.SubElement(island, "static").text = "true"
ET.SubElement(island, "pose").text = f"{CENTER_X} {CENTER_Y} 0 0 0 0"

link = ET.SubElement(island, "link", {"name": "terrain"})

def add_mesh_geometry(parent, name):
    element = ET.SubElement(parent, name)
    geometry = ET.SubElement(element, "geometry")
    mesh = ET.SubElement(geometry, "mesh")
    ET.SubElement(mesh, "uri").text = str(MESH_PATH)
    return element

add_mesh_geometry(link, "collision").set("name", "terrain_collision")

visual = add_mesh_geometry(link, "visual")
visual.set("name", "terrain_visual")

material = ET.SubElement(visual, "material")
ET.SubElement(material, "ambient").text = "0.34 0.42 0.25 1"
ET.SubElement(material, "diffuse").text = "0.40 0.49 0.29 1"

pad_x = -CENTER_X

pad = ET.SubElement(link, "visual", {"name": "landing_pad"})
ET.SubElement(pad, "pose").text = f"{pad_x} 0 {PAD_Z + 0.04} 0 0 0"

geometry = ET.SubElement(pad, "geometry")
cylinder = ET.SubElement(geometry, "cylinder")
ET.SubElement(cylinder, "radius").text = "7"
ET.SubElement(cylinder, "length").text = "0.08"

material = ET.SubElement(pad, "material")
ET.SubElement(material, "ambient").text = "0.16 0.18 0.20 1"
ET.SubElement(material, "diffuse").text = "0.16 0.18 0.20 1"

ET.indent(tree, space="  ")
tree.write(WORLD_PATH, encoding="utf-8", xml_declaration=True)

print("Closed terrain mesh generated.")
print(f"Mesh: {MESH_PATH}")
print(f"Island centre: ({CENTER_X}, {CENTER_Y}, 0)")
print("Terrain visual and collision mesh added.")
print("Landing pad positioned at the world origin.")
