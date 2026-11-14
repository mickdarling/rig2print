"""Run inside Blender. Reads the loaded scene; never saves or changes its file."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import bpy


def topology(mesh):
    mesh.calc_loop_triangles()
    uses = Counter(tuple(sorted(edge)) for tri in mesh.loop_triangles
                   for edge in ((tri.vertices[0], tri.vertices[1]),
                                (tri.vertices[1], tri.vertices[2]),
                                (tri.vertices[2], tri.vertices[0])))
    return {"vertices": len(mesh.vertices), "triangles": len(mesh.loop_triangles),
            "boundary_edges": sum(n == 1 for n in uses.values()),
            "nonmanifold_triangle_edges": sum(n > 2 for n in uses.values())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    source = Path(bpy.data.filepath).resolve()
    output = args.output.resolve()
    if source == output or output.exists():
        raise ValueError("report must be new and cannot overwrite the source")
    scene = bpy.context.scene
    factor = scene.unit_settings.scale_length * 1000.0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    objects = []
    for obj in sorted(scene.objects, key=lambda x: x.name):
        record = {"name": obj.name, "type": obj.type,
                  "parent": obj.parent.name if obj.parent else None,
                  "modifiers": [{"name": m.name, "type": m.type} for m in obj.modifiers]}
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
                record["bounds_mm"] = (None if not points else [
                    [min(p[i] for p in points) * factor for i in range(3)],
                    [max(p[i] for p in points) * factor for i in range(3)]])
                record["topology"] = topology(mesh)
                record["vertex_groups"] = [g.name for g in obj.vertex_groups]
                armature = obj.find_armature()
                record["armature"] = armature.name if armature else None
            finally:
                evaluated.to_mesh_clear()
        if obj.type == "ARMATURE":
            record["bones"] = [{"name": b.name,
                "parent": b.parent.name if b.parent else None, "deform": b.use_deform,
                "head_mm": list((obj.matrix_world @ b.head_local) * factor),
                "tail_mm": list((obj.matrix_world @ b.tail_local) * factor)} for b in obj.data.bones]
        objects.append(record)
    report = {"kind": "rig2print-scene-inventory", "schema_version": 1,
        "source_name": source.name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "blender_version": bpy.app.version_string, "frame": scene.frame_current,
        "scene_unit_system": scene.unit_settings.system, "mm_per_blender_unit": factor,
        "units_require_confirmation": scene.unit_settings.system == "NONE",
        "scope": "active-scene, current frame, viewport-evaluated meshes; not print qualification",
        "limitations": ["bone endpoints are rest-space coordinates transformed into world space",
            "topology edge counts do not test self-intersections or wall thickness",
            "instanced geometry is not expanded", "vertex weights are not exported"],
        "objects": objects}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        json.dump(report, handle, indent=2, allow_nan=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
