from usecase.gateway.device_gateway import DeviceGateway
from domain.entities.message import Message


class DeviceCommunicationUseCase:
    """1つのデバイス(Gateway)との通信ロジックを担当する"""

    def __init__(self, gateway: DeviceGateway):
        self.gateway = gateway

    def list_available_devices(self):
        return self.gateway.list_devices()

    def connect(self, params):
        self.gateway.connect(params)

    def disconnect(self):
        self.gateway.disconnect()

    def send(self, message: Message):
        if not self.gateway.is_connected():
            raise RuntimeError("Device not connected.")
        self.gateway.send_message(message)

    def subscribe(self, callback):
        """受信時の処理を登録"""
        self.gateway.on_message(callback)
