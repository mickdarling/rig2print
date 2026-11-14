# Ferris exemplar

The first input is [RayMarch/ferris3d](https://github.com/RayMarch/ferris3d). It publishes `blend/ferris3d_v1.0.blend` under CC0. Original character: Karen Rustad Tölva. 3D interpretation: RayMarch.

Repository inventory and licensing have been inspected. The Blender scene, actual rig structure and physical manufacturability have **not** yet been verified. Do not infer the number or names of mechanical joints from the preview.

## Obtain the pinned source

Run from the repository root in a network-enabled environment:

```sh
git clone https://github.com/RayMarch/ferris3d.git assets/ferris3d
git -C assets/ferris3d checkout --detach 2a8ed2b5484b87e831c70f3346891fe1cab9aab4
python3 -m rig2print inspect assets/ferris3d/blend/ferris3d_v1.0.blend \
  --blender /path/to/blender --output build/ferris-inventory.json
```

`source.json` records the upstream Git blob id, which is **not** a file SHA-256. The inspector computes SHA-256 from the actual downloaded `.blend`.

## First experiment

1. Confirm Blender compatibility, units, world bounds, mesh/rig names and modifiers.
2. Choose the final physical span and print pose. The draft's 150 mm is a design hypothesis, not a measured source size or a user requirement.
3. Map one limb/body attachment into rigid bodies. Compare captive hinge and ball/socket options against available volume and desired motion.
4. Benchmark the upstream mesh converter on simpler original fixtures before applying an adapter to Ferris's branch structure.
5. Print a clearance coupon, then the representative joint at final scale. Finish the complete crab only after this gate.

`plan.draft.json` intentionally has empty body/joint mappings and unspecified printer/material fields. Its checker must reject it until real design inputs replace these gaps. It is not a conversion recipe or an STL.
