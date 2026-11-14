---
name: pip-tolerance-fits
type: skill
format_version: v2
version: 1.0.0
description: Define unambiguous printed-joint gaps, retention and process-calibrated dimensions.
author: mickdarling
created: '2026-11-14T15:58:38Z'
modified: '2026-11-14T15:58:38Z'
tags:
- rig2print
- print-in-place
instructions: When sizing a moving interface, distinguish gap conventions, check mechanical
  constraints, and require target-process coupon evidence before calling the fit qualified.
domains:
- 3d-printing
- mechanical-design
examples:
- title: Clarify a trial clearance
  description: Illustrative use, not an executed physical result.
  input: The experiment specifies a 0.4 mm gap.
  output: Identify one-sided radial/axial convention; check derived sizes and require target-process
    calibration.
---

# Joint dimensions and fits

- Specify all dimensions at final size in millimetres. Label each clearance as one-sided radial, diameter allowance, axial or planar gap; never use those terms interchangeably.
- Record the intended fit and motion, pin and cavity radii, keeper dimensions, throat/slot openings, minimum wall and attachment cross-section. Check derived dimensions remain positive and leave sufficient material.
- Check capture over the requested motion, including possible escape paths. Keeper diameter larger than one opening alone is a design hypothesis, not proof of retention.
- Account for material/process variation, first-layer spread and orientation. Use graded coupons on the chosen machine, material, nozzle and slicer profile before selecting a production gap.
- Record nominal dimensions, measured results, uncertainty and rejected combinations in pip-conversion-review. Do not transfer nominal machining fits or another printer's calibration blindly.
- If final size or process changes, recompute the mechanism and repeat the affected checks; do not scale a finished STL as a substitute.
