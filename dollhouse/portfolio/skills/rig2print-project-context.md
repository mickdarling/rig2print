---
name: rig2print-project-context
type: skill
format_version: v2
version: 1.0.0
description: Public, replaceable reference brief for the Ferris exemplar; contains no private
  portfolio history.
author: mickdarling
created: '2026-11-14T15:58:38Z'
modified: '2026-11-14T15:58:38Z'
tags:
- rig2print
- print-in-place
instructions: Read this public brief and current repository evidence before choosing model-specific
  names, scale, process or claims. Record changes and unknowns instead of inheriting another
  project's settings.
domains:
- 3d-printing
- mechanical-design
examples:
- title: Use the current Ferris brief
  description: Illustrative use, not an executed physical result.
  input: Plan the next experiment using the knee candidate.
  output: Read current issues and report; retain shape-loss blocker and unspecified print
    setup.
---

# Rig2Print project context

Repository: https://github.com/mickdarling/rig2print

Read the current repository and open issues before relying on this snapshot. Source: RayMarch/ferris3d at 2a8ed2b5484b87e831c70f3346891fe1cab9aab4, blend/ferris3d_v1.0.blend, CC0-1.0. Its inspected SHA-256 is a158352815726791e7bf14b1b08696fc046e9d51797ccdebda86a0f9fabf2d2e.

Blender 4.0.2 inspection found 13 meshes and 33 bones; 19 bones have matching positive skin influences and 14 others include rig controls. The experimental knee uses leg1L / UpperLeg1.L / LowerLeg1.L. A two-body candidate passes independent STL closure and five collision samples, but its approximately 16.93 mm cut radius removes too much source shape. This is not full-Ferris conversion or print qualification.

The 150 mm whole-model span, 0.4 mm gap and +/-10 degree sampled sweep are experiment parameters, not user requirements or calibrated printer settings. Target printer, material, nozzle, slicer/profile and required motion remain unspecified. Do useful source/geometry work while identifying which later checks depend on them.

Keep shared sizing and mechanical constraints in Rust and Blender operations in Python. Open review follow-ups: #12 moves shared hinge logic into Rust; #13 handles a source scene without a World. Consult their current status. Wait for completed final-head review and clean findings before merging; track any authorized deferral in a separate issue first.

Use pip-conversion-review for the result. Replace this reference skill's body when adapting to another asset. Keep optional live session memories separate; they are not part of this public distribution.
