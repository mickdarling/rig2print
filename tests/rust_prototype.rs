use std::process::Command;

fn invoke(args: &[&str]) -> std::process::Output {
    Command::new(env!("CARGO_BIN_EXE_rig2print"))
        .args(args)
        .output()
        .unwrap()
}

#[test]
fn prototype_help_does_not_require_blender() {
    let result = invoke(&["prototype-joint", "--help"]);
    assert!(result.status.success());
    assert!(String::from_utf8_lossy(&result.stdout).contains("not full-model"));
}

#[test]
fn incomplete_or_unknown_options_fail_before_launch() {
    for args in [
        vec!["prototype-joint"],
        vec!["prototype-joint", "missing.blend"],
        vec!["prototype-joint", "missing.blend", "--unknown", "value"],
        vec!["prototype-joint", "missing.blend", "--mesh"],
        vec![
            "prototype-joint",
            "missing.blend",
            "--mesh",
            "a",
            "--mesh",
            "b",
        ],
    ] {
        let result = invoke(&args);
        assert_eq!(result.status.code(), Some(2));
        assert!(!String::from_utf8_lossy(&result.stderr).contains("could not run Blender"));
    }
}

#[test]
fn numeric_limits_are_checked_without_blender() {
    for value in ["NaN", "inf", "-1", "0", "not-a-number"] {
        let result = invoke(&[
            "prototype-joint",
            "missing.blend",
            "--mesh",
            "mesh",
            "--armature",
            "rig",
            "--parent-bone",
            "upper",
            "--child-bone",
            "lower",
            "--span-mm",
            value,
            "--output-dir",
            "not-created",
        ]);
        assert_eq!(result.status.code(), Some(2));
        assert!(String::from_utf8_lossy(&result.stderr).contains("--span-mm"));
    }
}
