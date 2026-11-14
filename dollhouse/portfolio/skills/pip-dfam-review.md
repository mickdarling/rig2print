---
name: pip-dfam-review
type: skill
format_version: v2
version: 1.0.0
description: Review captive articulation geometry, print orientation, layer support and slicing
  evidence.
author: mickdarling
created: '2026-11-14T15:58:38Z'
modified: '2026-11-14T15:58:38Z'
tags:
- rig2print
- print-in-place
instructions: Before recommending a print, independently review geometry, layer feasibility,
  slicing and physical evidence. Block unsupported qualification claims and name the next
  useful experiment.
domains:
- 3d-printing
- mechanical-design
examples:
- title: Review unprinted output
  description: Illustrative use, not an executed physical result.
  input: Two closed bodies pass five sampled collision checks.
  output: Keep continuous motion, retention, wall/layer review, slicing and physical qualification
    separate and unrun.
---

# Fabrication review

1. Verify final units and intended body count. Check connected closed surfaces, triangle closure, consistent orientation, self-intersections, minimum walls and attachment regions. State which checks were actually run.
2. Check positive separation and collisions over requested motion; disclose sample count and limits. Verify retention separately from collision freedom.
3. Review a feasible print orientation for every body: first-layer contact, overhangs, bridges, wall extrusion paths and support removal. Reject supports that cannot be removed from a captive joint.
4. Inspect slicer toolpaths for actual size, gap preservation, unexpected repairs/fusion, thin-wall omissions and first-layer spread. Record slicer version/profile and changes.
5. Print and measure a representative joint at final scale before the whole model. Demonstrate motion and retention without inserting a pin or snapping parts together.
6. Report blockers with the next test. Use plan-only, geometry-only, slicer-reviewed, joint-print-verified and full-print-verified separately. An unrun test is not a pass.
