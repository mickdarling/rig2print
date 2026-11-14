# Contributing

Start with an issue describing the input, target process, expected motion, and a measurable acceptance test. Use small fixture meshes with explicit licensing. Submit source recipes and reports alongside generated examples.

Run `python3 scripts/check.py --all` before opening a PR. This runs Python syntax, strict JSON parsing, portable Dollhouse bundle checks, CLI smoke check and unit tests, plus Rust formatting, Clippy and locked Cargo tests. CI runs the same commands in language-specific jobs. New files must be added to Git so the tracked-file checks include them. The Python-only command is `python3 scripts/check.py`. Blender-dependent changes also need a documented headless integration run with the exact Blender version.

Open a feature branch and pull request targeting `main`. CI runs on Python 3.11–3.14 and Rust 1.85.0/stable; the aggregate check is `CI passed`. See [CI and PR workflow](docs/ci.md) for coverage and merge-protection setup. Use the PR template to distinguish automated, Blender and physical evidence.

Build shared application logic in Rust. Keep Blender-specific code in Python and preserve the JSON boundary between the languages. Ferris is the branching Rust exemplar; the planned python snake is the simpler chain exemplar. Retire the Python reference checker once its relevant behavior is covered by the Rust core and migration checks.

Report these evidence levels separately: plan checks, geometry checks, slicer review, coupon print, joint print, full-model print. An unrun check stays unknown. A rendered joint is not a verified printed joint.

For a physical test, record printer, nozzle, filament, layer height, slicer and profile versions, orientation, model scale, measured gap, release effort, range of motion, retention, and failures. Include photos or video when possible. Never upload credentials, local logs containing private data, or models without redistribution rights.
