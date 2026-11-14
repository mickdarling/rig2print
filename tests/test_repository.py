import copy
import json
from pathlib import Path
import unittest

from scripts.check_repository import strict_json, validate_bundle


ROOT = Path(__file__).resolve().parents[1]


class RepositoryDataTests(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads((ROOT / "dollhouse/bundle.json").read_text())

    def test_current_portable_bundle_is_consistent(self):
        validate_bundle(self.bundle)

    def test_duplicate_keys_and_nonfinite_constants_fail(self):
        for text in ('{"name": 1, "name": 2}', '{"value": NaN}', '{"value": Infinity}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                strict_json(text)

    def test_unresolved_or_out_of_order_members_fail(self):
        self.bundle["operations"].reverse()
        with self.assertRaisesRegex(ValueError, "unresolved or out-of-order"):
            validate_bundle(self.bundle)

    def test_overwriting_an_existing_dependency_fails(self):
        self.bundle["requires"].append({"element_type": "persona", "element_name": "pip-mechanical-designer"})
        with self.assertRaisesRegex(ValueError, "dependency-overwriting"):
            validate_bundle(self.bundle)

    def test_undeclared_template_variable_fails(self):
        template = next(op for op in self.bundle["operations"] if op["element_type"] == "template")
        template["params"]["content"] += "\n{{undeclared}}"
        with self.assertRaisesRegex(ValueError, "variables must match"):
            validate_bundle(self.bundle)

    def test_duplicate_member_and_invalid_role_fail(self):
        for mode in ("duplicate", "bad-role"):
            with self.subTest(mode=mode):
                bundle = copy.deepcopy(self.bundle)
                members = bundle["operations"][-1]["params"]["metadata"]["elements"]
                if mode == "duplicate":
                    members.append(copy.deepcopy(members[0]))
                else:
                    members[0]["role"] = "unknown"
                with self.assertRaises(ValueError):
                    validate_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
