# Rig-derived knee specimen

This is the first executable conversion experiment on the supplied pre-rigged Ferris model. It converts one weighted knee into a two-body headed-pin/C-socket candidate. It does not convert the whole character.

With Rust and Blender installed, obtain the pinned source as described in README.md, then run:

```sh
cargo run --locked -- prototype-joint assets/ferris3d/blend/ferris3d_v1.0.blend \
  --mesh leg1L --armature Armature \
  --parent-bone UpperLeg1.L --child-bone LowerLeg1.L \
  --span-mm 150 --clearance-mm 0.4 --wall-mm 1.2 \
  --motion-deg 10 --output-dir build/ferris-knee

python3 scripts/check_stl.py build/ferris-knee
```

Use `--blender /path/to/blender` if needed. The output directory must be new. Embedded source scripts are disabled, and the source hash is checked after conversion. Embedded-script control is not a sandbox for untrusted files. The CLI embeds its Blender adapter, so the executable does not need to locate a separate Python script.

Outputs: combined `prototype.stl`, separate `parent.stl` and `child.stl`, the evaluated `source-limb.stl`, `prototype.blend`, `preview.png`, and `report.json`. STL coordinates are millimetres, Z up. Only the two final bodies go into the combined candidate; camera/light/cutter objects are excluded.

## Limits of this experiment

- Supports a single existing parent/child bone pair on one closed weighted mesh.
- Derives a plane from the posed bone directions; collinear bones require an explicit axis policy and are rejected.
- Creates a vertical hinge specimen, with a requested sampled range up to +/-15 degrees. It does not preserve all degrees of freedom of an animation rig.
- Uses pin, keeper, gap and wall dimensions as a design hypothesis, not a universal printer fit.
- Tests each body for one connected component, nonmanifold edges and positive volume, plus intersection volume at five angles. An independent STL reader checks exported triangle closure and component counts.
- Flags a cut neighborhood larger than twice the socket radius for shape review. The initial Ferris specimen triggers that flag.
- Physical strength, retention, support strategy and actual movement must still be checked in a slicer and printed.

The 150 mm span and 0.4 mm clearance are experiment parameters. They are not printer-calibrated values or a user requirement. Read [manual workflow evidence](../../docs/manual-workflows.md) before extending this into a full-model converter.
