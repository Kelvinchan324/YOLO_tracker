# YOLO Camera Tracker

Mechanical design files for a two-axis camera and sensor tracker intended for
YOLO-based object-tracking projects.

## CAD contents

The [`cad`](cad) directory contains the original SolidWorks models and
assemblies, along with neutral CAD exports where available.

- `cad/camera tracker with laser/` — current SolidWorks tracker parts and the
  `camer_tracker.SLDASM` top-level assembly.
- `cad/3D printing files/` — the grouped design files previously packaged as
  the sharing revision.
- `cad/educational version/` — simplified educational tracker design, including the main
  `camer_tracker_easy.SLDASM` assembly and electronics enclosure.
- `cad/distance_sensor-1.snapshot.12/` — distance-sensor reference model,
  images, datasheet, and STEP files.

## File formats

| Extension | Purpose |
| --- | --- |
| `.SLDASM` | SolidWorks assembly |
| `.SLDPRT` | SolidWorks part |
| `.STEP` | Neutral CAD exchange file |

SolidWorks assemblies reference their part files by name. Keep the relevant
assembly and its component files together when downloading or moving them.

## Getting started

For the camera tracker with laser, open
`cad/camera tracker with laser/camer_tracker.SLDASM` in SolidWorks. For the
simplified design, open `cad/educational version/camer_tracker_easy.SLDASM`.

Archive files that duplicated folders already included in this repository were
left out to avoid storing the same large binary files twice.
