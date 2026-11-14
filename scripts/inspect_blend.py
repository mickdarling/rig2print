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
                  "parent_type": obj.parent_type, "parent_bone": obj.parent_bone,
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
                groups = {g.index: {"name": g.name, "vertex_count": 0, "weight_sum": 0.0,
                                   "bounds_rest_mm": None} for g in obj.vertex_groups}
                for vertex in obj.data.vertices:
                    point = (obj.matrix_world @ vertex.co) * factor
                    for influence in vertex.groups:
                        if influence.weight <= 0 or influence.group not in groups:
                            continue
                        group = groups[influence.group]
                        group["vertex_count"] += 1
                        group["weight_sum"] += influence.weight
                        bounds = group["bounds_rest_mm"]
                        if bounds is None:
                            group["bounds_rest_mm"] = [list(point), list(point)]
                        else:
                            for axis in range(3):
                                bounds[0][axis] = min(bounds[0][axis], point[axis])
                                bounds[1][axis] = max(bounds[1][axis], point[axis])
                record["weight_groups"] = list(groups.values())
                armature = obj.find_armature()
                record["armature"] = armature.name if armature else None
            finally:
                evaluated.to_mesh_clear()
        if obj.type == "ARMATURE":
            record["pose_position"] = obj.data.pose_position
            record["bones"] = [{"name": b.name,
                "parent": b.parent.name if b.parent else None, "deform": b.use_deform,
                "head_mm": list((obj.matrix_world @ b.head_local) * factor),
                "tail_mm": list((obj.matrix_world @ b.tail_local) * factor),
                "pose_head_mm": list((obj.matrix_world @ obj.pose.bones[b.name].head) * factor),
                "pose_tail_mm": list((obj.matrix_world @ obj.pose.bones[b.name].tail) * factor)
                } for b in obj.data.bones]
        objects.append(record)
    report = {"kind": "rig2print-scene-inventory", "schema_version": 1,
        "source_name": source.name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "blender_version": bpy.app.version_string, "frame": scene.frame_current,
        "scene_unit_system": scene.unit_settings.system, "mm_per_blender_unit": factor,
        "units_require_confirmation": scene.unit_settings.system == "NONE",
        "scope": "active-scene, current frame, viewport-evaluated meshes; not print qualification",
        "limitations": ["bone endpoints are rest-space coordinates transformed into world space",
            "topology edge counts do not test self-intersections or wall thickness",
            "instanced geometry is not expanded", "per-vertex weights are not exported; group summaries only"],
        "objects": objects}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        json.dump(report, handle, indent=2, allow_nan=False)
        handle.write("\n")


if __name__ == "__main__":
    main()
