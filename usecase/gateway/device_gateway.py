from abc import ABC, abstractmethod
from typing import Callable, Sequence
from domain.entities.message import Message
from domain.entities.connection_params import ConnectionParams


class DeviceGateway(ABC):
    """外部デバイスとの通信を抽象化するGatewayインターフェース"""

    @abstractmethod
    def list_devices(self) -> Sequence[ConnectionParams]:
        """接続可能なデバイスの一覧を返す。"""
        pass

    @abstractmethod
    def connect(self, param: ConnectionParams) -> None:
        """指定したデバイスに接続する（ポート名やアドレスなど実装依存）。"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """デバイスとの接続を切断する。"""
        pass

    @abstractmethod
    def send_message(self, message: Message) -> None:
        """
        デバイスにメッセージを送信する。
        """
        pass

    @abstractmethod
    def on_message(self, callback: Callable[[Message], None]) -> None:
        """受信時に呼ばれるコールバックを登録"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """現在接続中かどうかを返す。"""
        pass
