"""Run the same repository checks locally and in GitHub Actions."""

import argparse
import ast
from pathlib import Path
import subprocess
import sys

from check_repository import check_json_files


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="also run Rust formatting, Clippy and tests")
    args = parser.parse_args()
    try:
        paths = subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT
        ).decode("utf-8").strip("\0").split("\0")
        python_files = [ROOT / path for path in paths if path.endswith(".py")]
        for path in python_files:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        count = check_json_files(ROOT, paths)
        print(f"Checked {len(python_files)} Python files and {count} JSON files.", flush=True)
        subprocess.run([sys.executable, "-m", "rig2print", "--help"], cwd=ROOT, check=True)
        subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                       cwd=ROOT, check=True)
        if args.all:
            for command in (["cargo", "fmt", "--all", "--", "--check"],
                            ["cargo", "clippy", "--locked", "--all-targets", "--", "-D", "warnings"],
                            ["cargo", "test", "--locked"]):
                subprocess.run(command, cwd=ROOT, check=True)
        return 0
    except (OSError, ValueError, SyntaxError, subprocess.SubprocessError) as exc:
        print(f"Repository checks failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
