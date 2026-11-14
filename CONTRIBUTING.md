# Contributing

Start with an issue describing the input, target process, expected motion, and a measurable acceptance test. Use small fixture meshes with explicit licensing. Submit source recipes and reports alongside generated examples.

Run `python3 -m unittest discover -s tests -v`. The initial tools use only the Python standard library. Blender-dependent changes also need a documented headless integration run with the exact Blender version.

Report these evidence levels separately: plan checks, geometry checks, slicer review, coupon print, joint print, full-model print. An unrun check stays unknown. A rendered joint is not a verified printed joint.

For a physical test, record printer, nozzle, filament, layer height, slicer and profile versions, orientation, model scale, measured gap, release effort, range of motion, retention, and failures. Include photos or video when possible. Never upload credentials, local logs containing private data, or models without redistribution rights.
