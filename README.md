# Rig2Print

Turn articulated Blender models into **print-in-place articulated models**. Ferris the Rustacean is the first exemplar; the goal is a reusable, inspectable workflow for other characters.

**Status: project bootstrap and feasibility study.** This repository currently provides a Blender scene inspector, a mechanical-plan checker, an evidence-based reuse study, and a staged implementation backlog. It does **not** yet generate articulated STL files. No Ferris conversion or physical print has been verified.

An animation rig describes motion. A printable mechanism needs separate closed solids, physical joints, clearance, retention, adequate walls, and a feasible print orientation. Simply exporting a posed mesh to STL loses the rig.

## Start here

- [Existing projects and reuse decisions](docs/existing-projects.md)
- [Ferris exemplar](examples/ferris/README.md)
- [Architecture and scope](docs/architecture.md)
- [Roadmap and acceptance criteria](docs/roadmap.md)
- [Dollhouse expertise](dollhouse/README.md)

## Reuse before rebuilding

We will benchmark [articulated-toys](https://github.com/tusosos/articulated-toys) for static-mesh conversion and evaluate [mcp-printable](https://github.com/AaronGoldsmith/mcp-printable) for Blender geometry and print checks. Neither has been run by this project yet. [PrintSplit](https://github.com/wenyen-hsu/printsplit) is a useful comparison for interactive segmentation and assembled joints. The 2012 paper [Fabricating Articulated Characters from Skinned Meshes](https://vcg.seas.harvard.edu/publications/20120101-fabricating-articulated-characters-from-skinned-meshes) is directly relevant prior work.

The intended contribution is rig-aware mapping, branching limb handling, reproducible conversion recipes, and evidence that the resulting mechanism works on a real printer. Backend selection remains open pending the benchmark.

## Run the starter tools

Python 3.11+; the checker has no third-party dependencies. Blender 4.2+ is the intended inspection target, with integration verification still pending.

```sh
python3 -m rig2print --help
python3 -m unittest discover -s tests -v

# Download the pinned upstream asset first; see examples/ferris/README.md.
python3 -m rig2print inspect assets/ferris3d/blend/ferris3d_v1.0.blend \
  --blender /path/to/blender --output build/ferris-inventory.json

# Deliberately fails: this is an incomplete design brief, not a print-ready plan.
python3 -m rig2print check-plan examples/ferris/plan.draft.json
```

The inspector reports objects, evaluated mesh topology, world-space bounds, armatures, deform bones, vertex groups and modifiers. It disables automatic embedded script execution, does not save over the source, and writes only the requested report. This setting is not a security sandbox: inspect untrusted files in an isolated environment.

`check-plan` checks the design contract, not mesh geometry or printability. Passing it cannot qualify an STL. All distances in plans are millimetres; `clearance_mm` is a **one-sided surface gap**, not a diameter allowance. Choose the final scale before sizing joints.

## First physical milestone

Print and measure a clearance coupon, then one Ferris limb joint, then the complete model on one documented printer/material/profile combination. Record slicer evidence and actual motion. Label unprinted candidates as unverified. Printer and material for the exemplar are not yet specified.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep conversion logic usable without an AI service. Dollhouse expertise is an optional planning and review layer.

## License and credit

Original project code and documentation: [MIT](LICENSE). Ferris is a separate CC0 asset by RayMarch, based on the character by Karen Rustad Tölva; see [provenance](examples/ferris/source.json). Upstream models and third-party tools retain their own licenses. No third-party implementation is vendored in this bootstrap.
