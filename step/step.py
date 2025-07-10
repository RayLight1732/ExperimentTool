from tkinter import ttk
from typing import Callable
from abc import ABC, abstractmethod


# ---------------------
# Step 基底クラス
# ---------------------
class Step(ABC):

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def on_dispose(self):
        pass

    @abstractmethod
    def before_next(self):
        pass
