import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Tuple
from PIL.ImageFile import ImageFile
import PIL.ImageTk
from step.step import Step
import cv2
from mark_seat_reader import CorrectionProcessor, Margin, MarkseatReader
from queue import Queue
import numpy as np
from pathlib import Path
import csv
import step.util as sutil


class SSQStep(Step):
    def __init__(
        self,
        queue: Queue,
        save_dir: Path,
        file_name: str,
        container: ttk.Frame,
        set_complete: Callable[[bool], None],
        save_value: Callable[[list[int]], None],
        col_count: int,
        row_count: int,
        correction_processor: CorrectionProcessor,
        markseat_reader: MarkseatReader,
    ):
        super().__init__(container, set_complete)
        self.queue = queue
        self.save_dir = save_dir
        self.file_name = file_name
        self.save_value = save_value
        self.canvas_width = 0
        self.canvas_height = 0
        self.after_id = None
        self.image: Optional[ImageFile] = None
        self.col_count = col_count
        self.row_count = row_count
        self.correction_processor = correction_processor
        self.markseat_reader = markseat_reader
        self.radio_vars: list[tk.IntVar] = []

    def build(self):
        with self.queue.mutex:
            self.queue.queue.clear()
            self.queue.all_tasks_done.notify_all()
            self.queue.unfinished_tasks = 0

        self.container.columnconfigure(0, weight=2)  # 左：2
        self.container.columnconfigure(1, weight=1)  # 右：1
        self.container.rowconfigure(0, weight=1)

        camera_container = ttk.Frame(master=self.container)
        camera_container.bind("<Button-1>", lambda event: event.widget.focus_set())
        camera_container.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(
            camera_container, highlightthickness=0, width=10, background="gray"
        )
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.pack(side="top", fill="both", expand=True)

        display_container = ttk.Frame(master=self.container)
        display_container.bind("<Button-1>", lambda event: event.widget.focus_set())
        display_container.grid(row=0, column=1, sticky="nsew")

        description_label = ttk.Label(display_container, text="SSQを回答してください")
        description_label.pack(side="top")
        # 中央寄せ用の内部フレーム
        radio_inner_frame = ttk.Frame(display_container)
        radio_inner_frame.pack(expand=True, side="top", anchor="n")

        # ラジオボタンスタイル
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

        # ラジオボタン配置（radio_inner_frame の中に配置）
        self.radio_buttons = []
        self.radio_vars = []
        index = 0

        for row in range(16):
            label = ttk.Label(radio_inner_frame, text=f"Q{row+1}")
            label.grid(row=row, column=0, sticky="w", padx=5, pady=10)

            var = tk.IntVar(value=-1)
            self.radio_vars.append(var)

            for col in range(4):
                rb = ttk.Radiobutton(
                    radio_inner_frame,
                    value=col,
                    variable=var,
                    style="NoFocus.TRadiobutton",
                    command=self.on_radio_value_update,
                )
                rb.grid(row=row, column=col + 1, sticky="w", padx=5, pady=2)
                self.radio_buttons.append(rb)
                index += 1

        self.update()

    def _on_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        if self.canvas_width != 0 and self.canvas_height != 0:
            self.redraw_canvas()

    def update(self):
        if self.canvas_width == 0 or self.canvas_height == 0:
            self.after_id = self.container.after(30, self.update)
        if self.queue.qsize() <= 0:
            self.after_id = self.container.after(30, self.update)
            return

        image = self.queue.get(False)
        if image is None:
            self.after_id = self.container.after(30, self.update)
            return
        self.image = image
        self.redraw_canvas()
        self._read(self.image)
        self.after_id = self.container.after(30, self.update)

    def resize(self, image) -> Tuple[ImageFile, int, int]:
        image_ratio = image.width / image.height
        container_ratio = (
            self.canvas_width / self.canvas_height if self.canvas_height > 0 else 1
        )

        if container_ratio > image_ratio:
            # 横長すぎ → 高さに合わせる
            new_height = self.canvas_height
            new_width = int(new_height * image_ratio)
        else:
            # 縦長すぎ → 幅に合わせる
            new_width = self.canvas_width
            new_height = int(new_width / image_ratio)

        return (image.resize((new_width, new_height)), new_width, new_height)

    def redraw_canvas(self):
        self.canvas.delete("all")

        if self.image is None:
            self.canvas.create_rectangle(
                0, 0, self.canvas_width, self.canvas_height, fill="gray"
            )
            self.canvas.create_text(
                self.canvas_width // 2,
                self.canvas_height // 2,
                text="画像を撮影してください",
                fill="white",
                font=("Arial", 14),
            )
        else:
            resized, new_width, new_height = self.resize(self.image)
            self.tk_image = PIL.ImageTk.PhotoImage(resized)
            x = (self.canvas_width - new_width) / 2
            y = (self.canvas_height - new_height) / 2
            self.canvas.create_image(x, y, anchor=tk.NW, image=self.tk_image)

    def _read(self, image):
        numpy_image = np.array(image)

        # RGB → BGR（OpenCV形式）
        opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

        corrected = self.correction_processor.correct(opencv_image)
        if corrected is None:
            return
        gray = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)

        # resized = self.markseat_reader._resize(gray)
        # region = self.markseat_reader._extract_region(resized)
        # binary = self.markseat_reader._binarize_image(region)

        result = self.markseat_reader.read(gray)
        for row in range(self.row_count):
            if len(result[row]) == 1:
                self.radio_vars[row].set(result[row][0])
            else:
                self.radio_vars[row].set(-1)
        self.on_radio_value_update()
        # return binary

    def on_radio_value_update(self):
        all_selected = all([var.get() != -1 for var in self.radio_vars])
        self.set_complete(all_selected)

    def on_dispose(self):
        if self.after_id is not None:
            self.container.after_cancel(self.after_id)

    def before_next(self):
        self.save_dir.mkdir(parents=True, exist_ok=True)
        if self.image is not None:
            image_path = Path(self.save_dir) / f"{self.file_name}.jpeg"
            # 保存
            self.image.save(image_path)

        csv_path = Path(self.save_dir) / f"{self.file_name}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # 各行のラジオボタンの選択を記録
            for var in self.radio_vars:
                writer.writerow([var.get()])


class SSQStepFactory:
    def __init__(
        self,
        working_dir: Path,
        data_container,
        queue: Queue,
        save_value: Callable[[list[int]], None],
        file_name_prefix: str = "",
    ):
        self.working_dir = working_dir
        self.data_container = data_container
        self.file_name_prefix = file_name_prefix
        self.queue = queue
        self.save_value = save_value

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> Step:
        rect_margin = Margin(230, 1110, 0, 10)
        margin = Margin(15, 75, 75, 15)
        reader = MarkseatReader(
            rect_margin=rect_margin,
            row=16,
            col=4,
            width=120,
            height=60,
            cell_margin=margin,
        )
        processor = CorrectionProcessor(1000, 900)
        save_dir = sutil.get_save_dir(self.working_dir, self.data_container)
        file_name = (
            f"{sutil.get_file_name(self.data_container)}_{self.file_name_prefix}"
        )
        return SSQStep(
            self.queue,
            save_dir,
            file_name,
            frame,
            set_complete,
            self.save_value,
            4,
            16,
            processor,
            reader,
        )
