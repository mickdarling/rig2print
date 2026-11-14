from pathlib import Path
import struct
import tempfile
import unittest

from scripts.check_stl import check_stl


class StlChecks(unittest.TestCase):
    def test_open_triangle_is_not_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "open.stl"
            path.write_bytes(b"fixture".ljust(80, b" ")+struct.pack("<I", 1)
                +struct.pack("<12fH", 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0))
            self.assertEqual(check_stl(path)["nonmanifold_edges"], 3)

    def test_truncated_stl_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "truncated.stl"
            path.write_bytes(b"fixture".ljust(80, b" ")+struct.pack("<I", 1))
            with self.assertRaises(ValueError):
                check_stl(path)
