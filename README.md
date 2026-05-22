# 保存屈曲模态：
```
*node file,  global=yes,  last mode=1
U
```
# 叠加曲屈模态：
```
*imperfection,  file=文件名,  Step=1
1, 0.7%b
```

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Abaqus FEA automation for multi-cell aluminum extrusion buckling analysis. Scripts run **inside Abaqus CAE** (not standalone Python) using `abaqus cae noGUI=<script>.py`.

## How to Run

```bash
abaqus cae noGUI=build_model_local.py    # Local buckling (defect factor study)
abaqus cae noGUI=build_model_overall.py  # Overall buckling (length/section study)
abaqus cae noGUI=自定义方案.py            # Custom nonlinear static with imperfections
```

Post-processing (standalone Python — Abaqus not required):
```bash
python extract_data.py
```

## Architecture

### Analysis workflow (2-stage)

Each `build_model_*.py` runs both stages in sequence:

1. **Linear eigenvalue buckling** — creates the shell model, applies a unit compressive load, submits a `BuckleStep` to get eigenmodes, then patches the keyword block to write a `.fil` node file with mode 1 displacements.
2. **Nonlinear Riks post-buckling** — copies the model, applies the first buckling mode as an initial geometric imperfection via `*Imperfection`, suppresses the force load, applies a displacement-controlled boundary condition, and runs a `StaticRiksStep`.

Results are extracted as load-displacement CSV + PNG from the Riks job's ODB history output (U3/RF3 at the loaded reference point).

### File roles

| File | Purpose |
|---|---|
| `build_model_local.py` | Parameter studies: defect factor, dimensions, hardening factor, material, thickness, height-width ratio, mesh seed. Defect factor = `defect_factor * h`. Length = `3 * h3`. |
| `build_model_overall.py` | Parameter studies across predefined section/length lists. Length is explicit (`l` parameter). Imperfection = `0.001 * l`. Contains a `TASKS` list driving the parameter sweep. |
| `extract_data.py` | Standalone post-processing: walks result directories, aggregates CSVs, generates overlaid load-displacement plots per first-level directory. |
| `hhhbg.py` | Separate plate-with-hole buckling analysis (single model, hardcoded params). |
| `自定义方案.py` | Custom analysis: 2-part script that runs eigenvalue buckling → pickle-extracts mode data → copies model → applies amplitude-controlled displacement loading in a StaticStep (not Riks). |

### Key classes and functions

- `MultiCellAluminumSection` — defines the cross-section geometry (b, h, t, chamber dimensions) and generates 5 closed centerline polygons (4 corner chambers + middle web/flange). Note: two near-identical copies exist in `build_model_local.py` and `build_model_overall.py` with slightly different constructors (defect_factor vs explicit length).
- `create_buckling_model()` — builds the full Abaqus model: sketch, shell extrusion, material (elastic + plastic), section assignment, RP coupling, boundary conditions, buckling step, meshing, submits both jobs and calls `extract_load_displacement()`.
- `extract_load_displacement()` — opens the Riks ODB, reads U3/RF3 history output, writes CSV and generates PNG load-displacement curve.
- `ALUMINUM_MATERIALS` — dict mapping yield stress keys to plastic stress-strain tables for various aluminum alloys (6063A-T4, 6082-T4, 6063-T5, 6061-T6, 6082-T6, etc.).

### Known limitations

- Edge selection uses hardcoded `getSequenceFromMask(mask=...)` — these masks are geometry-specific and will break if the cross-section sketch changes. They select the top/bottom edges of the extruded shell for coupling to reference points.
- Reference point positions are also hardcoded (e.g., `(0, 0, -50)` / `(0, 0, l+50)`).
- `build_model_overall.py` reference points are offset at `x=20.0` instead of `0.0` — a likely artifact from a specific section geometry.
- Working directories are hardcoded to Windows paths (`D:\abaqus_working_directory\...`).

## Material Data

`ALUMINUM_MATERIALS` keys index aluminum alloy grades:
- 90/110: 6063A-T4 / 6082-T4
- 150: 6063A-T5
- 180/181/182/183: 6063-T6 / 6063A-T6 variants with different hardening exponents (n)
- 240: 6061-T6
- 260: 6082-T6
- 80/81/82: 6082-T6 test data at different thicknesses (4mm/6mm/5mm)

Plastic data format: `[[stress_1, plastic_strain_1], [stress_2, plastic_strain_2], ...]`
