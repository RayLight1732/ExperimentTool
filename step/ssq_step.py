import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional,Tuple
from PIL import Image
import PIL.ImageTk
from step.step import Step
import cv2
from mark_seat_reader import CorrectionProcessor, Margin, MarkseatReader
from queue import Queue
import numpy as np
from pathlib import Path
import csv
import step.util as sutil


class SSQStepUI:
    def __init__(self, container: ttk.Frame, row_count: int, col_count: int):
        self.container = container
        self.row_count = row_count
        self.col_count = col_count
        self.canvas = None
        self.radio_vars: list[tk.IntVar] = []
        self.tk_image = None  # PIL画像保持用

    def build(self, on_resize: Callable, on_radio_update: Callable):
        self.container.columnconfigure(0, weight=2)
        self.container.columnconfigure(1, weight=1)
        self.container.rowconfigure(0, weight=1)

        # カメラ部分
        camera_container = ttk.Frame(self.container)
        camera_container.grid(row=0, column=0, sticky="nsew")
        self.canvas = tk.Canvas(
            camera_container, highlightthickness=0, background="gray", width=10
        )
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind("<Configure>", on_resize)

        # 表示部分
        display_container = ttk.Frame(self.container)
        display_container.grid(row=0, column=1, sticky="nsew")
        ttk.Label(display_container, text="SSQを回答してください").pack(side="top")

        inner = ttk.Frame(display_container)
        inner.pack(expand=True, side="top", anchor="n")

        # ラジオボタン
        style = ttk.Style()
        style.layout(
            "NoFocus.TRadiobutton",
            [
                (
                    "Radiobutton.padding",
                    {
                        "children": [
                            ("Radiobutton.indicator", {"side": "left", "sticky": ""}),
                            ("Radiobutton.label", {"side": "left", "sticky": ""}),
                        ],
                        "sticky": "nswe",
                    },
                )
            ],
        )
        for row in range(self.row_count):
            ttk.Label(inner, text=f"Q{row+1}").grid(
                row=row, column=0, sticky="w", padx=5
            )
            var = tk.IntVar(value=-1)
            self.radio_vars.append(var)
            for col in range(self.col_count):
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

        img_ratio = pil_image.width / pil_image.height
        canvas_ratio = self.canvas.winfo_width() / self.canvas.winfo_height()
        if canvas_ratio > img_ratio:
            height = self.canvas.winfo_height()
            width = int(height * img_ratio)
        else:
            width = self.canvas.winfo_width()
            height = int(width / img_ratio)

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


class SSQImageProcessor:
    def __init__(
        self, correction_processor: CorrectionProcessor, markseat_reader: MarkseatReader
    ):
        self.correction_processor = correction_processor
        self.markseat_reader = markseat_reader

    def read_answers(self, image: Image.Image) -> Tuple[list[int],np.ndarray] | Tuple[None,None]:
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        corrected,rect = self.correction_processor.correct(opencv_image)
        if corrected is None:
            return None,None

        gray = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)
        result = self.markseat_reader.read(gray)
        answers = []
        for row in result:
            answers.append(row[0] if len(row) == 1 else -1)
        return answers,rect
    
    def overlay_image(self,image:Image.Image,rect,answers:list[int])->Image.Image:
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        marked = [[answer] if answer != -1 else [] for answer in answers ]
        mask = self.markseat_reader.create_mask(marked)
        masked = self.correction_processor.overlay_mask(opencv_image,mask,rect,0.5)
        new_image = cv2.cvtColor(masked, cv2.COLOR_BGR2RGB)
        new_image = Image.fromarray(new_image)
        return new_image


class SSQDataSaver:
    def __init__(self, save_dir: Path, file_name: str):
        self.save_dir = save_dir
        self.file_name = file_name

    def save_image(self, image: Image.Image):
        self.save_dir.mkdir(parents=True, exist_ok=True)
        image_path = self.save_dir / f"{self.file_name}.jpeg"
        image.save(image_path)

    def save_csv(self, answers: list[int]):
        self.save_dir.mkdir(parents=True, exist_ok=True)
        csv_path = self.save_dir / f"{self.file_name}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for value in answers:
                writer.writerow([value])


class SSQStep(Step):
    def __init__(
        self,
        queue: Queue[Image.Image],
        container,
        set_complete: Callable[[bool], None],
        ui: SSQStepUI,
        processor: SSQImageProcessor,
        saver: SSQDataSaver,
    ):
        self.container = container
        self.set_complete = set_complete
        self.queue = queue
        self.image = None
        self.after_id = None
        self.ui = ui
        self.processor = processor
        self.saver = saver

    def build(self):
        with self.queue.mutex:
            self.queue.queue.clear()
            self.queue.all_tasks_done.notify_all()
            self.queue.unfinished_tasks = 0
        self.ui.build(self._on_resize, self._on_radio_update)
        self._update()

    def _on_resize(self, event):
        self.ui.update_canvas(self.image)

    def _update(self):
        if self.queue.qsize() > 0:
            image = self.queue.get(False)
            if image:
                answers,rect= self.processor.read_answers(image)
                if answers is not None:
                    self.ui.set_radio_values(answers)
                    self._on_radio_update()
                    self.image = self.processor.overlay_image(image,rect,answers)
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


class SSQStepFactory:
    def __init__(
        self,
        working_dir: Path,
        data_container,
        queue: Queue,
        file_name_prefix: str = "",
    ):
        self.working_dir = working_dir
        self.data_container = data_container
        self.file_name_prefix = file_name_prefix
        self.queue = queue

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> Step:
        rect_margin = Margin(230, 1110, 0, 10)
        margin = Margin(15, 75, 75, 15)
        markseat_reader = MarkseatReader(
            rect_margin=rect_margin,
            row=16,
            col=4,
            cell_width=120,
            cell_height=60,
            cell_margin=margin,
        )
        correction_processor = CorrectionProcessor(1000, 900)
        save_dir = sutil.get_save_dir(self.working_dir, self.data_container)
        file_name = (
            f"{sutil.get_file_name(self.data_container)}_{self.file_name_prefix}"
        )

        ui = SSQStepUI(frame, 16, 4)
        processor = SSQImageProcessor(correction_processor, markseat_reader)
        saver = SSQDataSaver(save_dir, file_name)

        return SSQStep(self.queue, frame, set_complete, ui, processor, saver)
