from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.participant import Participant
from domain.entities.cooling_condition import CoolingCondition


class ParticipantUsecase(ABC):
    @abstractmethod
    def list_unfinished_condition(
        self, participant: Participant
    ) -> List[CoolingCondition]:
        """未実施の実験条件を列挙する"""
        pass

    @abstractmethod
    def list_finished_condition() -> List[CoolingCondition]:
        """実行済みの実験条件を列挙する"""
        pass
