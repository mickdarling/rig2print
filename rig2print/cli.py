import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from .plan import check_plan


def inspection_command(blender, source, output):
    script = Path(__file__).resolve().parent.parent / "scripts" / "inspect_blend.py"
    return [str(blender), "--background", "--factory-startup", "--disable-autoexec",
            str(source), "--python-exit-code", "1", "--python", str(script),
            "--", "--output", str(output)]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inspect assets and check print-in-place design plans")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check-plan", help="check the plan contract, not geometry")
    check.add_argument("plan", type=Path)
    inspect = commands.add_parser("inspect", help="write a scene inventory using Blender")
    inspect.add_argument("source", type=Path)
    inspect.add_argument("--blender", default="blender")
    inspect.add_argument("--output", type=Path, required=True)
    inspect.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args(argv)
    try:
        if args.command == "check-plan":
            report = check_plan(json.loads(args.plan.read_text()))
            print(json.dumps(report, indent=2, allow_nan=False))
            return 0 if report["ok"] else 1
        source, output = args.source.resolve(), args.output.resolve()
        if not source.is_file() or source.suffix.lower() != ".blend":
            raise ValueError("source must be an existing .blend file")
        if output == source:
            raise ValueError("output cannot overwrite the source")
        if output.exists():
            raise ValueError("output already exists; choose a new report path")
        if output.suffix.lower() != ".json":
            raise ValueError("output must end in .json")
        blender = shutil.which(args.blender)
        if not blender:
            raise ValueError("Blender executable not found; supply --blender /path/to/blender")
        if args.timeout <= 0:
            raise ValueError("timeout must be positive")
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(inspection_command(blender, source, output), check=True, timeout=args.timeout)
        if not output.is_file():
            raise ValueError("Blender exited without producing the requested report")
        report = json.loads(output.read_text())
        if report.get("kind") != "rig2print-scene-inventory":
            raise ValueError("Blender report has an unexpected format")
        print(f"Inventory: {output}")
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"rig2print: {exc}", file=sys.stderr)
        return 2
