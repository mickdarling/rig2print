"""Regression: a surface T-junction must become conforming STL triangles."""

from pathlib import Path
import sys
import tempfile

import bmesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prototype_joint import export_stl, mesh_object, triangulate_closed
from check_stl import check_stl


vertices = [(0, 0, 0), (2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 0, 0)]
# One side of edge 0--1 has an extra collinear corner; the other side does not.
faces = [(0, 2, 1), (0, 4, 3), (4, 1, 3), (1, 2, 3), (2, 0, 3)]
obj = mesh_object("T-junction regression", vertices, faces)
bm = bmesh.new()
bm.from_mesh(obj.data)
assert sum(e.is_boundary for e in bm.edges) == 3
triangulate_closed(bm)
assert all(e.is_manifold for e in bm.edges)
bm.to_mesh(obj.data)
bm.free()
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "repaired.stl"
    export_stl(path, [obj])
    report = check_stl(path)
    assert report["nonmanifold_edges"] == 0, report
    assert report["components"] == 1, report
    assert abs(report["signed_volume_mm3"]-4/3) < 1e-6, report
print("Blender STL T-junction regression passed")

# Opposite coincident triangles have zero net surface. A Boolean n-gon can
# produce such a pair; cancelling it must preserve the surrounding solid.
obj = mesh_object("opposite surface regression",
    [(0, 0, 0), (2, 0, 0), (0, 2, 0), (0, 0, 2), (0.5, 0.2, 0.2)],
    [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3), (0, 1, 4), (1, 0, 4)])
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "opposite.stl"
    export_stl(path, [obj])
    report = check_stl(path)
    assert report["nonmanifold_edges"] == 0, report
    assert report["components"] == 1, report
    assert abs(report["signed_volume_mm3"]-4/3) < 1e-6, report
print("Blender STL opposite-surface regression passed")
