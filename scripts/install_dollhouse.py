"""Copy native Markdown elements into a chosen Dollhouse portfolio; never overwrite."""

import argparse
from pathlib import Path
import sys

try:
    from .check_repository import read_element, validate_elements
except ImportError:
    from check_repository import read_element, validate_elements


SOURCE = Path(__file__).resolve().parents[1] / "dollhouse/portfolio"


def install(portfolio, apply=False):
    portfolio = Path(portfolio).expanduser().resolve()
    if not portfolio.is_dir():
        raise ValueError("portfolio must be an existing directory on the Dollhouse server host")
    files = sorted(SOURCE.rglob("*.md"))
    documents = {str(path.relative_to(SOURCE)): read_element(path) for path in files}
    if not files:
        raise ValueError("bundled elements are missing")
    validate_elements(documents)
    targets = [(path, portfolio / path.relative_to(SOURCE)) for path in files]
    collisions = [str(target) for _, target in targets if target.exists() or target.is_symlink()]
    if collisions:
        raise ValueError("refusing to overwrite existing elements: " + ", ".join(collisions))
    for source, target in targets:
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation also protects a file created after preflight.
            with target.open("xb") as handle:
                handle.write(source.read_bytes())
        print(("Installed " if apply else "Would install ") + str(target))
    return len(targets)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("portfolio", type=Path, help="actual configured portfolio directory")
    parser.add_argument("--apply", action="store_true", help="copy files; default only previews")
    args = parser.parse_args()
    try:
        count = install(args.portfolio, args.apply)
    except (OSError, ValueError) as error:
        print(f"Installation stopped: {error}", file=sys.stderr)
        return 1
    print(f"{count} elements. Validate and activate them through Dollhouse after installation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
