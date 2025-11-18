from abc import ABC, abstractmethod
from typing import Callable, Sequence
from domain.entities.message import Message


class ArduinoGateway(ABC):
    """Arduinoとの通信を抽象化するGatewayインターフェース"""

    @abstractmethod
    def list_devices(self) -> Sequence[str]:
        """接続可能なデバイスの一覧を返す（通信方式に依存しない）。"""
        pass

    @abstractmethod
    def connect(self, device_id: str) -> None:
        """指定したデバイスに接続する（ポート名やアドレスなど実装依存）。"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Arduinoとの接続を切断する。"""
        pass

    @abstractmethod
    def send_message(self, message: Message) -> None:
        """
        Arduinoにメッセージを送信する。
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
