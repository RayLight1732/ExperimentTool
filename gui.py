import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, List, Optional
from step.step import Step
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True


# ---------------------
# MainWindow
# ---------------------
class MainWindow:
    def __init__(
        self,
        root: tk.Tk,
        on_press_next: Callable[[], None],
        on_press_return_first: Callable[[], None],
    ):
        self.root = root
        self.on_press_next = on_press_next
        self.on_press_return_first = on_press_return_first
        self.step: Optional[Step] = None
        self._build()

    def _build(self):
        outline = ttk.Frame(master=self.root, takefocus=True)
        outline.pack(fill="both", expand=True, padx=5, pady=5)

        header = ttk.Frame(master=outline)
        footer = ttk.Frame(master=outline)
        container = ttk.Frame(master=outline)
        container.bind("<Button-1>", lambda event: event.widget.focus_set())

        header.pack(side="top", fill="x")
        footer.pack(side="bottom", fill="x", padx=10, pady=5)
        container.pack(side="top", fill="both", expand=True)

        self.next_button = ttk.Button(
            master=footer, text="次へ", state="disabled", command=self.on_press_next
        )
        self.next_button.pack(side="right", ipady=3)

        back_button = ttk.Button(
            master=footer, text="最初に戻る", command=self.on_press_return_first
        )
        back_button.pack(side="left", ipady=3)

        self.container = container

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def get_container(self) -> ttk.Frame:
        return self.container

    def activate_next_button(self):
        self.next_button.config(state="normal")

    def disable_next_button(self):
        self.next_button.config(state="disabled")

    def show_end_message_box(self):
        messagebox.showinfo("終了", "すべてのステップが完了しました。")
        self.on_press_return_first()


# ---------------------
# StepManager
# ---------------------
class StepManager:
    def __init__(
        self, step_factories: List[Callable[[ttk.Frame, Callable[[bool], None]], Step]]
    ):
        self.step_factories = step_factories
        self.main_window: Optional[MainWindow] = None
        self.step: Optional[Step] = None
        self.current = 0

    def show_step(self, index: int):
        if 0 <= index < len(self.step_factories):
            self.current = index
            if self.step:
                self.step.on_dispose()
                self.main_window.clear_container()

            self.main_window.disable_next_button()
            factory = self.step_factories[index]
            self.step = factory(self.main_window.get_container(), self._set_complete)
            self.step.build()
        else:
            self.main_window.show_end_message_box()

    def _set_complete(self, completed: bool):
        if completed:
            self.main_window.activate_next_button()
        else:
            self.main_window.disable_next_button()

    def next_step(self):
        if self.step:
            self.step.before_next()
        self.show_step(self.current + 1)

