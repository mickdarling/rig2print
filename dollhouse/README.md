# Dollhouse expertise for Rig2Print

This directory ships ten native Dollhouse Markdown elements with YAML frontmatter and full instructions/reference content. The ensemble has nine bundled members. There is no JSON creation recipe and no dependency on a private portfolio or another CAD ensemble.

Dollhouse is an optional expertise layer for planning and reviewing conversions. It does not replace the Rust/Blender CLI, run a printer, or turn an unverified STL into a qualified print.

## Included elements

| File | Purpose |
|---|---|
| [ensembles/print-in-place-conversion-team.md](portfolio/ensembles/print-in-place-conversion-team.md) | Coordinate the designer, critic, methods and report |
| [personas/pip-mechanical-designer.md](portfolio/personas/pip-mechanical-designer.md) | Map an existing rig to physical bodies and joints |
| [personas/pip-mechanism-critic.md](portfolio/personas/pip-mechanism-critic.md) | Independently challenge geometry, fabrication and evidence claims |
| [skills/pip-articulation-knowledge.md](portfolio/skills/pip-articulation-knowledge.md) | Reusable constraints and primary-source references |
| [skills/rig2print-project-context.md](portfolio/skills/rig2print-project-context.md) | Replaceable public Ferris brief and known limitations |
| [skills/pip-design-intent.md](portfolio/skills/pip-design-intent.md) | Source inspection, mechanical mapping and reproducible recipe |
| [skills/pip-tolerance-fits.md](portfolio/skills/pip-tolerance-fits.md) | Explicit gap conventions, sizing and retention checks |
| [skills/pip-dfam-review.md](portfolio/skills/pip-dfam-review.md) | Layer feasibility, mesh/slicer checks and qualification |
| [skills/pip-calibration-ladder.md](portfolio/skills/pip-calibration-ladder.md) | Target-process coupons and representative joint trials |
| [templates/pip-conversion-review.md](portfolio/templates/pip-conversion-review.md) | Evidence-separated output with nine required fields and optional provenance |

These focused methods are original project elements. They replace the old recipe's references to four unbundled CAD/printing skills. Broad specialist teams remain optional; none is needed to install this set.

## Install on the Dollhouse server host

1. Install and connect [DollhouseMCP](https://github.com/DollhouseMCP/mcp-server) in your MCP client. These files use the native v2 element format. Confirm that your server supports ensembles and uses a filesystem portfolio.
2. Find the portfolio actually configured on that server. Its default is `~/.dollhouse/portfolio`; `DOLLHOUSE_PORTFOLIO_DIR` can override it. A remote/hosted server's portfolio is on the server host, not necessarily your laptop.
3. Run the following from the Rig2Print checkout on that host, using the real portfolio path. The installer previews by default; `--apply` copies the Markdown files unchanged into their type folders. It never converts element definitions to JSON and refuses all existing-file collisions before copying.

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/install_dollhouse.py /absolute/path/to/portfolio
python3 scripts/install_dollhouse.py /absolute/path/to/portfolio --apply
```

The portfolio directory must already exist. Installation does not activate elements, edit server configuration or overwrite your live portfolio. A concurrent write or later filesystem error stops installation; inspect any files already copied before retrying.

If names already exist, compare the files first. Back up the existing affected elements outside the watched portfolio and deactivate the old ensemble before an intentional replacement, or choose a different ensemble name and consistently rename its references. Do not delete or overwrite session memories to install this set. Restart/reload the server if its file watcher does not discover copied files.

## Validate and activate

Ask your connected assistant:

> List the elements in the Rig2Print Dollhouse set, read each one and validate all ten. Check that print-in-place-conversion-team resolves all nine bundled members, then activate it. Report missing elements or validation failures before doing conversion work.

For clients exposing MCP-AQL, use `mcp_aql_read` with these tool arguments (these are requests, not element files):

```json
{
  "operation": "validate_element",
  "element_type": "ensemble",
  "params": {"element_name": "print-in-place-conversion-team"}
}
```

```json
{
  "operation": "activate_element",
  "element_type": "ensemble",
  "params": {"element_name": "print-in-place-conversion-team"}
}
```

Validate the personas, skills and template individually too, using their types/names from the table. Inspect the activation response: all nine members should load with no failures. A monitor role loads critique instructions; it does not itself spawn an independent reviewer or provide a second-process guarantee.

## Use the expertise

Give the assistant access to this repository and the actual Blender asset, available source/license/revision details, inventory and available geometry/slicer/print evidence. Include final size, desired motion and printer/material/profile when known. Mark unknowns explicitly; do not invent them to complete the report.

For Ferris:

> Use print-in-place-conversion-team on the pinned Ferris source and current knee report. Read the public project context and open issues first. Identify a joint placement that preserves more of the leg, state which skin/bone evidence supports it, and propose one concrete experiment. Have the critic assess the evidence independently. Render pip-conversion-review; mark slicer and physical evidence unrun unless supplied.

For another pre-rigged character, update the public context reference skill or provide a separate asset brief. Keep reusable mechanical methods separate from model-specific facts. Use the Rust CLI and Blender adapter for deterministic conversion work; record actual outcomes and hashes rather than presenting a proposed experiment as executed.

The report template requires `asset`, `process`, `mapping`, `joints`, `geometry_evidence`, `slicer_evidence`, `physical_evidence`, `blockers` and `next_experiment`. `provenance` is optional: omit it or supply available source details; when omitted it renders as an empty value. Missing provenance alone does not block a review. Supply the nine required fields when calling `render`; use `unrun` for absent evidence.

To stop using this set, ask Dollhouse to deactivate the ensemble and check its response. Review any members that remain active before continuing unrelated work.

## Native files and migration

The old `bundle.json` was a custom list of MCP creation operations, not a directly loadable native element distribution. It has been removed.

The public knowledge and context seeds are now Markdown reference **skills**. Dollhouse's live **memories** use YAML and have appendable entry histories; renaming a memory file to `.md` would not convert it. Existing runtime memories may remain in your portfolio but are not referenced by this packaged ensemble. No private history, runtime logs or account-specific settings are included.

Native v2 ensemble files use a top-level `elements` list with `element_name`, `element_type` and `role`; template variables also live at the top level of frontmatter. These filesystem fields differ from `create_element` API parameters. See the [official format reference](https://github.com/DollhouseMCP/mcp-server/blob/main/docs/reference/element-format-guide.md) and [manual construction guide](https://github.com/DollhouseMCP/mcp-server/blob/main/docs/developer-guide/manual-element-construction.md).

## Verification

`python3 scripts/check.py` validates frontmatter, filenames/types, all local member references, roles and template placeholders, and runs installation collision/copy tests. It does not contact or modify a live Dollhouse portfolio. Validate and activate the installed set on your server as above; offline consistency is not a server activation or physical-print result.

On 2026-11-14, this Markdown set was also installed into an isolated temporary portfolio and loaded with the native managers from a local DollhouseMCP 2.0.0-rc.2 build: all ten elements passed validation with no warnings, all ten template fields rendered, and all nine ensemble members activated with zero failures. The live portfolio was not changed. This manual integration check is separate from CI and does not establish compatibility with every server version.
