"""Fetch and inspect the pinned CC0 rig in an ephemeral CI checkout."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.request


ROOT = Path(__file__).resolve().parents[1]


def main():
    metadata = json.loads((ROOT / "examples/ferris/source.json").read_text())
    output = ROOT / "build/ferris"
    output.mkdir(parents=True, exist_ok=True)
    source = output / "source.blend"
    url = (metadata["repository"].replace("https://github.com/", "https://raw.githubusercontent.com/")
           + "/" + metadata["revision"] + "/" + metadata["path"])
    with urllib.request.urlopen(url, timeout=60) as response:
        content = response.read()
    digest = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
    if digest != metadata["git_blob_sha1"]:
        raise ValueError("downloaded Ferris asset does not match pinned Git blob")
    source.write_bytes(content)
    report = output / "inventory.json"
    subprocess.run(["blender", "--background", "--factory-startup", "--disable-autoexec", str(source),
                    "--python-exit-code", "1", "--python", str(ROOT / "scripts/inspect_blend.py"),
                    "--", "--output", str(report)], check=True, timeout=180)
    inventory = json.loads(report.read_text())
    assert inventory["source_sha256"] == hashlib.sha256(content).hexdigest()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == inventory["source_sha256"]
    assert any(o["type"] == "ARMATURE" for o in inventory["objects"]), "Ferris has no armature"
    print("FERRIS_RIG_INVENTORY_BEGIN", flush=True)
    print(json.dumps(inventory, indent=2), flush=True)
    print("FERRIS_RIG_INVENTORY_END", flush=True)


if __name__ == "__main__":
    main()
