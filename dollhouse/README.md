# Dollhouse expertise

`print-in-place-conversion-team` was created in the working Dollhouse portfolio using the Forge v2 research, decomposition, authoring and validation methods. This was a host-driven build; the Forge actor mailbox/runtime pipeline was not executed. Research was a targeted feasibility review, not a complete domain survey.

| Member | Role |
|---|---|
| pip-mechanical-designer | Primary: rig-to-rigid-body mapping and physical joint design |
| pip-mechanism-critic | Monitor: independent evidence and fabrication blocker |
| pip-articulation-knowledge | Core: reusable constraints and source references |
| rig2print-project-context | Support: swappable Ferris project context |
| cad-design-intent | Support: existing CAD method |
| cad-tolerance-fits | Support: existing fit and tolerance method |
| print-dfam-review | Support: existing fabrication review |
| print-calibration-ladder | Support: existing calibration method |
| pip-conversion-review | Support: evidence-separated output template |

The existing `parametric-cad-team`, `procedural-geometry-team`, and `print-fabrication-team` informed the design and remain optional specialist routes. The new ensemble does not nest these broad teams.

## Activate in a portfolio containing the elements

```json
{
  "operation": "activate_element",
  "element_type": "ensemble",
  "params": {"element_name": "print-in-place-conversion-team"}
}
```

Use the read endpoint, `mcp_aql_read`. Then supply the current asset inventory, design brief and required evidence level.

## Portable creation recipe

`bundle.json` contains reviewed MCPAQL creation operations for the six new elements, plus an explicit list of four existing method dependencies. It is a portable recipe, **not** the server's native import/export format or a self-installing program. It intentionally excludes account data, unrelated memories and runtime logs. Its short public knowledge/context seeds are not exact backups of live memory history.

Before replaying, verify that the four `requires` elements exist in the destination portfolio and inspect names for collisions. If missing, obtain the existing Dollhouse 3D modeling methods or author equivalent methods through MCPAQL. Do not overwrite existing elements just to replay the recipe. Apply operations individually through `mcp_aql_create` in listed order, inspect every result, render the template, validate all members, then activate the ensemble.

Inherited methods refer to shared context/template names. The project-context memory explicitly binds `modeling3d-project-context` to `rig2print-project-context` and `cad-design-intent-brief` to `pip-conversion-review`. Read current primary sources for additional facts instead of assuming a different project's printer or tool licenses.

## Validation on 2026-11-13

- Every member was retrieved and inspected; all nine members and the ensemble passed server validation.
- All ten template fields rendered with sample values and no remaining placeholders.
- Activation loaded nine members with zero failures; the ensemble appeared in a fresh paginated listing.
- The server reported one invalid ensemble elsewhere in its global listing. A clean-server restart check was not performed, and no unrelated elements were changed.
- Advisory warnings remain for missing persona triggers, template examples and reused skill examples/domain categories.

This validates the bundle structure and activation. It does not validate generated geometry, Blender integration, or physical prints.
