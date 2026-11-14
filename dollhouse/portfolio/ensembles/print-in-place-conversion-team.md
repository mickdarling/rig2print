---
name: print-in-place-conversion-team
type: ensemble
format_version: v2
version: 1.0.0
description: Coordinate pre-rigged model conversion with an independent fabrication/evidence
  critic. All members are bundled.
author: mickdarling
created: '2026-11-14T15:58:38Z'
modified: '2026-11-14T15:58:38Z'
tags:
- rig2print
- print-in-place
elements:
- element_name: pip-articulation-knowledge
  element_type: skill
  role: core
  priority: 50
  activation: always
- element_name: rig2print-project-context
  element_type: skill
  role: support
  priority: 50
  activation: always
- element_name: pip-mechanical-designer
  element_type: persona
  role: primary
  priority: 50
  activation: always
- element_name: pip-mechanism-critic
  element_type: persona
  role: monitor
  priority: 50
  activation: always
- element_name: pip-design-intent
  element_type: skill
  role: support
  priority: 50
  activation: always
- element_name: pip-tolerance-fits
  element_type: skill
  role: support
  priority: 50
  activation: always
- element_name: pip-dfam-review
  element_type: skill
  role: support
  priority: 50
  activation: always
- element_name: pip-calibration-ladder
  element_type: skill
  role: support
  priority: 50
  activation: always
- element_name: pip-conversion-review
  element_type: template
  role: support
  priority: 50
  activation: always
activationStrategy: sequential
conflictResolution: priority
contextSharing: selective
allowNested: false
---

# Print-in-place conversion team

Read the reference context and source inventory first. Use the designer and focused methods to propose a mechanical conversion, then have the critic assess the supplied evidence independently. The monitor role loads the critic's instructions; it does not itself launch an independent process or guarantee a second review.

Render pip-conversion-review with blockers and the next concrete test. Require physical evidence before labeling a joint or full model print-verified. This expertise guides work; the deterministic Rust/Blender tool remains usable without Dollhouse.

All nine members are shipped in this repository. No external ensembles, methods, account data or private memory history are required.
