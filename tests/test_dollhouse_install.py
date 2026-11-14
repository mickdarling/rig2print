import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from scripts.install_dollhouse import install, SOURCE


class DollhouseInstallTests(unittest.TestCase):
    def test_preview_does_not_write_and_apply_copies_exact_files(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            target = Path(directory)
            self.assertEqual(install(target), 10)
            self.assertEqual(list(target.iterdir()), [])
            self.assertEqual(install(target, apply=True), 10)
            for source in SOURCE.rglob("*.md"):
                self.assertEqual((target / source.relative_to(SOURCE)).read_bytes(), source.read_bytes())

    def test_collision_aborts_before_any_file_is_copied(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            existing = target / "templates/pip-conversion-review.md"
            existing.parent.mkdir()
            existing.write_text("existing user element")
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                install(target, apply=True)
            self.assertEqual(existing.read_text(), "existing user element")
            self.assertEqual(list(target.rglob("*.md")), [existing])
