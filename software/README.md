# STS3215 Gimbal Controller

This controller follows the workshop setup:

- yaw motor: STS3215 servo ID `1`
- pitch motor: STS3215 servo ID `2`
- connection: ESP32 servo driver in `SERIAL_FORWARDING` mode
- serial device: `/dev/ttyUSB0`
- baud rate: `1,000,000`

The two motors are daisy-chained. The ESP32 driver is connected to the
Raspberry Pi by USB-C and powered separately by the 12 V servo supply.

## Safety before running

1. Assemble the gimbal and connect the servo cables in the orientation shown
   in the workshop notes.
2. Position the camera approximately forward and level by hand.
3. Keep hands and loose cables clear of the gears.
4. Power the ESP32 servo driver with the correct 12 V supply.
5. Confirm its display detects servo IDs `1` and `2` and enters
   `SERIAL_FORWARDING` mode.

The program reads the current positions on startup and treats them as the
center. It does not command either motor until you press a movement key.

## Install

On the Raspberry Pi:

```bash
cd software
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

If the Raspberry Pi reports a serial-port permission error, add the current
user to the `dialout` group and then sign out and back in:

```bash
sudo usermod -aG dialout "$USER"
```

## Calibrate and control

First read the two center positions without moving the gimbal:

```bash
python3 gimbal_controller.py --calibrate-only
```

Record the displayed yaw and pitch values, as required by the workshop notes.
Then start keyboard control:

```bash
python3 gimbal_controller.py
```

Controls:

- Left/Right: yaw
- Up/Down: pitch
- `C`: return to the center recorded at startup
- `R`: use the current measured positions as new centers
- `P`: display the current measured positions
- `Esc` or `Q`: quit

If an axis moves in the opposite direction, use `--invert-yaw` or
`--invert-pitch`. To limit travel for a particular build, set safe position
ranges. For example:

```bash
python3 gimbal_controller.py \
  --yaw-min 100 --yaw-max 4000 \
  --pitch-min 1800 --pitch-max 3100
```

Run `python3 gimbal_controller.py --help` for all options, including motor
IDs, serial port, step size, speed, and acceleration.
