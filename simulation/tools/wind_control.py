import math
import subprocess
import tkinter as tk
from tkinter import ttk


TOPIC = "/world/varuna_mission/wind"
MSG_TYPE = "gz.msgs.Wind"


class WindControl:
    def __init__(self, root):
        self.root = root
        self.root.title("VARUNA | Wind Control")
        self.root.geometry("440x410")
        self.root.resizable(False, False)

        self.enabled = tk.BooleanVar(value=True)
        self.speed = tk.DoubleVar(value=12.0)
        self.direction = tk.DoubleVar(value=0.0)
        self.status = tk.StringVar(value="Ready — Gazebo must be running")

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame, text="VARUNA WIND CONTROL",
            font=("Sans", 16, "bold")
        ).pack(anchor="w", pady=(0, 4))

        ttk.Label(
            frame, text="Live Gazebo wind configuration",
            font=("Sans", 10)
        ).pack(anchor="w", pady=(0, 18))

        ttk.Checkbutton(
            frame, text="Wind enabled",
            variable=self.enabled
        ).pack(anchor="w", pady=(0, 12))

        self.speed_label = ttk.Label(frame, text="Wind speed: 12.0 m/s")
        self.speed_label.pack(anchor="w")

        ttk.Scale(
            frame, from_=0, to=20, variable=self.speed,
            command=self.update_speed_label
        ).pack(fill="x", pady=(4, 16))

        self.direction_label = ttk.Label(frame, text="Direction: 0° (+X)")
        self.direction_label.pack(anchor="w")

        ttk.Scale(
            frame, from_=0, to=359, variable=self.direction,
            command=self.update_direction_label
        ).pack(fill="x", pady=(4, 18))

        ttk.Button(
            frame, text="APPLY TO RUNNING SIMULATION",
            command=self.apply
        ).pack(fill="x", ipady=7)

        ttk.Separator(frame).pack(fill="x", pady=16)

        ttk.Label(
            frame, textvariable=self.status, wraplength=390
        ).pack(anchor="w")

        ttk.Label(
            frame,
            text="0° = +X   |   90° = +Y   |   180° = -X   |   270° = -Y",
            font=("Sans", 9)
        ).pack(anchor="w", pady=(12, 0))

    def update_speed_label(self, _=None):
        self.speed_label.config(text=f"Wind speed: {self.speed.get():.1f} m/s")

    def update_direction_label(self, _=None):
        angle = round(self.direction.get()) % 360
        self.direction_label.config(text=f"Direction: {angle}°")

    def apply(self):
        angle = math.radians(self.direction.get())
        speed = self.speed.get() if self.enabled.get() else 0.0
        x = speed * math.cos(angle)
        y = speed * math.sin(angle)

        message = (
            f"linear_velocity: {{x: {x:.4f}, y: {y:.4f}, z: 0}}, "
            f"enable_wind: {'true' if self.enabled.get() else 'false'}"
        )

        self.status.set("Sending wind update...")
        self.root.update_idletasks()

        try:
            result = subprocess.run(
                [
                    "gz", "topic", "-t", TOPIC,
                    "-m", MSG_TYPE, "-p", message
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.status.set(
                    f"Command sent: {speed:.1f} m/s at "
                    f"{round(self.direction.get()) % 360}°"
                )
            else:
                detail = (result.stderr or result.stdout).strip()
                self.status.set(f"Gazebo rejected command: {detail[:180]}")

        except subprocess.TimeoutExpired:
            self.status.set("Timed out waiting for Gazebo Transport.")
        except FileNotFoundError:
            self.status.set("Could not find 'gz'. Check your Gazebo installation.")
        except Exception as exc:
            self.status.set(f"Error: {exc}")


if __name__ == "__main__":
    root = tk.Tk()
    WindControl(root)
    root.mainloop()
