# YOLO Camera Tracker

Mechanical design files for a two-axis camera and sensor tracker intended for
YOLO-based object-tracking projects.

## CAD contents

The [`cad`](cad) directory contains the original SolidWorks models and
assemblies, along with neutral and printable exports where available.

- `cad/Easy_version/` — simplified/current tracker design, including the main
  `camer_tracker_easy.SLDASM` assembly and electronics enclosure.
- `cad/Easy_version/3dp_to_print/` — ready-to-slice STL files for the easy
  version.
- `cad/3dp_to_print/` — STEP exports from earlier design revisions (`v1.0` to
  `v1.2`).
- `cad/distance_sensor-1.snapshot.12/` — distance-sensor reference model,
  images, datasheet, and STEP files.
- `cad/YOLO_tracker_send2ryan/` — packaged SolidWorks source revision.
- Files directly inside `cad/` — original tracker parts and the
  `camer_tracker.SLDASM` top-level assembly.

## File formats

| Extension | Purpose |
| --- | --- |
| `.SLDASM` | SolidWorks assembly |
| `.SLDPRT` | SolidWorks part |
| `.STEP` | Neutral CAD exchange file |
| `.STL` | 3D-printable mesh |
| `.3mf` | 3D manufacturing file |

SolidWorks assemblies reference their part files by name. Keep the relevant
assembly and its component files together when downloading or moving them.

## Getting started

For the simplified design, open
`cad/Easy_version/camer_tracker_easy.SLDASM` in SolidWorks. To print the
components, use the STL files in `cad/Easy_version/3dp_to_print/`.

Archive files that duplicated folders already included in this repository were
left out to avoid storing the same large binary files twice.
