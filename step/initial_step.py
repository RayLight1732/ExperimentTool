from tkinter import ttk
from typing import Callable
from step.step import Step
from datetime import datetime
import step.util as sutil

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
        self.mode = -1
        self.position = sutil.POSITION_NONE
        self.position_label = None
        self.position_button = None

    def build(self):
        ttk.Label(self.container, text="名前を入力").pack()
        val_cmd = self.container.register(self.validate_name)
        self.entry = ttk.Entry(
            self.container,
            validate="key",
            validatecommand=(val_cmd, "%d", "%i", "%P", "%s", "%S", "%v", "%V", "%W"),
        )
        self.entry.pack()

        self.mode_label = ttk.Label(self.container, text="冷却モードを選択").pack(pady=(10, 0))
        val_cmd2 = self.container.register(self.validate_mode_combobox)
        self.mode_combobox = ttk.Combobox(
            self.container,
            state="readonly",
            values=sutil.MODE,
            validate="all",
            validatecommand=(val_cmd2, "%d", "%i", "%P", "%s", "%S", "%v", "%V", "%W"),
        ).pack()

        self.position_label = ttk.Label(self.container, text="冷却場所を選択")
        val_cmd3 = self.container.register(self.validate_position_combobox)
        self.position_combobox = ttk.Combobox(
            self.container,
            state="readonly",
            values=sutil.POSITIONS[1:],
            validate="all",
            validatecommand=(val_cmd3, "%d", "%i", "%P", "%s", "%S", "%v", "%V", "%W"),
        )

    def _show_position_selector(self):
        self.position_label.pack(pady=(10, 0))
        self.position_combobox.pack()

    def _hide_podition_selector(self):
        self.position_label.pack_forget()
        self.position_combobox.pack_forget()

    def on_dispose(self):
        pass

    def validate_name(self, d, i, P, s, S, v, V, W):
        self.name_set = len(P) > 0
        self.set_complete(self.can_go_next())
        return True

    def validate_mode_combobox(self, d, i, P, s, S, v, V, W):
        self.mode = sutil.get_mode_number(P)
        print("mode",self.mode)
        if self.mode != sutil.MODE_NEVER:
            self._show_position_selector()
        else:
            self._hide_podition_selector()
        self.set_complete(self.can_go_next())
        return True
    
    def validate_position_combobox(self, d, i, P, s, S, v, V, W):
        self.position = sutil.get_position_number(P)
        self.set_complete(self.can_go_next())
        return True
    
    
    def can_go_next(self)->bool:
        if not self.name_set or self.mode == -1: #名前とmodeは必須
            return False
        if self.mode == sutil.MODE_NEVER: #modeがなしだったらtrue
            return True
        else:
            return self.position != sutil.POSITION_NONE #modeが何かしらに設定されてたら、positionが入力されていたらtrue

    def before_next(self):
        if self.mode == sutil.MODE_NEVER:
            self.position = sutil.POSITION_NONE
        self.save_value(self.entry.get(),sutil.calc_condition(self.mode,self.position))


class InitialStepFactory:
    def __init__(self, data_container: dict):
        self.data_container = data_container

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> Step:
        def save(name: str,condition:int):
            self.data_container["name"] = name
            self.data_container["condition"] = condition
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            self.data_container["timestamp"] = timestamp

        return InitialStep(frame, set_complete, save)
