from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.participant import Participant
from domain.entities.cooling_condition import CoolingCondition


class ParticipantUsecase(ABC):
    @abstractmethod
    def list_participant(self, prefix: str) -> List[Participant]:
        """
        prefixから始まる被験者を返す
        """
        pass

    @abstractmethod
    def get_participant(self, name: str) -> Participant:
        """
        被験者を取得
        存在しなかったら新しく作成
        """
        pass

    @abstractmethod
    def list_unfinished_condition(
        self, participant: Participant
    ) -> List[CoolingCondition]:
        """未実施の実験条件を列挙する"""
        pass

    @abstractmethod
    def list_finished_condition(
        self, participant: Participant
    ) -> List[CoolingCondition]:
        """実行済みの実験条件を列挙する"""
        pass
