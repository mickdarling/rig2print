# Articulated python snake exemplar

Ferris represents Rust; the second exemplar is a python snake. This is a proposed original model, not the Python logo. No snake mesh, Blender rig or printable STL has been created yet.

The snake provides a simple chain of joints, which can exercise the static-mesh conversion baseline before the more difficult branching crab. It complements Ferris rather than replacing it.

## Design brief

- Create original, openly licensed source geometry with a recognizable head, tapered body and tail.
- Supply an articulated Blender source and a static mesh export, with the joint map kept separately.
- Begin with a straight or gently curved print pose and repeated captive joints. Verify end segments, thin tail features and bends rather than assuming all repeated joints behave identically.
- Choose final scale, segment count, printer, material and measured clearance through the same reviewed plan and coupon workflow as Ferris.
- Keep geometry generation, reports and source recipes reproducible. A Python generator may use Blender's Python API; the shared validator and future conversion core are Rust.

## Acceptance

Use the same source/plan/geometry/motion/slicer/physical evidence gates as Ferris. Publish the source and plan first, then unverified candidates, and only label a one-piece print verified after its joints move and remain captive without assembly. The same Rust core must work for both examples through model-specific plans.
