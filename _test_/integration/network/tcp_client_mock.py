import socket
import threading
from network.data.serializable_data import SerializableData
from typing import Callable, Optional
from network.data.multi_type_data_decoder import MultiTypeDataDecoder
from network.data.string_data import StringData, STRING_DATA_TYPE, StringDataDecoder
from network.data.data_decoder import DataDecoder, DecodedData
from network.tcp_common import DataReceiver, DataSender


class TCPClientMock:
    def __init__(self):
        pass

    @property
    def connected(self) -> bool:
        return True

    def connect(
        self,
        host="127.0.0.1",
        port=12345,
    ) -> bool:
        pass

    def disconnect(self):
        pass
    def send_data(self, data: SerializableData):
        pass

