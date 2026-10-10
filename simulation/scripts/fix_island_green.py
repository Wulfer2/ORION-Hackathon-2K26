import math
from pathlib import Path

project = Path.home() / "hack"
mesh_path = project / "simulation/models/island/island_terrain.obj"
mtl_path = project / "simulation/models/island/island_terrain.mtl"

lines = mesh_path.read_text().splitlines()
vertices = []
faces = []

for line in lines:
    parts = line.split()

    if not parts:
        continue

    if parts[0] == "v" and len(parts) >= 4:
        vertices.append(tuple(map(float, parts[1:4])))

    elif parts[0] == "f" and len(parts) >= 4:
        face = [int(part.split("/")[0]) for part in parts[1:]]
        for i in range(1, len(face) - 1):
            faces.append((face[0], face[i], face[i + 1]))

normal_sums = [[0.0, 0.0, 0.0] for _ in vertices]

def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )

for a, b, c in faces:
    p1 = vertices[a - 1]
    p2 = vertices[b - 1]
    p3 = vertices[c - 1]

    edge1 = tuple(p2[i] - p1[i] for i in range(3))
    edge2 = tuple(p3[i] - p1[i] for i in range(3))
    normal = cross(edge1, edge2)

    for index in (a - 1, b - 1, c - 1):
        for axis in range(3):
            normal_sums[index][axis] += normal[axis]

normals = []

for normal in normal_sums:
    length = math.sqrt(sum(value * value for value in normal))

    if length < 1e-12:
        normals.append((0.0, 0.0, 1.0))
    else:
        normals.append(tuple(value / length for value in normal))

mtl_path.write_text(
    "newmtl IslandGrass\n"
    "Ka 0.20 0.30 0.12\n"
    "Kd 0.32 0.48 0.20\n"
    "Ks 0.04 0.04 0.04\n"
    "Ns 12\n"
)

with mesh_path.open("w") as mesh:
    mesh.write("mtllib island_terrain.mtl\n")
    mesh.write("o tropical_island\n")
    mesh.write("usemtl IslandGrass\n")

    for vertex in vertices:
        mesh.write("v {:.7f} {:.7f} {:.7f}\n".format(*vertex))

    for normal in normals:
        mesh.write("vn {:.7f} {:.7f} {:.7f}\n".format(*normal))

    for a, b, c in faces:
        mesh.write(f"f {a}//{a} {b}//{b} {c}//{c}\n")

print(f"Vertices: {len(vertices)}")
print(f"Triangles: {len(faces)}")
print("Terrain normals regenerated.")
print("Green OBJ material reference restored.")
print(f"Mesh: {mesh_path}")
print(f"Material: {mtl_path}")
