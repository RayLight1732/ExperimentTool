import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, List, Optional
from abc import ABC, abstractmethod
from step.step import Step
from step.initial_step import InitialStepFactory
from step.order_step import OrderStepFactory
from step.ssq_step import SSQStepFactory
from step.unity_step import UnityStepFactory
from network.data.image_data import ImageDataDecoder, IMAGE_DATA_TYPE
from network.tcp_server import TCPServer
from network.data.data_decoder import DecodedData
import queue
from pathlib import Path
from PIL import ExifTags, ImageFile

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


def on_receive(queue: queue.Queue, decodedData: DecodedData):
    if decodedData.get_name() == IMAGE_DATA_TYPE:
        image = decodedData.get_data()

        exif = image._getexif()

        # Orientationタグを探す
        if exif is not None:
            for tag, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag)
                if tag_name == "Orientation":
                    orientation = value
                    if orientation == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation == 8:
                        image = image.rotate(90, expand=True)
        queue.put(image)
    else:
        print(f"Recieve {decodedData.get_name()}")


# ---------------------
# main
# ---------------------
def main():
    working_dir = Path("C:\\Users\\arusu\\Downloads")
    decoder = ImageDataDecoder()
    q = queue.Queue(0)
    server = TCPServer(decoder, lambda data: on_receive(q, data), port=51234)
    server.start_server()

    root = tk.Tk()
    root.geometry("400x300")
    root.title("実験フロー")

    data_container = {}

    name_step_factory = InitialStepFactory(data_container)
    before_ssq_factory = SSQStepFactory(
        working_dir, data_container, q, lambda: print("save"), "before"
    )
    unity_step_factory = UnityStepFactory(data_container)
    after_ssq_factory = SSQStepFactory(
        working_dir, data_container, q, lambda: print("save"), "after"
    )
    factories = [
        name_step_factory.create,
        before_ssq_factory.create,
        # unity_step_factory.create,
        after_ssq_factory.create,
    ]

    manager = StepManager(factories)
    window = MainWindow(
        root,
        on_press_next=manager.next_step,
        on_press_return_first=lambda: manager.show_step(0),
    )
    manager.main_window = window
    manager.show_step(0)

    root.mainloop()


if __name__ == "__main__":
    main()
