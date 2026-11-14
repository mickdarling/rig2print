# Working on Rig2Print

Read README.md and docs/existing-projects.md first. This is an early feasibility project.
Do not claim conversion, geometry validation, slicer qualification or a physical print
without the corresponding evidence. Never overwrite source assets. Keep mm units and
one-sided surface clearance explicit. Preserve each moving body as a separate closed
solid; never union across an intended joint. Prefer tested upstream integrations to
duplicated geometry engines. Do not import third-party source without preserving its
license and attribution. Keep credentials, private conversations, and machine-specific
paths out of public artifacts. Run `python3 -m unittest discover -s tests -v` after code
changes. For all-language checks run `python3 scripts/check.py --all`. Build shared
application logic in Rust; keep Blender-specific adapters in Python. Ferris and the
planned python snake are separate exemplars using the same core. Blender integration
and physical checks must be reported separately.
