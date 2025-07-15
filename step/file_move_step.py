from tkinter import ttk
import tkinter as tk
from typing import Callable
from step.step import Step
import step.util as sutil
from pathlib import Path
import shutil


class FileMoveStepUI:
    def __init__(self, container: ttk.Frame):
        self.container = container
        self.label = None

    def show_waiting(self):
        self.label = ttk.Label(self.container, text="ファイルを待っています...")
        self.label.pack()

    def show_complete(self):
        if self.label:
            self.label.destroy()
        ttk.Label(self.container, text="ファイルの移動が完了しました!").pack()


class FileMoveProcessor:
    def __init__(self, src_folder: Path, dst_folder: Path, pattern):
        self.src_folder = src_folder
        self.dst_folder = dst_folder
        self.pattern = pattern

    def move_file(self) -> bool:
        self.dst_folder.mkdir(parents=True, exist_ok=True)
        count = 0
        for csv_file in self.src_folder.glob(self.pattern):
            try:
                shutil.move(str(csv_file), str(self.dst_folder / csv_file.name))
                count += 1
            except:
                pass
        return count > 0


class FileMoveStep(Step):
    def __init__(
        self,
        container: ttk.Frame,
        set_complete: Callable[[bool], None],
        ui: FileMoveStepUI,
        processor: FileMoveProcessor,
    ):
        self.container = container
        self.set_complete = set_complete
        self.ui = ui
        self.processor = processor
        self.after_id = None

    def build(self):
        self.ui.show_waiting()
        self._update()

    def _update(self):
        if not self.processor.move_file():
            self.after_id = self.container.after(30, self._update)
        else:
            self.ui.show_complete()
            self.set_complete(True)

    def before_next(self):
        pass

    def on_dispose(self):
        if self.after_id:
            self.container.after_cancel(self.after_id)


class FileMoveStepFactory:
    def __init__(self, src_dir: Path, working_dir: Path, data_container: dict):
        self.working_dir = working_dir
        self.data_container = data_container
        self.src_dir = src_dir

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> Step:
        ui = FileMoveStepUI(frame)
        save_dir = sutil.get_save_dir(self.working_dir, self.data_container)
        processor = FileMoveProcessor(self.src_dir, save_dir, "*.csv")
        return FileMoveStep(frame, set_complete, ui, processor)
