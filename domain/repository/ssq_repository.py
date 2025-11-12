from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.participant import Participant
from domain.entities.session import Session
from domain.entities.ssq import SSQScore


class SSQRepository(ABC):
    @abstractmethod
    def save_pre(
        self, participant: Participant, session: Session, ssq: SSQScore
    ) -> None:
        """事前SSQを保存"""
        pass

    @abstractmethod
    def save_post(
        self, participant: Participant, session: Session, ssq: SSQScore
    ) -> None:
        """事後SSQを保存"""
        pass

    @abstractmethod
    def load_pre(
        self, participant: Participant, session: Session
    ) -> Optional[SSQScore]:
        """事前SSQを読み込み"""
        pass

    @abstractmethod
    def load_post(
        self, participant: Participant, session: Session
    ) -> Optional[SSQScore]:
        """事後SSQを読み込み"""
        pass
