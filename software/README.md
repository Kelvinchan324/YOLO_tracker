# STS3215 Gimbal Controller

This controller follows the workshop setup:

- yaw motor: STS3215 servo ID `1`
- pitch motor: STS3215 servo ID `2`
- connection: ESP32 servo driver in `SERIAL_FORWARDING` mode
- serial device: `/dev/ttyUSB0`
- baud rate: `115,200`

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

## Raspberry Pi control with Python and `scservo_sdk`

The controller uses the Feetech `scservo_sdk` package directly. The workshop
ESP32 board forwards commands at `115200` baud; this differs from the
STS3215's direct-bus factory baud rate. The Raspberry Pi port can change when
USB devices are reconnected, so find it before running the program:

```bash
dmesg | grep -i cp210x
python3 -m serial.tools.list_ports
ls -l /dev/ttyUSB*
```

Look for the CP210x adapter and use the corresponding device, commonly
`/dev/ttyUSB0` or `/dev/ttyUSB1`. Test communication without moving either
motor:

```bash
python3 gimbal_controller.py \
  --port /dev/ttyUSB0 \
  --baudrate 115200 \
  --calibrate-only
```

The essential `scservo_sdk` pattern used by the controller is:

```python
from scservo_sdk import COMM_SUCCESS, PortHandler, sms_sts

port = PortHandler("/dev/ttyUSB0")
servos = sms_sts(port)

if not port.openPort():
    raise RuntimeError("Could not open the serial port")

try:
    if not port.setBaudRate(115200):
        raise RuntimeError("Could not set the ESP32 forwarding baud rate")

    # ID 1 is yaw; ID 2 is pitch.
    yaw_position, result, error = servos.ReadPos(1)
    if result != COMM_SUCCESS or error:
        raise RuntimeError("Could not read yaw servo")

    pitch_position, result, error = servos.ReadPos(2)
    if result != COMM_SUCCESS or error:
        raise RuntimeError("Could not read pitch servo")

    print(f"Yaw center: {yaw_position}, pitch center: {pitch_position}")

    # WritePosEx(servo_id, target_position, speed, acceleration)
    # Use measured, mechanically safe targets between 0 and 4095.
    result, error = servos.WritePosEx(1, yaw_position, 500, 50)
    if result != COMM_SUCCESS or error:
        raise RuntimeError("Could not command yaw servo")
finally:
    port.closePort()
```

Use `ReadPos()` to obtain each tracker's unique center before commanding any
movement. `WritePosEx()` accepts the servo ID, a target from `0` to `4095`,
speed, and acceleration. The full `gimbal_controller.py` wraps these calls
with arrow-key input, limit checking, communication-error reporting, and
automatic serial-port cleanup.

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
