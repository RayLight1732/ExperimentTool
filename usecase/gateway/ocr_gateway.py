from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.participant import Participant
from domain.entities.session import Session
from domain.entities.ssq import SSQScore
from PIL import Image


class OCRGateway(ABC):
    @abstractmethod
    def read_answers(self, image: Image.Image) -> SSQScore:
        """画像からSSQスコアを取得"""
        pass

    @abstractmethod
    def overlay_image(self, image: Image.Image, rect, answers: SSQScore) -> Image.Image:
        """画像にSSQスコアを重畳表示"""
        pass
