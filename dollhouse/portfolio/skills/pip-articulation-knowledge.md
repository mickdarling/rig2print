---
name: pip-articulation-knowledge
type: skill
format_version: v2
version: 1.0.0
description: Reference constraints and primary sources for converting a pre-rigged model into
  a captive printed mechanism.
author: mickdarling
created: '2026-11-14T15:58:38Z'
modified: '2026-11-14T15:58:38Z'
tags:
- rig2print
- print-in-place
instructions: Use these constraints and sources during design and review. Keep unrun checks
  explicit; never infer physical qualification from a render or STL export.
domains:
- 3d-printing
- mechanical-design
examples:
- title: Separate evidence levels
  description: Illustrative use, not an executed physical result.
  input: A closed STL and a joint render are supplied.
  output: Record geometry evidence only; slicing, retention and physical motion remain unrun.
---

# Articulation knowledge

Treat animation rigging, mesh segmentation, assembly-required joints and captive print-in-place fabrication as separate capabilities. Start from the actual armature, skin influences, pose and evaluated mesh of the supplied model; do not require a hand-split replacement mesh. IK and aim controls are not automatically physical joints.

A physical mechanism needs separate closed bodies, attached joint features, explicit one-sided surface gaps, minimum walls, retained moving parts, feasible layer support and requested motion evidence. Scale the model before sizing joints. Do not assume a universal printer clearance or scale a completed STL's gaps without redesign.

Distinguish source observations, design hypotheses, executed geometry checks, slicer review and physical results. A closed STL and a sampled collision check do not prove continuous motion, retention or a working print. Exclude cutters from exports. Verify triangle closure independently of the Blender mesh.

## Primary sources

- Baecher et al., [Fabricating Articulated Characters from Skinned Meshes](https://vcg.seas.harvard.edu/publications/20120101-fabricating-articulated-characters-from-skinned-meshes), ACM TOG 2012: directly relevant skinned-mesh fabrication research; its process is not support-free desktop FDM qualification.
- [Fab Academy manual Blender joint build](https://fabacademy.org/2026/labs/kochi/students/ardradevi-k/assignments/week05.html): written modeling, export correction and print evidence; no source files or images are bundled here.
- [Ferris printing discussion](https://github.com/RayMarch/ferris3d/issues/1): static-print observations, not a captive articulated-print demonstration.

Read docs/existing-projects.md, docs/manual-workflows.md and docs/architecture.md in the Rig2Print repository for the capability review and limitations. Verify current upstream source before recommending reuse; unexecuted tools remain unbenchmarked.
