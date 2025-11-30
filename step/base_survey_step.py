import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, List, Tuple
from PIL import Image
import PIL.ImageTk
from step.step import Step
from queue import Queue
import numpy as np
import csv
from pathlib import Path


class BaseSurveyUI:
    def __init__(
        self,
        container: ttk.Frame,
        sections: List[Tuple[str, int, int]],  # [(タイトル, 行数, 列数), ...]
        main_title: str,
    ):
        self.container = container
        self.sections = sections
        self.main_title = main_title
        self.canvas = None
        self.radio_vars: list[tk.IntVar] = []
        self.tk_image = None

    def build(self, on_resize: Callable, on_radio_update: Callable):
        self.container.columnconfigure(0, weight=2)
        self.container.columnconfigure(1, weight=1)
        self.container.rowconfigure(0, weight=1)

        # カメラ側
        camera_container = ttk.Frame(self.container)
        camera_container.grid(row=0, column=0, sticky="nsew")
        self.canvas = tk.Canvas(
            camera_container, background="gray", highlightthickness=0
        )
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Configure>", on_resize)

        # 表示側
        display_container = ttk.Frame(self.container)
        display_container.grid(row=0, column=1, sticky="nsew")
        ttk.Label(display_container, text=self.main_title).pack(side="top")

        style = ttk.Style()
        style.layout(
            "NoFocus.TRadiobutton",
            [
                (
                    "Radiobutton.padding",
                    {
                        "children": [
                            ("Radiobutton.indicator", {"side": "left"}),
                            ("Radiobutton.label", {"side": "left"}),
                        ],
                        "sticky": "nswe",
                    },
                )
            ],
        )

        for section_title, row_count, col_count in self.sections:
            ttk.Label(display_container, text=section_title).pack(side="top", padx=10)
            inner = ttk.Frame(display_container)
            inner.pack(expand=True, side="top", anchor="n")

            for row in range(row_count):
                ttk.Label(inner, text=f"Q{row+1}").grid(
                    row=row, column=0, sticky="w", padx=5
                )
                var = tk.IntVar(value=-1)
                self.radio_vars.append(var)
                for col in range(col_count):
                    ttk.Radiobutton(
                        inner,
                        value=col,
                        variable=var,
                        style="NoFocus.TRadiobutton",
                        command=on_radio_update,
                    ).grid(row=row, column=col + 1, sticky="w", padx=5, pady=5)

    def update_canvas(self, pil_image: Optional[Image.Image]):
        self.canvas.delete("all")
        if pil_image is None:
            self.canvas.create_text(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                text="画像を撮影してください",
                fill="white",
                font=("Arial", 14),
            )
            return

        canvas_ratio = self.canvas.winfo_width() / self.canvas.winfo_height()
        img_ratio = pil_image.width / pil_image.height
        if canvas_ratio > img_ratio:
            height = self.canvas.winfo_height()
            width = int(height * img_ratio)
        else:
            width = self.canvas.winfo_width()
            height = int(width / img_ratio)
        if width <= 0 or height <= 0:
            return
        resized = pil_image.resize((width, height))
        self.tk_image = PIL.ImageTk.PhotoImage(resized)
        x = (self.canvas.winfo_width() - width) // 2
        y = (self.canvas.winfo_height() - height) // 2
        self.canvas.create_image(x, y, anchor="nw", image=self.tk_image)

    def get_radio_values(self) -> list[int]:
        return [var.get() for var in self.radio_vars]

    def set_radio_values(self, values: list[int]):
        for i, val in enumerate(values):
            self.radio_vars[i].set(val if val != -1 else -1)


class BaseImageProcessor:
    def read_answers(
        self, image: Image.Image
    ) -> Tuple[list[int], np.ndarray] | Tuple[None, None]:
        raise NotImplementedError

    def overlay_image(
        self, image: Image.Image, rect, answers: list[int]
    ) -> Image.Image:
        raise NotImplementedError


class BaseDataSaver:
    def __init__(self, save_dir: Path, file_name: str):
        self.save_dir = save_dir
        self.file_name = file_name

    def _ensure_dir_exists(self):
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def save_image(self, image: Image.Image):
        self._ensure_dir_exists()
        image_path = self.save_dir / f"{self.file_name}.jpeg"
        image.save(image_path)

    def save_csv(self, answers: list[int]):
        self._ensure_dir_exists()
        csv_path = self.save_dir / f"{self.file_name}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for value in answers:
                writer.writerow([value])

    def load(self) -> Tuple[Optional[Image.Image], Optional[list[int]]]:
        image_path = self.save_dir / f"{self.file_name}.jpeg"
        csv_path = self.save_dir / f"{self.file_name}.csv"
        image, answers = None, None

        try:
            with Image.open(image_path) as img:
                image = img.copy()
        except Exception:
            pass

        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                answers = [int(row[0]) for row in reader if row]
        except Exception:
            pass

        return image, answers


class BaseSurveyStep(Step):
    def __init__(
        self,
        queue: Queue,
        container: tk.Frame,
        set_complete: Callable[[bool], None],
        ui: BaseSurveyUI,
        processor: BaseImageProcessor,
        saver: BaseDataSaver,
    ):
        self.queue = queue
        self.container = container
        self.set_complete = set_complete
        self.ui = ui
        self.processor = processor
        self.saver = saver
        self.image = None
        self.after_id = None

    def build(self):
        with self.queue.mutex:
            self.queue.queue.clear()
            self.queue.all_tasks_done.notify_all()
            self.queue.unfinished_tasks = 0

        self.ui.build(self._on_resize, self._on_radio_update)
        image, answers = self.saver.load()
        if answers:
            self.ui.set_radio_values(answers)
            self._on_radio_update()
        if image:
            self.image = image
            self.ui.update_canvas(image)
        self._update()

    def _on_resize(self, event):
        self.ui.update_canvas(self.image)

    def _update(self):
        if self.queue.qsize() > 0:
            image = self.queue.get(False)
            if image:
                answers, rect = self.processor.read_answers(image)
                if answers is not None:
                    self.ui.set_radio_values(answers)
                    self._on_radio_update()
                    self.image = self.processor.overlay_image(image, rect, answers)
                else:
                    self.image = image
                self.ui.update_canvas(self.image)
        self.after_id = self.container.after(30, self._update)

    def _on_radio_update(self):
        complete = all(val != -1 for val in self.ui.get_radio_values())
        self.set_complete(complete)

    def on_dispose(self):
        if self.after_id:
            self.container.after_cancel(self.after_id)

    def before_next(self):
        if self.image:
            self.saver.save_image(self.image)
        self.saver.save_csv(self.ui.get_radio_values())
