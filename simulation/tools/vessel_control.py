import math
import os
import subprocess
import tkinter as tk
from tkinter import ttk

WORLD = "varuna_mission"
PARTITION = "varuna_demo"
VESSEL = "supply_vessel"
PAD = "flat_platform"
PAD_Z = 2.275
PAD_LIMIT = 7.0


class VesselControl:
    def __init__(self, root):
        self.root = root
        self.root.title("VARUNA | Vessel & Landing Pad")
        self.root.geometry("480x500")
        self.root.resizable(False, False)

        self.distance = tk.DoubleVar(value=100.0)
        self.pad_enabled = tk.BooleanVar(value=False)
        self.pad_speed = tk.DoubleVar(value=1.0)
        self.status = tk.StringVar(value="Ready — start Gazebo first")

        self.vessel_x = 100.0
        self.pad_offset = 0.0
        self.direction = 1
        self.last_tick = None
        self.busy = False

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame, text="VESSEL & LANDING PAD CONTROL",
            font=("Sans", 14, "bold")
        ).pack(anchor="w", pady=(0, 18))

        ttk.Label(frame, text="Vessel distance from origin (m)").pack(anchor="w")
        self.distance_label = ttk.Label(frame, text="100 m")
        self.distance_label.pack(anchor="w")
        ttk.Scale(
            frame, from_=100, to=300, variable=self.distance,
            command=self.update_distance_label
        ).pack(fill="x", pady=(4, 8))
        ttk.Button(
            frame, text="MOVE VESSEL",
            command=self.move_vessel
        ).pack(fill="x", ipady=5, pady=(0, 20))

        ttk.Separator(frame).pack(fill="x", pady=(0, 16))
        ttk.Label(frame, text="Landing pad speed (m/s)").pack(anchor="w")
        self.speed_label = ttk.Label(frame, text="1.0 m/s")
        self.speed_label.pack(anchor="w")
        ttk.Scale(
            frame, from_=0.1, to=2.0, variable=self.pad_speed,
            command=self.update_speed_label
        ).pack(fill="x", pady=(4, 12))
        ttk.Checkbutton(
            frame, text="Enable landing pad motion",
            variable=self.pad_enabled, command=self.toggle_pad
        ).pack(anchor="w", pady=(0, 12))
        ttk.Button(
            frame, text="RETURN PAD TO VESSEL CENTRE",
            command=self.return_to_centre
        ).pack(fill="x", ipady=5)

        ttk.Separator(frame).pack(fill="x", pady=16)
        ttk.Label(frame, textvariable=self.status, wraplength=420).pack(anchor="w")

        self.root.after(200, self.tick)

    def run_pose(self, name, x, y, z):
        request = (
            f'name: "{name}", position: {{x: {x:.3f}, y: {y:.3f}, z: {z:.3f}}}, '
            'orientation: {w: 1}'
        )
        env = {**os.environ, "GZ_PARTITION": PARTITION}
        try:
            result = subprocess.run(
                [
                    "gz", "service", "-s", f"/world/{WORLD}/set_pose",
                    "--reqtype", "gz.msgs.Pose",
                    "--reptype", "gz.msgs.Boolean",
                    "--timeout", "1000",
                    "--req", request
                ],
                capture_output=True, text=True, timeout=2, env=env
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def update_distance_label(self, _=None):
        self.distance_label.config(text=f"{self.distance.get():.0f} m")

    def update_speed_label(self, _=None):
        self.speed_label.config(text=f"{self.pad_speed.get():.1f} m/s")

    def move_vessel(self):
        x = round(self.distance.get())
        if self.run_pose(VESSEL, x, 0, 0):
            self.vessel_x = x
            self.pad_offset = 0.0
            self.run_pose(PAD, self.vessel_x, 0, PAD_Z)
            self.status.set(f"Vessel moved to X = {x} m; pad centred.")
        else:
            self.status.set("Could not move vessel. Check Gazebo and GZ_PARTITION.")

    def toggle_pad(self):
        self.last_tick = None
        if self.pad_enabled.get():
            self.status.set("Landing pad motion enabled.")
        else:
            self.return_to_centre()

    def return_to_centre(self):
        self.pad_enabled.set(False)
        self.pad_offset = 0.0
        self.last_tick = None
        if self.run_pose(PAD, self.vessel_x, 0, PAD_Z):
            self.status.set("Landing pad returned to vessel centre.")
        else:
            self.status.set("Could not move pad. Check Gazebo and GZ_PARTITION.")

    def tick(self):
        now = self.root.tk.call("clock", "milliseconds")
        now = int(now)
        if self.last_tick is None:
            self.last_tick = now
        dt = min((now - self.last_tick) / 1000.0, 0.2)
        self.last_tick = now

        if self.pad_enabled.get() and not self.busy:
            self.pad_offset += self.direction * self.pad_speed.get() * dt
            if self.pad_offset >= PAD_LIMIT:
                self.pad_offset = PAD_LIMIT
                self.direction = -1
            elif self.pad_offset <= -PAD_LIMIT:
                self.pad_offset = -PAD_LIMIT
                self.direction = 1

            self.busy = True
            ok = self.run_pose(PAD, self.vessel_x + self.pad_offset, 0, PAD_Z)
            self.busy = False
            if not ok:
                self.pad_enabled.set(False)
                self.status.set("Pad update failed. Check Gazebo and GZ_PARTITION.")
            else:
                self.status.set(
                    f"Pad moving — offset {self.pad_offset:+.1f} m from vessel centre."
                )

        self.root.after(200, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    VesselControl(root)
    root.mainloop()
