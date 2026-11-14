import copy
import json
from pathlib import Path
import unittest

from rig2print.plan import check_plan
from rig2print.cli import inspection_command, main


def fixture():
    return {"schema_version": 1, "units": "mm", "target_span_mm": 100,
        "source": {"repository": "fixture", "revision": "v1", "path": "original.blend", "license": "MIT"},
        "process": {"type": "FDM", "printer": "test setup", "material": "PLA",
            "slicer_profile": "fixture-v1", "nozzle_mm": 0.4, "layer_height_mm": 0.2,
            "coupon_verified": False},
        "parts": [{"id": "body", "source_objects": ["body"]},
                  {"id": "limb", "source_objects": ["limb"]}],
        "joints": [{"id": "shoulder", "parent": "body", "child": "limb",
            "type": "hinge", "anchor_mm": [0, 0, 5], "axis": [1, 0, 0],
            "motion_degrees": [-30, 30], "clearance_mm": 0.4, "min_wall_mm": 1.2,
            "retention_strategy": "captive headed axle", "print_support_strategy": "bed-contact fixture"}]}


class PlanTests(unittest.TestCase):
    def test_structural_pass_does_not_certify_print(self):
        report = check_plan(fixture())
        self.assertTrue(report["ok"])
        self.assertEqual(report["scope"], "plan-only")
        self.assertTrue(any("physically" in warning for warning in report["warnings"]))

    def test_unknown_and_disconnected_bodies_fail(self):
        p = fixture()
        p["joints"][0]["child"] = "unknown"
        self.assertFalse(check_plan(p)["ok"])
        p = fixture()
        p["parts"].append({"id": "loose", "source_objects": ["loose"]})
        self.assertIn("mechanical part graph must be connected", check_plan(p)["errors"])

    def test_bad_numeric_values_fail(self):
        for value in (0, -0.1, True, float("inf"), float("nan"), "0.4", None):
            with self.subTest(value=value):
                p = fixture()
                p["joints"][0]["clearance_mm"] = value
                self.assertFalse(check_plan(p)["ok"])

    def test_duplicate_ids_and_zero_axis_fail(self):
        p = fixture()
        p["parts"][1]["id"] = "body"
        self.assertFalse(check_plan(p)["ok"])
        p = fixture()
        p["joints"][0]["axis"] = [0, 0, 0]
        self.assertFalse(check_plan(p)["ok"])

    def test_reversed_or_nonfinite_limits_fail(self):
        for limits in ([30, -30], [0, 0], [0, float("inf")], [True, 90]):
            p = fixture()
            p["joints"][0]["motion_degrees"] = limits
            self.assertFalse(check_plan(p)["ok"])

    def test_missing_retention_or_process_fails(self):
        for section, key in (("joint", "retention_strategy"), ("process", "printer")):
            p = copy.deepcopy(fixture())
            del (p["joints"][0] if section == "joint" else p["process"])[key]
            self.assertFalse(check_plan(p)["ok"])

    def test_wrong_units_and_empty_plan_fail(self):
        p = fixture()
        p["units"] = "m"
        self.assertFalse(check_plan(p)["ok"])
        for value in ([], None, {}, "bad"):
            self.assertFalse(check_plan(value)["ok"])

    def test_malformed_nested_values_are_reported(self):
        for field, value in (("parts", [None, {}]), ("joints", [None]), ("process", [])):
            p = fixture()
            p[field] = value
            self.assertFalse(check_plan(p)["ok"])
        p = fixture()
        p["joints"][0]["parent"] = []
        self.assertFalse(check_plan(p)["ok"])

    def test_ferris_draft_remains_rejected(self):
        path = Path(__file__).resolve().parents[1] / "examples/ferris/plan.draft.json"
        report = check_plan(json.loads(path.read_text()))
        self.assertFalse(report["ok"])
        self.assertIn("joints must contain at least one mechanical joint", report["errors"])

    def test_blender_launch_preserves_paths_and_failure_exit(self):
        command = inspection_command("/app path/blender", "/model path/input.blend", "/out path/report.json")
        self.assertEqual(command[0], "/app path/blender")
        self.assertIn("/model path/input.blend", command)
        self.assertLess(command.index("--disable-autoexec"), command.index("/model path/input.blend"))
        self.assertEqual(command[command.index("--python-exit-code") + 1], "1")
        self.assertEqual(command[-1], "/out path/report.json")


if __name__ == "__main__":
    unittest.main()
