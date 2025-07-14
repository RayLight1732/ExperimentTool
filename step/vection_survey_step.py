from tkinter import ttk
import tkinter as tk
from typing import Callable, Optional
from step.step import Step
from datetime import datetime
import step.util as sutil
from pathlib import Path
import csv
import math


class VectionSurveyStepUI:
    def __init__(self, container: ttk.Frame, vection: int = 50):
        self.container = container
        self.vection = vection

    def build(self):
        ttk.Label(
            self.container,
            text="ベクション(自分が動いた感覚)の強さを入力してください（0〜100）",
        ).pack()

        # StringVarを使ってEntryとScaleを連動させる
        self.vection_var = tk.StringVar(value=str(self.vection))
        self.vection_var.trace_add("write", self._on_vection_change)

        # Entry作成
        self.vection_entry = ttk.Entry(self.container, textvariable=self.vection_var)
        self.vection_entry.pack()

        # Scale作成
        self.vection_scale_var = tk.IntVar(value=self.vection)
        self.vection_scale = ttk.Scale(
            self.container,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.vection_scale_var,
            command=self._on_scale_change,
        )
        self.vection_scale.pack()

    def _on_vection_change(self, *args):
        val = self.vection_var.get()
        try:
            num = int(val)
            if 0 <= num <= 100:
                self.vection = num
                self.vection_scale_var.set(num)
        except ValueError:
            pass  # 数値でない場合は無視

    def _on_scale_change(self, val):
        self.vection = round(float(val))
        self.vection_var.set(str(self.vection))  # Entryには整数で表示


class DataSaver:
    def __init__(self, save_dir: Path, file_name: str):
        self.save_dir = save_dir
        self.file_name = file_name

    def _ensure_dir_exists(self):
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def save_csv(self, vection: int):
        self._ensure_dir_exists()
        csv_path = self.save_dir / f"{self.file_name}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([vection])


class VectionSurveyStep(Step):
    def __init__(
        self,
        set_complete: Callable[[bool], None],
        ui: VectionSurveyStepUI,
        data_saver: DataSaver,
    ):
        self.set_complete = set_complete
        self.ui = ui
        self.data_saver = data_saver

    def build(self):
        self.ui.build()
        self.set_complete(True)

    def before_next(self):
        self.data_saver.save_csv(self.ui.vection)

    def on_dispose(self):
        pass


class VectionSurveyStepFactory:
    def __init__(
        self,
        working_dir: Path,
        data_container: dict,
    ):
        self.working_dir = working_dir
        self.data_container = data_container

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> Step:
        ui = VectionSurveyStepUI(frame)
        save_dir = sutil.get_save_dir(self.working_dir, self.data_container)
        file_name = f"vection_{sutil.get_timestamp(self.data_container)}"
        data_saver = DataSaver(save_dir, file_name)
        return VectionSurveyStep(set_complete, ui, data_saver)
