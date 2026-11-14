"""Blender adapter: derive a two-body captive-hinge candidate from an existing rig.

This experimental command exports geometry evidence, never a print qualification.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def mesh_object(name, vertices, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    normalize(obj)
    return obj


def normalize(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def boolean(obj, cutter, operation):
    activate(obj)
    modifier = obj.modifiers.new("mechanical-CSG", "BOOLEAN")
    modifier.operation = operation
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    normalize(obj)


def cylinder(name, radius, z0, z1, radius_top=None):
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=radius,
        radius2=radius if radius_top is None else radius_top,
        depth=z1-z0, location=(0, 0, (z0+z1)/2))
    obj = bpy.context.object
    obj.name = name
    return obj


def box(name, center, dimensions, angle=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    obj.rotation_euler.z = angle
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    # Bake translation so every final body uses the same millimetre coordinates.
    obj.data.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    return obj


def bake_primitive(obj):
    obj.data.transform(obj.matrix_world)
    obj.matrix_world = Matrix.Identity(4)
    return obj


def bridge(name, direction, start, end, width, height):
    center = direction * ((start+end)/2)
    center.z = height/2
    return box(name, center, (end-start, width, height), math.atan2(direction.y, direction.x))


def ring(outer, neck, cavity, base, gap, height):
    profile = [(outer, 0), (outer, height), (neck, height),
               (neck, base+gap+cavity-neck), (cavity, base+gap), (cavity, 0)]
    vertices = [(r*math.cos(2*math.pi*i/64), r*math.sin(2*math.pi*i/64), z)
                for r, z in profile for i in range(64)]
    faces = []
    for j in range(len(profile)):
        for i in range(64):
            faces.append((j*64+i, j*64+(i+1)%64,
                          ((j+1)%len(profile))*64+(i+1)%64,
                          ((j+1)%len(profile))*64+i))
    return mesh_object("socket", vertices, faces)


def split(source, point, normal, gap):
    parts, boundaries = [], []
    for name, sign in (("parent", -1), ("child", 1)):
        bm = bmesh.new()
        bm.from_mesh(source.data)
        bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
            dist=0.000001, plane_co=point+normal*(gap/2)*sign, plane_no=normal,
            clear_outer=sign == -1, clear_inner=sign == 1)
        edges = [edge for edge in bm.edges if edge.is_boundary]
        boundaries.extend(v.co.copy() for edge in edges for v in edge.verts)
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        parts.append(obj)
    if not boundaries:
        raise ValueError("bone-derived plane did not cut the source mesh")
    return parts, max(math.hypot(p.x, p.y) for p in boundaries)


def health(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    remaining = set(bm.verts)
    components = 0
    while remaining:
        components += 1
        pending = [remaining.pop()]
        while pending:
            for edge in pending.pop().link_edges:
                for vertex in edge.verts:
                    if vertex in remaining:
                        remaining.remove(vertex)
                        pending.append(vertex)
    result = {"vertices": len(bm.verts), "faces": len(bm.faces),
              "nonmanifold_edges": sum(not e.is_manifold for e in bm.edges),
              "components": components, "volume_mm3": abs(bm.calc_volume(signed=True))}
    bm.free()
    return result


def duplicate(obj, name):
    copy = bpy.data.objects.new(name, obj.data.copy())
    bpy.context.collection.objects.link(copy)
    return copy


def intersect_volume(a, b, angle):
    left, right = duplicate(a, "collision-a"), duplicate(b, "collision-b")
    right.data.transform(Matrix.Rotation(math.radians(angle), 4, "Z"))
    boolean(left, right, "INTERSECT")
    volume = health(left)["volume_mm3"]
    bpy.data.objects.remove(left, do_unlink=True)
    return volume


def triangulate_closed(bm):
    bmesh.ops.triangulate(bm, faces=list(bm.faces), ngon_method="EAR_CLIP")
    # Blender can drop collinear n-gon corners during tessellation. Repair only
    # resulting T-junctions: split a triangle's long boundary edge at existing
    # boundary vertices, without moving vertices or filling arbitrary holes.
    for _ in range(100):
        boundary = [e for e in bm.edges if e.is_boundary]
        points = {v for e in boundary for v in e.verts}
        repaired = False
        for edge in boundary:
            face = edge.link_faces[0]
            loop = next(loop for loop in face.loops if loop.edge == edge)
            a, b = loop.vert, loop.link_loop_next.vert
            c = loop.link_loop_prev.vert
            direction = b.co-a.co
            length2 = direction.length_squared
            if length2 < 1e-12:
                continue
            middle = []
            for vertex in points-{a, b, c}:
                t = (vertex.co-a.co).dot(direction)/length2
                if 1e-6 < t < 1-1e-6 and (vertex.co-(a.co+t*direction)).length < 1e-5:
                    middle.append((t, vertex))
            if not middle:
                continue
            chain = [a]+[v for _, v in sorted(middle, key=lambda p: p[0])]+[b]
            bm.faces.remove(face)
            for left, right in zip(chain, chain[1:]):
                bm.faces.new((left, right, c))
            if not edge.link_faces:
                bm.edges.remove(edge)
            repaired = True
            break
        if not repaired:
            break
    # Wire edges left by the tessellator have no surface to export.
    for edge in list(bm.edges):
        if edge.is_wire:
            bm.edges.remove(edge)
    if any(not edge.is_manifold for edge in bm.edges):
        raise ValueError("surface is not closed after triangulation/T-junction repair")


def export_stl(path, objects):
    triangles = []
    for obj in objects:
        # Boolean n-gons can have collinear boundary vertices. Loop-triangle
        # tessellation may omit those vertices and leave T-junctions in STL.
        # Triangulate a copy explicitly so the source body's edges survive.
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        try:
            triangulate_closed(bm)
        except ValueError as error:
            bm.free()
            raise ValueError(f"{obj.name}: {error}") from error
        for triangle in bm.faces:
            points = [obj.matrix_world @ v.co for v in triangle.verts]
            normal = (points[1]-points[0]).cross(points[2]-points[0]).normalized()
            triangles.append(struct.pack("<12fH", *normal, *(v for p in points for v in p), 0))
        bm.free()
    with path.open("xb") as handle:
        handle.write(b"Rig2Print mm Z-up UNPRINTED candidate".ljust(80, b" "))
        handle.write(struct.pack("<I", len(triangles)))
        handle.writelines(triangles)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", required=True)
    parser.add_argument("--armature", required=True)
    parser.add_argument("--parent-bone", required=True)
    parser.add_argument("--child-bone", required=True)
    parser.add_argument("--span-mm", type=float, required=True)
    parser.add_argument("--clearance-mm", type=float, default=0.4)
    parser.add_argument("--wall-mm", type=float, default=1.2)
    parser.add_argument("--pin-radius-mm", type=float, default=2.0)
    parser.add_argument("--motion-deg", type=float, default=10.0)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    for key in ("span_mm", "clearance_mm", "wall_mm", "pin_radius_mm", "motion_deg"):
        if not math.isfinite(getattr(args, key)) or getattr(args, key) <= 0:
            raise ValueError(f"{key} must be finite and positive")
    if args.motion_deg > 15:
        raise ValueError("prototype hinge supports a requested sweep of at most +/-15 degrees")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("output directory must be empty")
    source_path = Path(bpy.data.filepath).resolve()
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    obj = bpy.data.objects.get(args.mesh)
    rig = bpy.data.objects.get(args.armature)
    if obj is None or obj.type != "MESH" or rig is None or rig.type != "ARMATURE":
        raise ValueError("requested source mesh or armature is missing")
    if obj.find_armature() != rig:
        raise ValueError("source mesh is not bound to the requested armature")
    parent, child = rig.pose.bones.get(args.parent_bone), rig.pose.bones.get(args.child_bone)
    if parent is None or child is None or child.parent != parent:
        raise ValueError("requested bones must be an existing parent-child pair")
    for name in (parent.name, child.name):
        group = obj.vertex_groups.get(name)
        if group is None or not any(any(g.group == group.index and g.weight > 0 for g in v.groups)
                                    for v in obj.data.vertices):
            raise ValueError(f"source mesh has no skin influence for {name}")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    world_points = []
    for mesh_obj in bpy.context.scene.objects:
        if mesh_obj.type == "MESH":
            evaluated = mesh_obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            world_points.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
            evaluated.to_mesh_clear()
    span = max(max(p[i] for p in world_points)-min(p[i] for p in world_points) for i in range(3))
    if span <= 0:
        raise ValueError("source scene has zero physical span")
    scale = args.span_mm/span
    pivot = rig.matrix_world @ child.head
    parent_direction = (rig.matrix_world @ parent.head)-pivot
    child_direction = (rig.matrix_world @ child.tail)-pivot
    x = parent_direction.normalized()
    z = (-parent_direction).cross(child_direction).normalized()
    if z.length < 0.99:
        raise ValueError("straight/degenerate bone pair needs an explicit hinge-axis policy")
    y = z.cross(x).normalized()
    transform = Matrix((x, y, z))
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    vertices = [transform @ ((evaluated.matrix_world @ v.co)-pivot)*scale for v in mesh.vertices]
    faces = [tuple(poly.vertices) for poly in mesh.polygons]
    evaluated.to_mesh_clear()
    floor = min(v.z for v in vertices)
    for vertex in vertices:
        vertex.z -= floor
    split_normal = transform @ ((-parent_direction).normalized()+child_direction.normalized()).normalized()
    print_pivot = Vector((0, 0, -floor))
    # Work on evaluated geometry only. The original rig/file is never saved over.
    for existing in list(bpy.data.objects):
        bpy.data.objects.remove(existing, do_unlink=True)
    source = mesh_object("source-leg", vertices, faces)
    export_stl(output / "source-limb.stl", [source])
    parts, boundary_radius = split(source, print_pivot, split_normal, args.clearance_mm)
    bpy.data.objects.remove(source, do_unlink=True)
    parent_body, child_body = parts
    gap, wall, pin = args.clearance_mm, args.wall_mm, args.pin_radius_mm
    keeper = pin+wall
    neck, cavity = pin+gap, keeper+gap
    outer = cavity+wall
    base, height = 2*wall, max(8.0, 6*wall+gap)
    keepout = max(outer+gap, boundary_radius+gap)
    extent_z = max(v.z for v in vertices)+height+wall
    for part in parts:
        cutter = bake_primitive(cylinder("joint-keepout", keepout, -wall, extent_z))
        boolean(part, cutter, "DIFFERENCE")
    male = bake_primitive(cylinder("keeper-bottom", keeper, 0, base))
    boolean(male, bake_primitive(cylinder("pin", pin, base-0.05, height+gap+0.05)), "UNION")
    boolean(male, bake_primitive(cylinder("keeper-ramp", pin, height+gap, height+gap+wall, keeper)), "UNION")
    boolean(male, bake_primitive(cylinder("keeper-top", keeper, height+gap+wall-0.05, height+gap+2*wall)), "UNION")
    boolean(male, bridge("parent-stem", Vector((1, 0, 0)), 0, keepout+2*wall, 2*wall, height), "UNION")
    boolean(parent_body, male, "UNION")
    female = ring(outer, neck, cavity, base, gap, height)
    direction = transform @ child_direction
    direction.z = 0
    direction.normalize()
    boolean(female, bridge("child-stem", direction, outer-wall/2, keepout+2*wall, 2*wall, height), "UNION")
    slot_width = 2*(keeper-gap)
    if slot_width <= 2*wall+2*gap or slot_width >= 2*keeper:
        raise ValueError("chosen clearance/wall/pin dimensions cannot retain this hinge")
    slot = box("stem-slot", (keepout, 0, height/2), (2*keepout, slot_width, 4*height))
    boolean(female, slot, "DIFFERENCE")
    boolean(child_body, female, "UNION")
    checks = {part.name: health(part) for part in parts}
    angles = [-args.motion_deg, -args.motion_deg/2, 0, args.motion_deg/2, args.motion_deg]
    motion = [{"angle_degrees": angle, "intersection_mm3": intersect_volume(parent_body, child_body, angle)}
              for angle in angles]
    ok = (all(h["components"] == 1 and h["nonmanifold_edges"] == 0 and h["volume_mm3"] > 0 for h in checks.values())
          and all(m["intersection_mm3"] < 0.001 for m in motion))
    report = {"kind": "rig2print-joint-prototype", "geometry_pass": ok,
        "source_sha256": source_hash, "source_mesh": args.mesh, "armature": args.armature,
        "parent_bone": args.parent_bone, "child_bone": args.child_bone,
        "blender_version": bpy.app.version_string, "target_model_span_mm": args.span_mm,
        "source_world_units_to_mm": scale, "source_pivot": list(pivot),
        "print_frame_axes": [list(x), list(y), list(z)], "source_floor_offset_mm": -floor,
        "clearance_mm": gap, "wall_mm": wall, "keepout_radius_mm": keepout,
        "pin_radius_mm": pin, "keeper_radius_mm": keeper, "slot_width_mm": slot_width,
        "body_checks": checks, "sampled_motion": motion,
        "review_required": keepout > 2*outer,
        "review_notes": (["bone-derived cut needs a large removal region; inspect shape loss and improve joint placement"]
                         if keepout > 2*outer else []),
        "limitations": ["experimental two-body specimen, not full-model conversion",
            "bone-derived bisector cut; skin weights verify binding but do not optimize segmentation",
            "five sampled poses do not prove continuous collision freedom",
            "no self-intersection, wall-thickness or slicer certification",
            "keeper and slot dimensions express capture intent, not a retention proof",
            "source posed limb is reoriented as a whole for the specimen",
            "physical printing, joint release and strength remain unverified"]}
    (output / "report.json").write_text(json.dumps(report, indent=2)+"\n")
    if hashlib.sha256(source_path.read_bytes()).hexdigest() != source_hash:
        raise ValueError("source asset changed during conversion")
    print("JOINT_PROTOTYPE_REPORT "+json.dumps(report), flush=True)
    if not ok:
        raise ValueError("prototype failed geometry or sampled collision checks; see report.json")
    export_stl(output / "prototype.stl", parts)
    for part in parts:
        export_stl(output / (part.name+".stl"), [part])
        part["source_bone"] = args.parent_bone if part == parent_body else args.child_bone
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 0.001
    # Render the exported bodies, not hidden cutters or the original unmodified rig.
    for part, color in zip(parts, ((0.08, 0.35, 0.7, 1), (0.9, 0.3, 0.05, 1))):
        material = bpy.data.materials.new(part.name)
        material.diffuse_color = color
        part.data.materials.append(material)
    points = [v.co for part in parts for v in part.data.vertices]
    center = sum(points, Vector())/len(points)
    span = max(max(p[i] for p in points)-min(p[i] for p in points) for i in range(3))
    bpy.ops.object.camera_add(location=center+Vector((span, -span, span)))
    camera = bpy.context.object
    camera.rotation_euler = (center-camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = span*1.5
    camera.data.clip_end = span*10
    scene = bpy.context.scene
    scene.camera = camera
    bpy.ops.object.light_add(type="SUN", rotation=(0.4, -0.5, -0.4))
    bpy.context.object.data.energy = 3
    scene.world.color = (0.4, 0.4, 0.4)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.resolution_x, scene.render.resolution_y = 640, 480
    scene.render.resolution_percentage = 100
    # The source asset may be configured for an animation/video export.
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.use_compositing = False
    scene.render.use_sequencer = False
    scene.render.filepath = str(output / "preview.png")
    bpy.ops.render.render(write_still=True)
    report["output_sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in output.glob("*.stl")}
    (output / "report.json").write_text(json.dumps(report, indent=2)+"\n")
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "prototype.blend"))


if __name__ == "__main__":
    main()
