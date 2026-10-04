# YOLO Camera Tracker

Mechanical design files for a two-axis camera and sensor tracker intended for
YOLO-based object-tracking projects.

## Teaching materials

- [`Workshop: Build Your Own YOLO Tracker`](teaching_materials/Workshop_Build_Your_Own_YOLO_Tracker.pdf)
  - the complete 65-page assembly, wiring, calibration, and testing guide.

## Gimbal control software

The [`software`](software) directory contains a Raspberry Pi controller for
the two STS3215 motors used by the workshop tracker. It uses servo ID `1` for
yaw and servo ID `2` for pitch, reads each unit's current center position, and
supports manual arrow-key control through the ESP32 driver's serial-forwarding
mode. The [software instructions](software/README.md) include a dedicated
Raspberry Pi Python and `scservo_sdk` setup section; read it before powering
the motors.

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
