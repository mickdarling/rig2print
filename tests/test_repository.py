import copy
from pathlib import Path
import tempfile
import unittest

from scripts.check_repository import read_element, strict_json, validate_elements


ROOT = Path(__file__).resolve().parents[1]


class RepositoryDataTests(unittest.TestCase):
    def setUp(self):
        self.elements = {str(path.relative_to(ROOT)): read_element(path)
                         for path in (ROOT / "dollhouse/portfolio").rglob("*.md")}

    def test_native_portfolio_is_complete(self):
        self.assertEqual(len(self.elements), 10)
        validate_elements(self.elements)
        self.assertFalse((ROOT / "dollhouse/bundle.json").exists())

    def test_duplicate_keys_and_nonfinite_constants_fail(self):
        for text in ('{"name": 1, "name": 2}', '{"value": NaN}', '{"value": Infinity}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                strict_json(text)

    def test_duplicate_yaml_keys_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.md"
            path.write_text("---\nname: first\nname: second\n---\nBody")
            with self.assertRaisesRegex(ValueError, "duplicate YAML key"):
                read_element(path)

    def test_missing_frontmatter_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "not-an-element.md"
            path.write_text("# Name list only")
            with self.assertRaisesRegex(ValueError, "frontmatter"):
                read_element(path)

    def test_missing_member_fails(self):
        del self.elements["dollhouse/portfolio/skills/pip-design-intent.md"]
        with self.assertRaisesRegex(ValueError, "unresolved ensemble member"):
            validate_elements(self.elements)

    def test_filename_and_type_must_match(self):
        metadata, _ = self.elements["dollhouse/portfolio/skills/pip-design-intent.md"]
        metadata["type"] = "memory"
        with self.assertRaisesRegex(ValueError, "type must match"):
            validate_elements(self.elements)

    def test_undeclared_template_variable_fails(self):
        path = "dollhouse/portfolio/templates/pip-conversion-review.md"
        metadata, body = self.elements[path]
        self.elements[path] = metadata, body+"\n{{undeclared}}"
        with self.assertRaisesRegex(ValueError, "variables must match"):
            validate_elements(self.elements)

    def test_duplicate_member_and_invalid_role_fail(self):
        for mode in ("duplicate", "bad-role"):
            with self.subTest(mode=mode):
                elements = copy.deepcopy(self.elements)
                metadata, _ = elements["dollhouse/portfolio/ensembles/print-in-place-conversion-team.md"]
                if mode == "duplicate":
                    metadata["elements"].append(copy.deepcopy(metadata["elements"][0]))
                else:
                    metadata["elements"][0]["role"] = "unknown"
                with self.assertRaises(ValueError):
                    validate_elements(elements)

    def test_api_wrapper_is_not_native_ensemble(self):
        metadata, _ = self.elements["dollhouse/portfolio/ensembles/print-in-place-conversion-team.md"]
        metadata["metadata"] = {"elements": metadata.pop("elements")}
        with self.assertRaisesRegex(ValueError, "native top-level elements"):
            validate_elements(self.elements)


if __name__ == "__main__":
    unittest.main()
