# Roadmap

## M0 — Evidence and reusable project foundation

Bootstrap: source provenance, reuse study, scene inspector, plan-contract checker, Dollhouse expertise, and acceptance-driven issues. Unit checks can run without Blender. Blender CI now inspects the pinned Ferris rig and exercises a knee specimen; physical evidence remains outstanding.

## M1 — Benchmark upstream conversion

Compare articulated-toys on centred, translated and branched original fixtures. Record backend/dependency versions and hashes. Check unions/attachment, retained solids, gaps, topology and dimensional fidelity. Run actual slicer review before recommending output. Decide whether to wrap, contribute fixes upstream, or replace a narrowly identified layer.

## M2 — Inspect and map Ferris

Run the inspector with a pinned Blender version. Confirm units and target span, rig hierarchy, skinning, object segmentation, modifiers and rest versus print pose. Produce a reviewed joint map with no invented names. Choose target printer, material, nozzle, profile and desired motion. Implement representative segmentation and geometry export integration tests.

Progress: actual scene inventory and one weighted knee connection have been exercised in Blender 4.0.2. The first cut removes too much surrounding shape and is marked for review. Full joint mapping, improved local placement and a printer-calibrated process remain open.

## M3 — Physical joint coupon

Implement or reuse a captive hinge and a ball/socket candidate with finite printable walls, retention and feasible layer support. Print a graded clearance coupon on the target setup. Print a Ferris limb joint at final scale, measure motion and retention, and record failure evidence. No assembly should be required for a print-in-place result; freeing light incidental adhesion is distinct from inserting pins or snapping parts together.

## M4 — Complete Ferris exemplar

Build complete model from the reviewed plan, inspect all joint gaps and collisions, check the sliced toolpath, then perform one complete print. Publish recipe, source, STL, slicer profile details, hashes and photos/video of motion. State unsupported bones, altered silhouette and measured motion limits. Do not label the STL verified before the physical print passes.

## M5 — Python snake and reusable Blender workflow

Create an original articulated python snake as the second openly licensed example. Its simple chain can also serve as an early M1 benchmark fixture before the complete Ferris print. Validate that the same Rust core pipeline works for chain and branching skeletons through different plans rather than model-specific conversion code. Add an interactive Blender panel and 3MF packaging after the STL workflow is qualified. See examples/python/README.md for the brief; the snake asset is not created yet.

## Acceptance rubric

| Gate | Evidence required |
|---|---|
| Provenance | Source revision/license, downloaded asset hash, attribution |
| Plan | Known bodies and joint references, explicit mm units and final scale, target process |
| Geometry | Separate closed moving solids; attached features; no unintended overlap or removed retention |
| Motion | Clearance and collision results across requested motion with sampling limits recorded |
| Fabrication | Wall and overhang review; each body has a feasible layer/support path; no inaccessible trapped support |
| Slicer | Expected size, preserved gaps, continuous intended bodies, no surprise repairs or fused toolpaths |
| Physical | One-piece print, no assembly, motion and retention demonstrated on documented setup |
| Reuse | Second model reproduced through the same core with a different plan |
