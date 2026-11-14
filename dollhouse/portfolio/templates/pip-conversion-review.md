---
name: pip-conversion-review
type: template
format_version: v2
version: 1.0.0
description: Evidence-separated conversion review.
author: mickdarling
created: '2026-11-14T15:58:38Z'
modified: '2026-11-14T15:58:38Z'
tags:
- rig2print
- print-in-place
instructions: Render every field. Use unrun for absent evidence. Use one-line variable values.
variables:
- name: asset
  type: string
  required: true
- name: provenance
  type: string
  required: true
- name: process
  type: string
  required: true
- name: mapping
  type: string
  required: true
- name: joints
  type: string
  required: true
- name: geometry_evidence
  type: string
  required: true
- name: slicer_evidence
  type: string
  required: true
- name: physical_evidence
  type: string
  required: true
- name: blockers
  type: string
  required: true
- name: next_experiment
  type: string
  required: true
output_format: markdown
examples:
- title: Unprinted knee review
  description: Complete sample variables with absent evidence marked unrun.
  variables:
    asset: Ferris knee candidate
    provenance: unrun
    process: unrun
    mapping: unrun
    joints: unrun
    geometry_evidence: unrun
    slicer_evidence: unrun
    physical_evidence: unrun
    blockers: Shape preservation and physical qualification remain open.
    next_experiment: Compare a smaller joint placement using the actual rig and local mesh
      volume.
---

## asset
{{asset}}

## provenance
{{provenance}}

## process
{{process}}

## mapping
{{mapping}}

## joints
{{joints}}

## geometry evidence
{{geometry_evidence}}

## slicer evidence
{{slicer_evidence}}

## physical evidence
{{physical_evidence}}

## blockers
{{blockers}}

## next experiment
{{next_experiment}}
