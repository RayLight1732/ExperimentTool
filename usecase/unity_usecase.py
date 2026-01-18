from abc import ABC, abstractmethod
from typing import Callable, Sequence
from domain.entities.connection_params import ConnectionParams


class UnityUsecase(ABC):
    @abstractmethod
    def list_devices(self) -> Sequence[ConnectionParams]:
        """接続可能なデバイスの一覧を返す。"""
        pass

    @abstractmethod
    def connect(self, param: ConnectionParams) -> None:
        """指定したデバイスに接続する"""
        pass

    @abstractmethod
    def on_try_connect(self, callback: Callable[[bool],]):
        """接続を試行した際のコールバックを登録する"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """デバイスとの接続を切断する。"""
        pass

    @abstractmethod
    def on_disconnected(self, callback: Callable[[],]):
        """切断した際のコールバックを登録する"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """現在接続中かどうかを返す。"""
        pass

    @abstractmethod
    def start(self) -> bool:
        """実験を開始する"""
        pass

    @abstractmethod
    def on_high_stress(self, callback: Callable[[],]):
        """高負荷状態になった際のコールバックを登録する"""
        pass

    @abstractmethod
    def on_low_stress(self, callback: Callable[[],]):
        """低負荷状態になった際のコールバックを登録する"""
        pass

    @abstractmethod
    def on_end_experiment(self, callback: Callable[[],]):
        """実験が終わった際のコールバックを登録する"""
        pass
