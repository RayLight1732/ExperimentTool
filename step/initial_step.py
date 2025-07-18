from tkinter import ttk
import tkinter as tk
from typing import Callable, Optional
from step.step import Step
from datetime import datetime
import step.util as sutil
from pathlib import Path
import os
from datetime import datetime

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
        self.completed_label = []
        self.last_modified_label = None

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

    def set_last_modified(self,timestamp):
        # フォーマットして表示
        if self.last_modified_label is not None:
            self.last_modified_label.destroy()
        if timestamp != -1:
            dt = datetime.fromtimestamp(timestamp)
            label_text = f"{dt.month}月 {dt.day}日 {dt.hour}時 {dt.minute}分 {dt.second}秒"
            self.last_modified_label = ttk.Label(self.container,text=label_text)
            self.last_modified_label.pack(side="bottom")

    def set_completed(self,completed:list[int]):
        for label in self.completed_label:
            label.destroy()
        for condition in reversed(completed):
            mode = sutil.get_mode(condition)
            position = sutil.get_position(condition)
            if mode == sutil.MODE_NEVER:
                label_text = mode
            else:
                label_text = f"{mode}/{position}"
            label = ttk.Label(self.container, text=label_text)
            label.pack(side="bottom")
            self.completed_label.append(label)

class DirectoryManager:
    def __init__(self,working_dir:Path):
        self.working_dir = working_dir

    def get_completed_conditions(self,name:str)->list:
        result = []
        if name.strip():
            for condition in sutil.list_condition():
                if sutil.get_save_dir(self.working_dir,condition,name).exists():
                    result.append(condition)
        return result
    
    def get_last_modified_time(self,name:str)->list:
        completed = self.get_completed_conditions(name)
        last = -1
        for condition in completed:
            path = sutil.get_save_dir(self.working_dir,condition,name)
            last = max(os.path.getmtime(path),last)
        return last

class InitialStep(Step):
    def __init__(
        self,
        ui: InitialStepUI,
        directory_manager:DirectoryManager,
        set_complete: Callable[[bool], None],
        save_value: Callable[[str, int], None],
    ):
        self.set_complete = set_complete
        self.directory_manager = directory_manager
        self.save_value = save_value
        self.ui = ui
        self.ui.on_change = self.on_value_change

    def build(self):
        self.ui.build()

    def on_value_change(self):
        self.set_complete(self.can_proceed())
        name = self.ui.name
        self.ui.set_completed(self.directory_manager.get_completed_conditions(name))
        self.ui.set_last_modified(self.directory_manager.get_last_modified_time(name))

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
    def __init__(self, data_container: dict,working_dir):
        self.data_container = data_container
        self.working_dir = working_dir

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> Step:
        def save(name: str, condition: int):
            self.data_container["name"] = name
            self.data_container["condition"] = condition
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            self.data_container["timestamp"] = timestamp
        directory_manager = DirectoryManager(self.working_dir)
        ui = InitialStepUI(frame)
        return InitialStep(ui,directory_manager, set_complete, save)
