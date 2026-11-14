# Existing projects and reuse study

Reviewed 2026-11-13. Evidence here is README and source inspection, not a successful installation, conversion, or print. The search was targeted, not exhaustive.

| Project | What the public project provides | Relevance and limits | Decision |
|---|---|---|---|
| [articulated-toys](https://github.com/tusosos/articulated-toys) | MIT Python converter for STL/OBJ/3MF; uniform or waist-based slices with ball/socket generation | Closest direct candidate. Converter consumes a static mesh, slices along one coordinate axis, and does not read a Blender rig. Branching crab limbs need separate handling. | First baseline to benchmark; do not treat its output as qualified. |
| [mcp-printable](https://github.com/AaronGoldsmith/mcp-printable) | MIT MCP tools for Blender/OpenSCAD, booleans, STL export, mesh and clearance/retention checks | Useful optional modeling and review backend; README does not establish automatic rig-to-physical-joint conversion. | Evaluate integration before writing equivalent tools. |
| [PrintSplit](https://github.com/wenyen-hsu/printsplit) | GPL-3.0-or-later Blender extension for mesh cutting and rigid/movable connectors | Movable connectors are described as snap-fit or slide-in assembly. This is distinct from captive print-in-place output. | Interactive comparison; no source copied. Review license obligations if integration is proposed. |
| [Articulate AnyMesh](https://github.com/UMass-Embodied-AGI/Articulate-Anymesh) and [project page](https://articulate-anymesh.github.io/) | Mesh articulation for simulation, including URDF output | Digital articulation and segmentation may inform future work. Does not establish printable captive joints. | Research reference; not the initial conversion backend. |
| [Fabricating Articulated Characters from Skinned Meshes](https://vcg.seas.harvard.edu/publications/20120101-fabricating-articulated-characters-from-skinned-meshes), SIGGRAPH 2012 | Research mapping skinning and articulation to manufactured mechanical joints | Direct conceptual prior art; paper reports single, assembled printed pieces. This does not establish suitability for support-free desktop FDM. No maintained reusable implementation was established in this review. | Study joint placement and collision constraints; do not claim this project invents the conversion concept. |
| [LayerMechanic](https://superhivemarket.com/products/layermechanic-print-in-place-motion/docs) | Public documentation for geometric hinge/slider motion preflight | Checks existing joints; explicitly does not create them and does not guarantee a printed result. | Capability comparison only; open-source licensing not established. |

## Source-level findings: articulated-toys

Inspected [`scripts/articulate_model.py`](https://github.com/tusosos/articulated-toys/blob/2c957023803e064b77c95a5cc3c8e33667b54225/scripts/articulate_model.py), revision `2c957023803e064b77c95a5cc3c8e33667b54225`.

- `articulate_model` chooses a single X/Y/Z axis from the bounds or a user argument and slices across that axis. It has no skeleton, skin weights, or branching joint graph input.
- `create_joint_at_position` translates joints along that axis; the other two coordinates remain zero. Off-origin cross-sections need a targeted regression case to establish correct attachment.
- The final output is `trimesh.util.concatenate(all_parts)`. Concatenation adds triangles; it does not prove Boolean fusion of each joint into its intended rigid body, separation of moving solids, or retention.
- A Boolean failure in socket construction falls back to an approximate mesh. That path must be tested and surfaced in any adapter rather than silently accepted as print-ready.

These are observed implementation choices and reasons to test, **not** claims that every upstream model fails. We have not executed this converter.

## Benchmark before a backend decision

1. Start with an original capsule-like mesh, then a translated copy. Test uniform and waist segmentation. Compare dimensions, attachment, shell count, watertightness and intersections.
2. Use a small original branched fixture. Determine whether explicit per-limb processing and rigid-body unions can preserve the branch structure.
3. Inspect Ferris and export a posed, explicitly scaled intermediate; keep rig information separately. Do not feed the whole crab into a chain heuristic and assume that limb joints are preserved.
4. Compare the baseline to one manually designed captive hinge and one captive ball joint. Inspect layer previews, print clearance coupons, then a representative limb.
5. Reuse, adapt, or replace only the failed layer. Publish the decision with actual reports and artifact hashes.

## Pinned references

| Source | Inspected revision | License evidence |
|---|---|---|
| RayMarch/ferris3d | `2a8ed2b5484b87e831c70f3346891fe1cab9aab4` | Repository LICENSE and README: CC0-1.0 |
| tusosos/articulated-toys | `2c957023803e064b77c95a5cc3c8e33667b54225` | Repository LICENSE: MIT |
| AaronGoldsmith/mcp-printable | `2810b946cb8a42b022ac34d31e8b168e3fc48bd1` | Repository LICENSE: MIT |
| wenyen-hsu/printsplit | `29cfe0d648b679701ba9e35f6e76ebe490d917b2` | README: GPL-3.0-or-later |

## Process guidance and disagreements

[Prusa's modeling guidance](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135) says tolerance depends on material, orientation, geometry and calibration, and gives an initial movable-part clearance. The existing Dollhouse fabrication guidance likewise requires coupons. Treat numeric recommendations as starting hypotheses, with radial, diametral and axial gaps named separately.

The mcp-printable print-in-place guide contains tension between its suggested zero bottom gap in one passage and its later prohibition on touching surfaces. It also presents broad bridging recommendations. Do not promote those passages to universal rules: evaluate each body's support/bridge path layer by layer and verify it on the chosen process.
