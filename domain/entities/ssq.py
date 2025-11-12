from dataclasses import dataclass
from typing import List


@dataclass
class SSQScore:
    nausea: int
    oculomoror: int
    disorientation: int
    total: int


@dataclass
class SSQResult:
    participant_id: str
    responses: List[int]
    timestamp: str

    def calc_scores(self) -> SSQScore:
        """症状群スコアや総合スコアを計算するメソッド"""
        nausea = (
            sum(self.responses[i] for i in [0, 5, 6, 7, 8, 14, 15]) * 9.54
        )  # 嘔吐系
        oculomotor = (
            sum(self.responses[i] for i in [0, 1, 2, 3, 4, 8, 10]) * 7.58
        )  # 視覚系
        disorientation = sum(
            self.responses[i] for i in [4, 7, 9, 10, 11, 12, 13] * 13.92
        )  # 方向感覚系
        total = sum(self.responses) * 3.74
        return SSQScore(
            nausea,
            oculomotor,
            disorientation,
            total,
        )
