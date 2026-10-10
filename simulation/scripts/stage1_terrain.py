import math
import random
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

PROJECT = Path.home() / "hack"
WORLD_PATH = PROJECT / "simulation/worlds/varuna_mission.sdf"
MODEL_DIR = PROJECT / "simulation/models/island"
HEIGHTMAP_PATH = MODEL_DIR / "island_heightmap.png"

random.seed(26)

WIDTH = 256
HEIGHT = 224
TERRAIN_LENGTH = 104.0
TERRAIN_WIDTH = 84.0
TERRAIN_HEIGHT = 10.0

ISLAND_CENTER_X = -40.0
ISLAND_CENTER_Y = 0.0

image = Image.new("L", (WIDTH, HEIGHT), 0)
pixels = image.load()

for py in range(HEIGHT):
    for px in range(WIDTH):
        x = (px / (WIDTH - 1) - 0.5) * TERRAIN_LENGTH
        y = (0.5 - py / (HEIGHT - 1)) * TERRAIN_WIDTH

        angle = math.atan2(y, x)
        boundary = 1.0 + (
            0.055 * math.sin(3 * angle + 0.3)
            + 0.035 * math.sin(5 * angle - 0.7)
            + 0.025 * math.sin(8 * angle)
        )

        nx = x / (TERRAIN_LENGTH * 0.5)
        ny = y / (TERRAIN_WIDTH * 0.5)
        radius = math.sqrt(nx * nx + ny * ny)

        if radius >= boundary:
            pixels[px, py] = 0
            continue

        edge = max(0.0, min(1.0, (boundary - radius) / 0.16))
        elevation = 0.5 + 0.5 * math.sin(5.5 * nx + 1.7 * ny)
        elevation += 0.25 * math.sin(10.0 * ny - 2.0 * nx)
        elevation += 0.15 * math.sin(15.0 * nx + 8.0 * ny)
        elevation = max(0.0, min(1.0, elevation / 1.9))

        height_value = 45 + int(170 * elevation * edge)
        pixels[px, py] = max(0, min(255, height_value))

pad_px = int((0.0 - (ISLAND_CENTER_X - TERRAIN_LENGTH / 2)) / TERRAIN_LENGTH * (WIDTH - 1))
pad_py = int((TERRAIN_WIDTH / 2) / TERRAIN_WIDTH * (HEIGHT - 1))

for py in range(max(0, pad_py - 12), min(HEIGHT, pad_py + 13)):
    for px in range(max(0, pad_px - 12), min(WIDTH, pad_px + 13)):
        x = (px / (WIDTH - 1) - 0.5) * TERRAIN_LENGTH
        y = (0.5 - py / (HEIGHT - 1)) * TERRAIN_WIDTH

        if math.hypot(x - 40.0, y) <= 7.5:
            pixels[px, py] = 45

image.save(HEIGHTMAP_PATH)

tree = ET.parse(WORLD_PATH)
root = tree.getroot()
world = root.find("world")

if world is None:
    raise RuntimeError("World element not found")

old_island = world.find("./model[@name='island']")

if old_island is None:
    raise RuntimeError("Existing island model not found")

world.remove(old_island)

island = ET.SubElement(world, "model", {"name": "island"})
ET.SubElement(island, "static").text = "true"
ET.SubElement(island, "pose").text = (
    f"{ISLAND_CENTER_X} {ISLAND_CENTER_Y} -1.8 0 0 0"
)

link = ET.SubElement(island, "link", {"name": "terrain"})

collision = ET.SubElement(link, "collision", {"name": "terrain_collision"})
geometry = ET.SubElement(collision, "geometry")
heightmap = ET.SubElement(geometry, "heightmap")
ET.SubElement(heightmap, "uri").text = HEIGHTMAP_PATH.as_uri()
ET.SubElement(heightmap, "size").text = (
    f"{TERRAIN_LENGTH} {TERRAIN_WIDTH} {TERRAIN_HEIGHT}"
)
ET.SubElement(heightmap, "pos").text = "0 0 0"

visual = ET.SubElement(link, "visual", {"name": "terrain_visual"})
geometry = ET.SubElement(visual, "geometry")
heightmap = ET.SubElement(geometry, "heightmap")
ET.SubElement(heightmap, "uri").text = HEIGHTMAP_PATH.as_uri()
ET.SubElement(heightmap, "size").text = (
    f"{TERRAIN_LENGTH} {TERRAIN_WIDTH} {TERRAIN_HEIGHT}"
)
ET.SubElement(heightmap, "pos").text = "0 0 0"

material = ET.SubElement(visual, "material")
ET.SubElement(material, "ambient").text = "0.32 0.42 0.23 1"
ET.SubElement(material, "diffuse").text = "0.38 0.48 0.28 1"

pad_x = -ISLAND_CENTER_X

pad = ET.SubElement(link, "visual", {"name": "landing_pad"})
ET.SubElement(pad, "pose").text = f"{pad_x} 0 0.02 0 0 0"
geometry = ET.SubElement(pad, "geometry")
cylinder = ET.SubElement(geometry, "cylinder")
ET.SubElement(cylinder, "radius").text = "7"
ET.SubElement(cylinder, "length").text = "0.04"

material = ET.SubElement(pad, "material")
ET.SubElement(material, "ambient").text = "0.16 0.18 0.2 1"
ET.SubElement(material, "diffuse").text = "0.16 0.18 0.2 1"

ET.indent(tree, space="  ")
tree.write(WORLD_PATH, encoding="utf-8", xml_declaration=True)

print("Heightmap terrain generated.")
print(f"Heightmap: {HEIGHTMAP_PATH}")
print(f"Island reference centre: ({ISLAND_CENTER_X}, {ISLAND_CENTER_Y})")
print("Island terrain collision and visual geometry added.")
print("Landing pad visual added.")
print(f"Updated world: {WORLD_PATH}")
