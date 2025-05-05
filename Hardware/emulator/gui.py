import tkinter as tk
from tkinter import ttk
import threading
import time
from emulator import ensure_pipes, format_sensor_data, write_to_pipes


class HWEmulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hardware Emulator")
        self.running = False

        self.vars = {
            "bpm": tk.DoubleVar(value=75),
            "spo2": tk.DoubleVar(value=98),
            "temp": tk.DoubleVar(value=37),
            "ecg": tk.DoubleVar(value=512),
            "jerk": tk.DoubleVar(value=5),
            "accx": tk.DoubleVar(value=0),
            "accy": tk.DoubleVar(value=0),
            "accz": tk.DoubleVar(value=0),
            "gyrox": tk.DoubleVar(value=0),
            "gyroy": tk.DoubleVar(value=0),
            "gyroz": tk.DoubleVar(value=0),
        }

        self.build_gui()


    def build_gui(self):
        self.value_labels = {}  # Store value labels for dynamic updates
        row = 0
        for key, var in self.vars.items():
            ttk.Label(self.root, text=key.upper()).grid(row=row, column=0, sticky="w")

            # Scale
            scale = ttk.Scale(
                self.root,
                from_=-4 if "gyro" in key or "acc" in key else 0,
                to=4 if "gyro" in key or "acc" in key else 100,
                variable=var,
                orient="horizontal",
                command=lambda val, k=key: self.update_value_label(k),
            )
            scale.grid(row=row, column=1, sticky="ew")

            # Value display label
            value_label = ttk.Label(self.root, text=str(var.get()))
            value_label.grid(row=row, column=2, padx=5)
            self.value_labels[key] = value_label

            row += 1

        ttk.Button(self.root, text="Start", command=self.start).grid(row=row, column=0)
        ttk.Button(self.root, text="Stop", command=self.stop).grid(row=row, column=1)

    def update_value_label(self, key):
        value = self.vars[key].get()
        self.value_labels[key].config(text=f"{value:.2f}")

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.emulation_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def emulation_loop(self):
        ensure_pipes()
        while self.running:
            data = format_sensor_data(
                self.vars["bpm"].get(),
                self.vars["spo2"].get(),
                self.vars["temp"].get(),
                self.vars["ecg"].get(),
                self.vars["jerk"].get(),
                self.vars["accx"].get(),
                self.vars["accy"].get(),
                self.vars["accz"].get(),
                self.vars["gyrox"].get(),
                self.vars["gyroy"].get(),
                self.vars["gyroz"].get(),
            )
            print("[HW Emulator] Sending:\n" + data)
            write_to_pipes(data)
            time.sleep(1)
