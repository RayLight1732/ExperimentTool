from usecase.gateway.device_gateway import DeviceGateway
from typing import Sequence, Callable
from domain.entities.message import Message
from domain.entities.connection_params import ConnectionParams
from infrastructure.device.tcp.tcp_connection_params import TCPConnectionParams


class TCPClientGateway(DeviceGateway):
    def list_devices(self) -> Sequence[ConnectionParams]:
        """接続可能なデバイスの一覧を返す。"""
        pass

    def connect(self, param: ConnectionParams) -> None:
        """指定したデバイスに接続する（ポート名やアドレスなど実装依存）。"""
        if not isinstance(param, TCPConnectionParams):
            raise ValueError("params must be TcpConnectionParams")

    def disconnect(self) -> None:
        """デバイスとの接続を切断する。"""
        pass

    def send_message(self, message: Message) -> None:
        """
        デバイスにメッセージを送信する。
        """
        pass

    def on_message(self, callback: Callable[[Message], None]) -> None:
        """受信時に呼ばれるコールバックを登録"""
        pass

    def is_connected(self) -> bool:
        """現在接続中かどうかを返す。"""
        pass
