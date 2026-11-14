---
name: pip-design-intent
type: skill
format_version: v2
version: 1.0.0
description: Capture a pre-rigged asset conversion brief, mechanical mapping and reproducible
  model recipe.
author: mickdarling
created: '2026-11-14T15:58:38Z'
modified: '2026-11-14T15:58:38Z'
tags:
- rig2print
- print-in-place
instructions: Before generating or revising geometry, inspect the actual pre-rigged source
  and capture a reviewable brief. Use the bundled context and review template; do not require
  external CAD teams.
domains:
- 3d-printing
- mechanical-design
examples:
- title: Inspect a pre-rigged limb
  description: Illustrative use, not an executed physical result.
  input: A .blend has an armature, weighted skin and IK controls.
  output: Record source/pose/units; select actual weighted connections and exclude controls
    before proposing cuts.
---

# Rig-to-mechanism design intent

1. Record source revision, license, file hash, Blender version, evaluated modifiers, units and pose. Inspect actual names and transforms; never invent bone or mesh names from an image.
2. State intended motion and final physical size. Separate known requirements from trial parameters and unspecified process settings.
3. Use positive skin influence and hierarchy to identify candidate body connections. Exclude IK/aim controls. Build a rigid-body/joint graph; record lost degrees of freedom and deliberately omitted joints.
4. Choose anchors using local available volume and required attachment thickness. Reject a cut that destroys the character's silhouette; do not silently enlarge housings until it fits.
5. Define pin/socket dimensions, one-sided gaps, keeper geometry, walls, motion limits and print frame explicitly. Use pip-tolerance-fits for interfaces and pip-dfam-review for fabrication constraints.
6. Keep reusable mechanical calculations in Rust and Blender CSG in its adapter. Preserve the original source and export only intended bodies. Record versions, parameters, hashes and failures.
7. Render pip-conversion-review, with evidence for each claim and a concrete next experiment.
