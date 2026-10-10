import math
import xml.etree.ElementTree as ET
from pathlib import Path

world_path = Path.home() / "hack/simulation/worlds/varuna_mission.sdf"

tree = ET.parse(world_path)
root = tree.getroot()
world = root.find("world")

ocean = world.find("./model[@name='ocean']")

if ocean is None:
    raise RuntimeError("Ocean model not found")

surface = ocean.find("./link[@name='surface']")
visual = surface.find("./visual[@name='visual']")

if surface is None or visual is None:
    raise RuntimeError("Ocean surface visual not found")

material = visual.find("material")

if material is None:
    material = ET.SubElement(visual, "material")

for tag, value in (
    ("ambient", "0.025 0.18 0.29 1"),
    ("diffuse", "0.035 0.27 0.40 1"),
    ("specular", "0.32 0.42 0.48 1"),
):
    element = material.find(tag)

    if element is None:
        element = ET.SubElement(material, tag)

    element.text = value

waves = world.find("./model[@name='ocean_wave_visuals']")

if waves is not None:
    world.remove(waves)

waves = ET.SubElement(world, "model", {"name": "ocean_wave_visuals"})
ET.SubElement(waves, "static").text = "true"

link = ET.SubElement(waves, "link", {"name": "wave_lines"})

for row in range(18):
    y = -70 + row * 8.0

    for segment in range(15):
        x = -45 + segment * 14.0
        phase = row * 0.83 + segment * 0.36

        length = 9.0
        amplitude = 0.65

        y1 = y + amplitude * math.sin(phase)
        y2 = y + amplitude * math.sin(phase + 0.65)

        dx = length
        dy = y2 - y1
        yaw = math.atan2(dy, dx)

        cx = x + dx / 2
        cy = (y1 + y2) / 2

        visual = ET.SubElement(
            link,
            "visual",
            {"name": f"wave_{row:02d}_{segment:02d}"}
        )

        ET.SubElement(visual, "pose").text = (
            f"{cx:.3f} {cy:.3f} 0.025 0 0 {yaw:.5f}"
        )

        geometry = ET.SubElement(visual, "geometry")
        box = ET.SubElement(geometry, "box")
        ET.SubElement(box, "size").text = "9.0 0.035 0.008"

        mat = ET.SubElement(visual, "material")
        ET.SubElement(mat, "ambient").text = "0.18 0.43 0.52 1"
        ET.SubElement(mat, "diffuse").text = "0.18 0.43 0.52 1"

ET.indent(tree, space="  ")
tree.write(world_path, encoding="utf-8", xml_declaration=True)

print("Ocean material updated.")
print("Visual-only wave patterns added.")
print("No water forces or buoyancy were added.")
print(f"Updated world: {world_path}")
