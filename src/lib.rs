//! Mechanical-plan contract checks. A pass does not qualify geometry or a print.

use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};

fn positive(value: &Value) -> bool {
    value.as_f64().is_some_and(|v| v.is_finite() && v > 0.0)
}

fn text(value: &Value) -> bool {
    value.as_str().is_some_and(|v| !v.trim().is_empty())
}

fn vector(value: &Value, nonzero: bool) -> bool {
    let Some(values) = value.as_array() else {
        return false;
    };
    values.len() == 3
        && values
            .iter()
            .all(|v| v.as_f64().is_some_and(|x| x.is_finite()))
        && (!nonzero || values.iter().any(|v| v.as_f64() != Some(0.0)))
}

pub fn check_plan(plan: &Value) -> Value {
    let mut errors: Vec<String> = Vec::new();
    let mut warnings: Vec<String> = Vec::new();
    if !plan.is_object() {
        return json!({"ok": false, "scope": "plan-only",
            "errors": ["plan must be an object"], "warnings": []});
    }
    if plan["schema_version"].as_u64() != Some(1) {
        errors.push("schema_version must be 1".into());
    }
    if plan["units"] != "mm" {
        errors.push("units must be mm".into());
    }
    if !positive(&plan["target_span_mm"]) {
        errors.push("target_span_mm must be finite and positive".into());
    }
    if !["repository", "revision", "path", "license"]
        .iter()
        .all(|key| text(&plan["source"][key]))
    {
        errors.push("source requires repository, revision, path and license".into());
    }
    let process = &plan["process"];
    if process["type"] != "FDM" {
        errors.push("v1 plans require an FDM process".into());
    }
    for key in ["printer", "material", "slicer_profile"] {
        if !text(&process[key]) {
            errors.push(format!("process.{key} is required"));
        }
    }
    for key in ["nozzle_mm", "layer_height_mm"] {
        if !positive(&process[key]) {
            errors.push(format!("process.{key} must be finite and positive"));
        }
    }
    if process["coupon_verified"] != true {
        warnings.push("clearance coupon has not been physically verified".into());
    }

    let empty = Vec::new();
    let parts = plan["parts"].as_array().unwrap_or(&empty);
    if parts.len() < 2 {
        errors.push("parts must contain at least two rigid bodies".into());
    }
    let mut graph: BTreeMap<&str, BTreeSet<&str>> = BTreeMap::new();
    for (i, part) in parts.iter().enumerate() {
        if !text(&part["id"]) {
            errors.push(format!("parts[{i}] requires a nonempty id"));
            continue;
        }
        let name = part["id"].as_str().unwrap();
        if graph.insert(name, BTreeSet::new()).is_some() {
            errors.push("part ids must be unique".into());
        }
        if !part["source_objects"]
            .as_array()
            .is_some_and(|objects| !objects.is_empty() && objects.iter().all(text))
        {
            errors.push(format!("part {name} requires source_objects"));
        }
    }
    let joints = plan["joints"].as_array().unwrap_or(&empty);
    if joints.is_empty() {
        errors.push("joints must contain at least one mechanical joint".into());
    }
    let mut joint_ids = BTreeSet::new();
    for (i, joint) in joints.iter().enumerate() {
        if !joint.is_object() {
            errors.push(format!("joints[{i}] must be an object"));
            continue;
        }
        if !text(&joint["id"]) || !joint_ids.insert(joint["id"].as_str().unwrap_or("")) {
            errors.push(format!("joints[{i}] requires a unique nonempty id"));
        }
        let kind = joint["type"].as_str().unwrap_or("");
        if !matches!(kind, "hinge" | "ball_socket") {
            errors.push(format!("joint {i}: type must be hinge or ball_socket"));
        }
        match (joint["parent"].as_str(), joint["child"].as_str()) {
            (Some(a), Some(b)) if a != b && graph.contains_key(a) && graph.contains_key(b) => {
                graph.get_mut(a).unwrap().insert(b);
                graph.get_mut(b).unwrap().insert(a);
            }
            _ => errors.push(format!(
                "joint {i}: parent and child must be different known part ids"
            )),
        }
        for key in ["clearance_mm", "min_wall_mm"] {
            if !positive(&joint[key]) {
                errors.push(format!("joint {i}: {key} must be finite and positive"));
            }
        }
        if !vector(&joint["anchor_mm"], false) {
            errors.push(format!("joint {i}: anchor_mm must be a finite 3-vector"));
        }
        if kind == "hinge" && !vector(&joint["axis"], true) {
            errors.push(format!(
                "joint {i}: hinge axis must be a finite nonzero 3-vector"
            ));
        }
        let limits_valid = joint["motion_degrees"].as_array().is_some_and(|limits| {
            limits.len() == 2
                && limits
                    .iter()
                    .all(|v| v.as_f64().is_some_and(|x| x.is_finite()))
                && limits[0].as_f64() < limits[1].as_f64()
        });
        if !limits_valid {
            errors.push(format!(
                "joint {i}: motion_degrees must be an increasing finite pair"
            ));
        }
        for key in ["retention_strategy", "print_support_strategy"] {
            if !text(&joint[key]) {
                errors.push(format!("joint {i}: {key} is required"));
            }
        }
    }
    if let Some(first) = graph.keys().next() {
        let mut reached = BTreeSet::new();
        let mut pending = vec![*first];
        while let Some(part) = pending.pop() {
            if reached.insert(part) {
                pending.extend(graph[part].iter().copied());
            }
        }
        if reached.len() != graph.len() {
            errors.push("mechanical part graph must be connected".into());
        }
    }
    warnings.push(
        "geometry, retention, collision, slicer and physical-print checks are separate".into(),
    );
    json!({"ok": errors.is_empty(), "scope": "plan-only", "errors": errors, "warnings": warnings})
}
