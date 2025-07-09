from network.data.serializable_data import SerializableData
from network.data.data_decoder import DataDecoder, DecodedData
import socket


STRING_DATA_TYPE = "StringData"


class StringData(SerializableData):

    def __init__(self, message: str):
        self.message = message

    def to_bytes(self) -> bytes:
        return self.message.encode()

    def name(self) -> str:
        return STRING_DATA_TYPE


class StringDataDecoder(DataDecoder):
    def accept(self, sock: socket.socket) -> DecodedData:
        size_header = self._recv_all(sock, 4)
        size = int.from_bytes(size_header, byteorder="little")
        message = self._recv_all(sock, size).decode()
        return DecodedData(STRING_DATA_TYPE, message)
