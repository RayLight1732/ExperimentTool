from tkinter import ttk
import tkinter as tk
from typing import Callable, Optional
from step.step import Step
from datetime import datetime
import step.util as sutil


class InitialStepUI:
    def __init__(self, container: ttk.Frame):
        self.container = container
        self.on_change: Optional[Callable[[], None]] = None
        self.name_entry = None
        self.mode_combobox = None
        self.position_combobox = None
        self.name = ""
        self.mode = -1
        self.position = sutil.POSITION_NONE
        self.position_label = None

    def build(self):
        ttk.Label(self.container, text="名前を入力").pack()
        self.name_var = tk.StringVar()
        self.name_var.trace_add("write", self._on_name_change)
        self.name_entry = ttk.Entry(self.container, textvariable=self.name_var)
        self.name_entry.pack()

        ttk.Label(self.container, text="冷却モードを選択").pack(pady=(10, 0))
        self.mode_var = tk.StringVar()
        self.mode_combobox = ttk.Combobox(
            self.container,
            state="readonly",
            values=sutil.MODE,
            textvariable=self.mode_var,
        )
        self.mode_combobox.pack()
        self.mode_var.trace_add("write", self._on_mode_change)

        self.position_label = ttk.Label(self.container, text="冷却場所を選択")
        self.position_var = tk.StringVar()
        self.position_combobox = ttk.Combobox(
            self.container,
            state="readonly",
            values=sutil.POSITIONS[1:],
            textvariable=self.position_var,
        )
        self.position_var.trace_add("write", self._on_position_change)

    def _on_name_change(self, *args):
        self.name = self.name_var.get()
        self.on_change()

    def _on_mode_change(self, *args):
        self.mode = sutil.get_mode_number(self.mode_var.get())
        if self.mode != sutil.MODE_NEVER and self.mode != -1:
            self.show_position_selector()
        else:
            self.hide_position_selector()
        self.on_change()

    def _on_position_change(self, *args):
        self.position = sutil.get_position_number(self.position_var.get())
        self.on_change()

    def show_position_selector(self):
        self.position_label.pack(pady=(10, 0))
        self.position_combobox.pack()

    def hide_position_selector(self):
        self.position_label.pack_forget()
        self.position_combobox.pack_forget()


class InitialStep(Step):
    def __init__(
        self,
        container: ttk.Frame,
        ui: InitialStepUI,
        set_complete: Callable[[bool], None],
        save_value: Callable[[str, int], None],
    ):
        super().__init__(container, set_complete)
        self.set_complete = set_complete
        self.save_value = save_value
        self.ui = ui
        self.ui.on_change = self.on_value_change

    def build(self):
        self.ui.build()

    def on_value_change(self):
        self.set_complete(self.can_proceed())

    def before_next(self):
        mode = self.ui.mode
        position = self.ui.position if mode != sutil.MODE_NEVER else sutil.POSITION_NONE
        condition = sutil.calc_condition(mode, position)
        self.save_value(self.ui.name, condition)

    def on_dispose(self):
        pass

    def can_proceed(self) -> bool:
        if not self.ui.name or self.ui.mode == -1:
            return False
        if self.ui.mode == sutil.MODE_NEVER:
            return True
        return self.ui.position != sutil.POSITION_NONE


class InitialStepFactory:
    def __init__(self, data_container: dict):
        self.data_container = data_container

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> Step:
        def save(name: str, condition: int):
            self.data_container["name"] = name
            self.data_container["condition"] = condition
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            self.data_container["timestamp"] = timestamp

        ui = InitialStepUI(frame)
        return InitialStep(frame, ui, set_complete, save)
