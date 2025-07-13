# step/mssq_step.py

from step.base_survey_step import (
    BaseStepUI,
    BaseImageProcessor,
    BaseDataSaver,
    BaseSurveyStep,
)
from mark_seat_reader import CorrectionProcessor, Margin, MarkseatReader
from pathlib import Path
from queue import Queue
from typing import Callable, Tuple
import numpy as np
from PIL import Image
import cv2
import step.util as sutil


class MSSQImageProcessor(BaseImageProcessor):
    def __init__(
        self,
        correction_processor: CorrectionProcessor,
        reader1: MarkseatReader,
        upper_row_count: int,
        reader2: MarkseatReader,
    ):
        self.correction_processor = correction_processor
        self.reader1 = reader1
        self.upper_row_count = upper_row_count
        self.reader2 = reader2

    def read_answers(
        self, image: Image.Image
    ) -> Tuple[list[int], np.ndarray] | Tuple[None, None]:
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        corrected, rect = self.correction_processor.correct(opencv_image)
        if corrected is None:
            return None, None
        gray = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)
        answers = []
        for reader in (self.reader1, self.reader2):
            result = reader.read(gray)
            answers.extend([row[0] if len(row) == 1 else -1 for row in result])
        return answers, rect

    def overlay_image(
        self, image: Image.Image, rect, answers: list[int]
    ) -> Image.Image:
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        marked1 = [[a] if a != -1 else [] for a in answers[: self.upper_row_count]]
        marked2 = [[a] if a != -1 else [] for a in answers[self.upper_row_count :]]
        mask1 = self.reader1.create_mask(marked1)
        mask2 = self.reader2.create_mask(marked2)
        overlayed = self.correction_processor.overlay_mask(
            opencv_image, [mask1, mask2], rect, alpha=0.5
        )
        return Image.fromarray(cv2.cvtColor(overlayed, cv2.COLOR_BGR2RGB))


class MSSQStepFactory:
    def __init__(
        self,
        working_dir: Path,
        data_container,
        queue: Queue,
        file_name_prefix: str = "",
    ):
        self.working_dir = working_dir
        self.data_container = data_container
        self.queue = queue
        self.file_name_prefix = file_name_prefix

    def create(self, frame, set_complete: Callable[[bool], None]) -> BaseSurveyStep:
        margin = Margin(15, 75, 75, 15)
        rect_margin1 = Margin(280, 1050, 0, 1260)
        rect_margin2 = Margin(1440, 1050, 0, 60)

        reader1 = MarkseatReader(
            rect_margin=rect_margin1,
            row=8,
            col=5,
            cell_width=120,
            cell_height=60,
            cell_margin=margin,
        )
        reader2 = MarkseatReader(
            rect_margin=rect_margin2,
            row=8,
            col=5,
            cell_width=120,
            cell_height=60,
            cell_margin=margin,
        )
        correction_processor = CorrectionProcessor(1075, 860, [4, 5, 7, 6])
        processor = MSSQImageProcessor(correction_processor, reader1, 8, reader2)
        save_dir = self.working_dir / sutil.get_name(self.data_container)
        file_name = "MSSQ"
        ui = BaseStepUI(
            frame,
            sections=[("12歳以前", 8, 5), ("直近10年", 8, 5)],
            main_title="MSSQを回答してください",
        )
        saver = BaseDataSaver(save_dir, file_name)
        return BaseSurveyStep(self.queue, frame, set_complete, ui, processor, saver)
