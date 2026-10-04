#!/usr/bin/env python3
"""Manual controller for a two-axis STS3215 camera gimbal.

The workshop hardware uses servo ID 1 for yaw and servo ID 2 for pitch.
Both servos share a serial bus connected through the ESP32 driver board.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

try:
    from scservo_sdk import COMM_SUCCESS, PortHandler, sms_sts
except ImportError as exc:  # pragma: no cover - depends on workshop hardware
    raise SystemExit(
        "Missing Feetech SDK. Install it with: "
        "python3 -m pip install ftservo-python-sdk"
    ) from exc


POSITION_MIN = 0
POSITION_MAX = 4095


@dataclass(frozen=True)
class Axis:
    name: str
    servo_id: int
    minimum: int
    maximum: int
    inverted: bool = False

    def clamp(self, value: int) -> int:
        return max(self.minimum, min(self.maximum, value))


class GimbalController:
    """Small reusable interface around the Feetech STS3215 SDK."""

    def __init__(
        self,
        port: str,
        baudrate: int,
        yaw: Axis,
        pitch: Axis,
        speed: int = 500,
        acceleration: int = 50,
    ) -> None:
        self.port_name = port
        self.baudrate = baudrate
        self.yaw = yaw
        self.pitch = pitch
        self.speed = speed
        self.acceleration = acceleration
        self.port_handler = PortHandler(port)
        self.packet_handler = sms_sts(self.port_handler)
        self.targets: dict[int, int] = {}
        self.centers: dict[int, int] = {}

    def open(self) -> None:
        if not self.port_handler.openPort():
            raise RuntimeError(f"Could not open serial port {self.port_name}")
        if not self.port_handler.setBaudRate(self.baudrate):
            self.port_handler.closePort()
            raise RuntimeError(f"Could not set baud rate to {self.baudrate}")

        for axis in (self.yaw, self.pitch):
            model, result, error = self.packet_handler.ping(axis.servo_id)
            self._check(result, error, f"ping {axis.name} servo")
            print(
                f"Detected {axis.name} servo: ID {axis.servo_id}, "
                f"model {model}"
            )

        self.record_centers()

    def close(self) -> None:
        self.port_handler.closePort()

    def _check(self, result: int, error: int, action: str) -> None:
        if result != COMM_SUCCESS:
            detail = self.packet_handler.getTxRxResult(result)
            raise RuntimeError(f"Failed to {action}: {detail}")
        if error:
            detail = self.packet_handler.getRxPacketError(error)
            raise RuntimeError(f"Servo error while trying to {action}: {detail}")

    def read_position(self, axis: Axis) -> int:
        position, result, error = self.packet_handler.ReadPos(axis.servo_id)
        self._check(result, error, f"read {axis.name} position")
        return int(position)

    def read_positions(self) -> tuple[int, int]:
        return self.read_position(self.yaw), self.read_position(self.pitch)

    def record_centers(self) -> tuple[int, int]:
        yaw_position, pitch_position = self.read_positions()
        self.centers = {
            self.yaw.servo_id: yaw_position,
            self.pitch.servo_id: pitch_position,
        }
        self.targets = dict(self.centers)
        return yaw_position, pitch_position

    def move(self, axis: Axis, position: int) -> int:
        position = axis.clamp(position)
        result, error = self.packet_handler.WritePosEx(
            axis.servo_id, position, self.speed, self.acceleration
        )
        self._check(result, error, f"move {axis.name} servo")
        self.targets[axis.servo_id] = position
        return position

    def nudge(self, axis: Axis, amount: int) -> int:
        direction = -1 if axis.inverted else 1
        current_target = self.targets[axis.servo_id]
        return self.move(axis, current_target + amount * direction)

    def center(self) -> None:
        self.move(self.yaw, self.centers[self.yaw.servo_id])
        self.move(self.pitch, self.centers[self.pitch.servo_id])


@contextmanager
def keyboard_input() -> Iterator[None]:
    """Put a terminal into immediate key-reading mode and restore it later."""
    if os.name == "nt":
        yield
        return

    import termios
    import tty

    file_descriptor = sys.stdin.fileno()
    original = termios.tcgetattr(file_descriptor)
    try:
        tty.setcbreak(file_descriptor)
        yield
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, original)


def read_key() -> str:
    if os.name == "nt":
        import msvcrt

        first = msvcrt.getwch()
        if first in ("\x00", "\xe0"):
            return {
                "K": "left",
                "M": "right",
                "H": "up",
                "P": "down",
            }.get(msvcrt.getwch(), "unknown")
        return "escape" if first == "\x1b" else first.lower()

    first = sys.stdin.read(1)
    if first != "\x1b":
        return first.lower()

    # Arrow keys arrive as a three-byte ANSI escape sequence.
    import select

    sequence = ""
    for _ in range(2):
        readable, _, _ = select.select([sys.stdin], [], [], 0.05)
        if not readable:
            return "escape"
        sequence += sys.stdin.read(1)
    return {
        "[D": "left",
        "[C": "right",
        "[A": "up",
        "[B": "down",
    }.get(sequence, "escape")


def show_status(controller: GimbalController) -> None:
    yaw = controller.targets[controller.yaw.servo_id]
    pitch = controller.targets[controller.pitch.servo_id]
    print(
        f"\rYaw ID {controller.yaw.servo_id}: {yaw:4d}  |  "
        f"Pitch ID {controller.pitch.servo_id}: {pitch:4d}    ",
        end="",
        flush=True,
    )


def run_keyboard(controller: GimbalController, step: int) -> None:
    yaw_center = controller.centers[controller.yaw.servo_id]
    pitch_center = controller.centers[controller.pitch.servo_id]
    print("\nKeyboard control active")
    print("  Left/Right : yaw (servo ID 1 by default)")
    print("  Up/Down    : pitch (servo ID 2 by default)")
    print("  C           : return to recorded center")
    print("  R           : record the current positions as new centers")
    print("  P           : read and print measured positions")
    print("  Esc or Q    : quit")
    print(f"\nRecorded center - yaw: {yaw_center}, pitch: {pitch_center}")

    with keyboard_input():
        show_status(controller)
        while True:
            key = read_key()
            if key in ("escape", "q"):
                break
            if key == "left":
                controller.nudge(controller.yaw, -step)
            elif key == "right":
                controller.nudge(controller.yaw, step)
            elif key == "up":
                controller.nudge(controller.pitch, step)
            elif key == "down":
                controller.nudge(controller.pitch, -step)
            elif key == "c":
                controller.center()
            elif key == "r":
                yaw, pitch = controller.record_centers()
                print(f"\nNew center - yaw: {yaw}, pitch: {pitch}")
            elif key == "p":
                yaw, pitch = controller.read_positions()
                print(f"\nMeasured position - yaw: {yaw}, pitch: {pitch}")
            else:
                continue
            time.sleep(0.02)
            show_status(controller)
    print()


def position_value(value: str) -> int:
    number = int(value)
    if not POSITION_MIN <= number <= POSITION_MAX:
        raise argparse.ArgumentTypeError(
            f"position must be between {POSITION_MIN} and {POSITION_MAX}"
        )
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Control a two-axis STS3215 camera gimbal with arrow keys."
    )
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=115_200)
    parser.add_argument("--yaw-id", type=int, default=1)
    parser.add_argument("--pitch-id", type=int, default=2)
    parser.add_argument("--step", type=int, default=32)
    parser.add_argument("--speed", type=int, default=500)
    parser.add_argument("--acceleration", type=int, default=50)
    parser.add_argument("--yaw-min", type=position_value, default=POSITION_MIN)
    parser.add_argument("--yaw-max", type=position_value, default=POSITION_MAX)
    parser.add_argument("--pitch-min", type=position_value, default=POSITION_MIN)
    parser.add_argument("--pitch-max", type=position_value, default=POSITION_MAX)
    parser.add_argument("--invert-yaw", action="store_true")
    parser.add_argument("--invert-pitch", action="store_true")
    parser.add_argument(
        "--calibrate-only",
        action="store_true",
        help="read and display both center positions without entering control mode",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.yaw_min > args.yaw_max or args.pitch_min > args.pitch_max:
        raise SystemExit("Each minimum position must be less than its maximum.")
    if args.yaw_id == args.pitch_id:
        raise SystemExit("Yaw and pitch must use different servo IDs.")
    if args.step <= 0 or args.speed < 0 or not 0 <= args.acceleration <= 254:
        raise SystemExit("Use step > 0, speed >= 0, and acceleration from 0 to 254.")

    yaw = Axis("yaw", args.yaw_id, args.yaw_min, args.yaw_max, args.invert_yaw)
    pitch = Axis(
        "pitch", args.pitch_id, args.pitch_min, args.pitch_max, args.invert_pitch
    )
    controller = GimbalController(
        args.port,
        args.baudrate,
        yaw,
        pitch,
        speed=args.speed,
        acceleration=args.acceleration,
    )

    try:
        controller.open()
        yaw_center = controller.centers[yaw.servo_id]
        pitch_center = controller.centers[pitch.servo_id]
        print(f"Current center - yaw: {yaw_center}, pitch: {pitch_center}")
        if not args.calibrate_only:
            run_keyboard(controller, args.step)
    except (KeyboardInterrupt, RuntimeError) as exc:
        print(f"\n{exc}", file=sys.stderr)
        return 1
    finally:
        controller.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
