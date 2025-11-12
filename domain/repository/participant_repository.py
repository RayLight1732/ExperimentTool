from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.participant import Participant
from domain.entities.cooling_condition import CoolingCondition


class ParticipantRepository(ABC):

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Participant]:
        """被験者名から検索"""
        pass

    @abstractmethod
    def list_all(self) -> list[Participant]:
        """すべての被験者を返す"""
        pass
