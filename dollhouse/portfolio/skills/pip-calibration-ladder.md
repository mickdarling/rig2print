---
name: pip-calibration-ladder
type: skill
format_version: v2
version: 1.0.0
description: Plan and record target-printer calibration and representative captive-joint trials.
author: mickdarling
created: '2026-11-14T15:58:38Z'
modified: '2026-11-14T15:58:38Z'
tags:
- rig2print
- print-in-place
instructions: Use when printer settings or fit calibration are missing or have changed. Plan
  useful coupons and record measurements; do not claim to have run a printer test without
  evidence.
domains:
- 3d-printing
- mechanical-design
examples:
- title: Plan the first joint coupon
  description: Illustrative use, not an executed physical result.
  input: Printer/material/profile are not yet specified.
  output: Identify missing setup, propose graded coupons and a measurement log; do not claim
    a fit is calibrated.
---

# Clearance and joint calibration

1. Record printer, material, nozzle, orientation, layer height, slicer/profile versions and operator. Check machine condition, filament handling and first-layer setup using the manufacturer's instructions.
2. Use the target system's documented calibration sequence for temperature, extrusion/flow, pressure compensation and motion settings as applicable. Record measured results instead of assuming universal values.
3. Generate graded joint or clearance coupons around the proposed gap at the final mechanism scale. Keep gap convention explicit and use the same material/orientation/profile as the exemplar.
4. Measure printed dimensions, release effort, achievable motion, retention and failure modes. Photograph or film the result. Do not mistake post-print assembly for a print-in-place result.
5. Select dimensions from the measured evidence, then print a representative Ferris joint. Only proceed to full-character qualification after that test passes.
6. Repeat affected tests after size, orientation, material, nozzle, machine or profile changes. Keep calibration records separate from the public seed elements.
