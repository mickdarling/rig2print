# Manual workflows and what the prototype automates

## Mechanism references

- [Ardradevi K, Fab Academy: print-in-place articulating joint](https://fabacademy.org/2026/labs/kochi/students/ardradevi-k/assignments/week05.html). A stepwise Blender build, export correction, physical print and measurements. Useful lessons: exclude cutters from export, prototype one joint, and measure the printed result. This is a mechanism example, not a rig converter. Its page/assets use a noncommercial license; no files or images were copied into Rig2Print.
- [How To Design Articulating 3D Prints! Blender Tutorial!](https://www.youtube.com/watch?v=y05kcJ8v_Y4). The tutorial linked by the above first-person build log. The written build log was reviewed; no claim of viewing the full video or reproducing its exact mechanism is made.
- [D1nuz: How to MAKE ARTICULATED MODELS for 3D Printing in Blender](https://www.youtube.com/watch?v=JbQRC9jD-y4). Its published chapters cover model preparation, cuts, joint booleans, prototypes, scale and export. Joint types and printed results must be inspected directly before reuse; its download links are not bundled here.
- [Bacher et al., Fabricating Articulated Characters from Skinned Meshes, SIGGRAPH 2012](https://vcg.seas.harvard.edu/publications/20120101-fabricating-articulated-characters-from-skinned-meshes). Direct prior work for mapping existing skinning to physical joints, including placement and collision constraints. Do not equate its fabrication results with support-free desktop FDM.

## Ferris-specific evidence

[Upstream issue 1](https://github.com/RayMarch/ferris3d/issues/1) includes actual static prints, pose experiments, and the creator's discussion of open eyes/tongue meshes, thin leg attachments and subdivision settings. It does not demonstrate captive articulated printing. The new Blender scan independently finds boundary edges on eyes and tongue, and shows that the legs carry upper/lower skin groups.

The inspected asset has 13 meshes and 33 bones. Nineteen bones have matching skin-weight groups. Fourteen other bones include aiming/IK controls. The raw `use_deform` flag alone therefore does not determine which bones should become physical joints.

## First conversion experiment

`prototype-joint` starts from the existing `Armature`, `leg1L`, `UpperLeg1.L` and `LowerLeg1.L`. It verifies the parent/child relation and positive skin influence, evaluates the current rig pose, derives the joint center and a cut bisector from bone coordinates, caps the two resulting regions, and builds a headed pin/C-socket specimen. The cut and captive-joint CSG code is original project code.

The specimen is reoriented as one unit into a print frame and scaled using the whole model's target span. The script does not require a manually split replacement mesh. Its weights check binding; they do not yet optimize the cut or joint location.

The first 150 mm-span experiment produced two connected closed solids and zero Boolean intersection volume at five poses from -10 to +10 degrees in Blender 4.0.2. Its required cut neighborhood is large: approximately 16.93 mm radius. The report marks this for review because shape preservation is not yet satisfactory. The next placement work should reduce that removal region using skinning and local volume, rather than silently calling the candidate finished.

These results are geometry evidence only. No wall-thickness proof, continuous-motion proof, slicer qualification, release/retention test or physical print is claimed.
