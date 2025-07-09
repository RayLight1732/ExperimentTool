import tkinter as tk
from tkinter import ttk
from typing import Callable
from step.step import Step


class OrderStep(Step):
    def __init__(
        self,
        container: ttk.Frame,
        set_complete: Callable[[bool], None],
        text="指示に従ってください",
    ):
        super().__init__(container, set_complete)
        self.text = text
        self.set_complete = set_complete

    def build(self):
        tk.Label(self.container, text=self.text).pack(pady=20)

        self.set_complete(True)

    def on_dispose(self):
        pass

    def before_next(self):
        pass


class OrderStepFactory:
    def __init__(self, order: str):
        self.order = order

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> Step:
        return OrderStep(frame, set_complete, self.order)
