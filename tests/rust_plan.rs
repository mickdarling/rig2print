use rig2print::check_plan;
use serde_json::{json, Value};
use std::process::Command;

fn fixture() -> Value {
    json!({"schema_version": 1, "units": "mm", "target_span_mm": 100,
        "source": {"repository": "original-fixture", "revision": "v1", "path": "fixture.blend", "license": "MIT"},
        "process": {"type": "FDM", "printer": "test setup", "material": "PLA", "slicer_profile": "fixture-v1",
            "nozzle_mm": 0.4, "layer_height_mm": 0.2, "coupon_verified": false},
        "parts": [{"id": "body", "source_objects": ["body"]}, {"id": "limb", "source_objects": ["limb"]}],
        "joints": [{"id": "shoulder", "type": "hinge", "parent": "body", "child": "limb",
            "anchor_mm": [0, 0, 5], "axis": [1, 0, 0], "motion_degrees": [-30, 30],
            "clearance_mm": 0.4, "min_wall_mm": 1.2, "retention_strategy": "captive axle",
            "print_support_strategy": "bed-contact fixture"}]})
}

#[test]
fn contract_pass_is_not_print_qualification() {
    let report = check_plan(&fixture());
    assert_eq!(report["ok"], true);
    assert_eq!(report["scope"], "plan-only");
    assert!(!report["warnings"].as_array().unwrap().is_empty());
}

#[test]
fn unknown_or_disconnected_bodies_fail() {
    let mut plan = fixture();
    plan["joints"][0]["child"] = json!("unknown");
    assert_eq!(check_plan(&plan)["ok"], false);
    let mut plan = fixture();
    plan["parts"]
        .as_array_mut()
        .unwrap()
        .push(json!({"id": "loose", "source_objects": ["loose"]}));
    assert_eq!(check_plan(&plan)["ok"], false);
}

#[test]
fn connected_branching_mechanism_passes_contract() {
    let mut plan = fixture();
    plan["parts"]
        .as_array_mut()
        .unwrap()
        .push(json!({"id": "other-limb", "source_objects": ["other-limb"]}));
    let mut joint = plan["joints"][0].clone();
    joint["id"] = json!("other-shoulder");
    joint["child"] = json!("other-limb");
    plan["joints"].as_array_mut().unwrap().push(joint);
    assert_eq!(check_plan(&plan)["ok"], true);
}

#[test]
fn invalid_units_clearances_axes_and_limits_fail() {
    for value in [
        json!(0),
        json!(-0.1),
        json!(true),
        json!("0.4"),
        Value::Null,
    ] {
        let mut plan = fixture();
        plan["joints"][0]["clearance_mm"] = value;
        assert_eq!(check_plan(&plan)["ok"], false);
    }
    let mut plan = fixture();
    plan["units"] = json!("m");
    assert_eq!(check_plan(&plan)["ok"], false);
    let mut plan = fixture();
    plan["joints"][0]["axis"] = json!([0, 0, 0]);
    assert_eq!(check_plan(&plan)["ok"], false);
    let mut plan = fixture();
    plan["joints"][0]["motion_degrees"] = json!([30, -30]);
    assert_eq!(check_plan(&plan)["ok"], false);
}

#[test]
fn missing_retention_and_duplicate_ids_fail() {
    let mut plan = fixture();
    plan["joints"][0]
        .as_object_mut()
        .unwrap()
        .remove("retention_strategy");
    assert_eq!(check_plan(&plan)["ok"], false);
    let mut plan = fixture();
    plan["parts"][1]["id"] = json!("body");
    assert_eq!(check_plan(&plan)["ok"], false);
}

#[test]
fn malformed_shapes_report_errors_without_panicking() {
    for plan in [
        Value::Null,
        json!([]),
        json!({}),
        json!({"parts": [null, {}], "joints": [null]}),
    ] {
        assert_eq!(check_plan(&plan)["ok"], false);
    }
}

#[test]
fn ferris_draft_stays_rejected() {
    let plan = serde_json::from_str(include_str!("../examples/ferris/plan.draft.json")).unwrap();
    assert_eq!(check_plan(&plan)["ok"], false);
}

#[test]
fn cli_returns_documented_exit_codes() {
    let binary = env!("CARGO_BIN_EXE_rig2print");
    assert!(Command::new(binary)
        .arg("--help")
        .output()
        .unwrap()
        .status
        .success());
    let draft = Command::new(binary)
        .args(["check-plan", "examples/ferris/plan.draft.json"])
        .output()
        .unwrap();
    assert_eq!(draft.status.code(), Some(1));
    let report: Value = serde_json::from_slice(&draft.stdout).unwrap();
    assert_eq!(report["scope"], "plan-only");
    assert_eq!(
        Command::new(binary)
            .arg("unknown-command")
            .output()
            .unwrap()
            .status
            .code(),
        Some(2)
    );
}
