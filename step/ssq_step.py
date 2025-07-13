# step/ssq_step.py

from step.base_survey_step import BaseStepUI,BaseImageProcessor,BaseDataSaver,BaseSurveyStep
from mark_seat_reader import CorrectionProcessor, Margin, MarkseatReader
from pathlib import Path
from queue import Queue
from typing import Callable, Tuple
import numpy as np
from PIL import Image
import cv2
import step.util as sutil
from tkinter import ttk


class SSQImageProcessor(BaseImageProcessor):
    def __init__(self, correction_processor: CorrectionProcessor, markseat_reader: MarkseatReader):
        self.correction_processor = correction_processor
        self.markseat_reader = markseat_reader

    def read_answers(self, image: Image.Image) -> Tuple[list[int], np.ndarray] | Tuple[None, None]:
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        corrected, rect = self.correction_processor.correct(opencv_image)
        if corrected is None:
            return None, None
        gray = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)
        result = self.markseat_reader.read(gray)
        answers = [row[0] if len(row) == 1 else -1 for row in result]
        return answers, rect

    def overlay_image(self, image: Image.Image, rect, answers: list[int]) -> Image.Image:
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        marked = [[a] if a != -1 else [] for a in answers]
        mask = self.markseat_reader.create_mask(marked)
        overlayed = self.correction_processor.overlay_mask(opencv_image, mask, rect, alpha=0.5)
        return Image.fromarray(cv2.cvtColor(overlayed, cv2.COLOR_BGR2RGB))


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

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> BaseSurveyStep:
        rect_margin = Margin(285, 1110, 0, 60)
        margin = Margin(15, 75, 75, 15)
        markseat_reader = MarkseatReader(
            rect_margin=rect_margin,
            row=16,
            col=4,
            cell_width=120,
            cell_height=60,
            cell_margin=margin,
        )
        processor = SSQImageProcessor(CorrectionProcessor(1000, 900), markseat_reader)
        save_dir = sutil.get_save_dir(self.working_dir, self.data_container)
        file_name = f"{sutil.get_file_name(self.data_container)}_{self.file_name_prefix}"
        ui = BaseStepUI(frame,[("",16, 4)],"SSQを回答してください")
        saver = BaseDataSaver(save_dir, file_name)
        return BaseSurveyStep(self.queue, frame, set_complete, ui, processor, saver)
