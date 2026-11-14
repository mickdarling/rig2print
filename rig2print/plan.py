"""Structural design checks. These checks do not certify geometry or prints."""

import math


def positive(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value > 0)


def vector(value, nonzero=False):
    valid = (isinstance(value, list) and len(value) == 3 and all(
        isinstance(x, (int, float)) and not isinstance(x, bool)
        and math.isfinite(x) for x in value))
    return valid and (not nonzero or any(x != 0 for x in value))


def check_plan(plan):
    """Return deterministic blockers and warnings for a v1 plan dictionary."""
    errors, warnings = [], []
    if not isinstance(plan, dict):
        return {"ok": False, "scope": "plan-only", "errors": ["plan must be an object"], "warnings": []}
    if plan.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if plan.get("units") != "mm":
        errors.append("units must be mm")
    if not positive(plan.get("target_span_mm")):
        errors.append("target_span_mm must be finite and positive")
    source = plan.get("source")
    if not isinstance(source, dict) or not all(
        isinstance(source.get(k), str) and source[k].strip()
        for k in ("repository", "revision", "path", "license")
    ):
        errors.append("source requires repository, revision, path and license")
    process = plan.get("process")
    if not isinstance(process, dict):
        process = {}
    if process.get("type") != "FDM":
        errors.append("v1 plans require an FDM process")
    for name in ("printer", "material", "slicer_profile"):
        if not isinstance(process.get(name), str) or not process[name].strip():
            errors.append(f"process.{name} is required")
    for name in ("nozzle_mm", "layer_height_mm"):
        if not positive(process.get(name)):
            errors.append(f"process.{name} must be finite and positive")
    if process.get("coupon_verified") is not True:
        warnings.append("clearance coupon has not been physically verified")

    parts, joints = plan.get("parts"), plan.get("joints")
    if not isinstance(parts, list) or len(parts) < 2:
        errors.append("parts must contain at least two rigid bodies")
        parts = parts if isinstance(parts, list) else []
    ids = []
    for i, part in enumerate(parts):
        if not isinstance(part, dict) or not isinstance(part.get("id"), str) or not part["id"].strip():
            errors.append(f"parts[{i}] requires a nonempty id")
            continue
        ids.append(part["id"])
        if not isinstance(part.get("source_objects"), list) or not part["source_objects"] or not all(
            isinstance(s, str) and s.strip() for s in part["source_objects"]
        ):
            errors.append(f"part {part['id']} requires source_objects")
    if len(set(ids)) != len(ids):
        errors.append("part ids must be unique")
    if not isinstance(joints, list) or not joints:
        errors.append("joints must contain at least one mechanical joint")
        joints = joints if isinstance(joints, list) else []
    adjacency = {name: set() for name in ids}
    joint_ids = set()
    for i, joint in enumerate(joints):
        if not isinstance(joint, dict):
            errors.append(f"joints[{i}] must be an object")
            continue
        name = joint.get("id")
        if not isinstance(name, str) or not name.strip() or name in joint_ids:
            errors.append(f"joints[{i}] requires a unique nonempty id")
        else:
            joint_ids.add(name)
        kind = joint.get("type")
        if kind not in ("hinge", "ball_socket"):
            errors.append(f"joint {i}: type must be hinge or ball_socket")
        a, b = joint.get("parent"), joint.get("child")
        if not isinstance(a, str) or not isinstance(b, str) or a == b or a not in adjacency or b not in adjacency:
            errors.append(f"joint {i}: parent and child must be different known part ids")
        else:
            adjacency[a].add(b)
            adjacency[b].add(a)
        for key in ("clearance_mm", "min_wall_mm"):
            if not positive(joint.get(key)):
                errors.append(f"joint {i}: {key} must be finite and positive")
        if not vector(joint.get("anchor_mm")):
            errors.append(f"joint {i}: anchor_mm must be a finite 3-vector")
        if kind == "hinge" and not vector(joint.get("axis"), nonzero=True):
            errors.append(f"joint {i}: hinge axis must be a finite nonzero 3-vector")
        limits = joint.get("motion_degrees")
        if not (isinstance(limits, list) and len(limits) == 2 and all(
            isinstance(x, (float, int)) and not isinstance(x, bool) and math.isfinite(x) for x in limits
        ) and limits[0] < limits[1]):
            errors.append(f"joint {i}: motion_degrees must be an increasing finite pair")
        for key in ("retention_strategy", "print_support_strategy"):
            if not isinstance(joint.get(key), str) or not joint[key].strip():
                errors.append(f"joint {i}: {key} is required")
    if adjacency:
        reached, pending = set(), [next(iter(adjacency))]
        while pending:
            part = pending.pop()
            if part not in reached:
                reached.add(part)
                pending.extend(adjacency[part] - reached)
        if reached != set(adjacency):
            errors.append("mechanical part graph must be connected")
    warnings.append("geometry, retention, collision, slicer and physical-print checks are separate")
    return {"ok": not errors, "scope": "plan-only", "errors": errors, "warnings": warnings}
