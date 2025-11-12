from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.participant import Participant
from domain.entities.session import Session
from domain.entities.ssq import SSQScore
from PIL import Image


class SSQUsecase(ABC):
    @abstractmethod
    def analyze_image(self, image: Image.Image) -> SSQScore:
        """画像からSSQスコアを取得"""
        pass

    @abstractmethod
    def make_overlay(self, image: Image.Image, rect, answers: SSQScore) -> Image.Image:
        """画像にSSQスコアを重畳表示"""
        pass
