from tkinter import ttk
from typing import Callable
from step.step import Step
from datetime import datetime


class InitialStep(Step):
    def __init__(
        self,
        container: ttk.Frame,
        set_complete: Callable[[bool], None],
        save_value: Callable[[str, int], None],
    ):
        super().__init__(container, set_complete)
        self.save_value = save_value
        self.name_set = False
        self.condition_set = False
        self.conditions = ["なし", "首筋", "頸動脈"]

    def build(self):
        ttk.Label(self.container, text="名前を入力").pack()
        val_cmd = self.container.register(self.validate)
        self.entry = ttk.Entry(
            self.container,
            validate="key",
            validatecommand=(val_cmd, "%d", "%i", "%P", "%s", "%S", "%v", "%V", "%W"),
        )
        self.entry.pack()

        ttk.Label(self.container, text="実験条件を選択").pack(pady=(10, 0))
        val_cmd2 = self.container.register(self.validate_combobox)
        self.combobox = ttk.Combobox(
            self.container,
            state="readonly",
            values=self.conditions,
            validate="all",
            validatecommand=(val_cmd2, "%d", "%i", "%P", "%s", "%S", "%v", "%V", "%W"),
        )
        self.combobox.pack()

    def on_dispose(self):
        pass

    def validate(self, d, i, P, s, S, v, V, W):
        self.name_set = len(P) > 0
        self.set_complete(self.name_set and self.condition_set)
        return True

    def validate_combobox(self, d, i, P, s, S, v, V, W):
        self.condition_set = len(P) > 0
        self.set_complete(self.name_set and self.condition_set)
        return True

    def before_next(self):
        self.save_value(self.entry.get(), self.conditions.index(self.combobox.get()))


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

        return InitialStep(frame, set_complete, save)
