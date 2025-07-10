from network.data.data_decoder import DataDecoder, DecodedData
from network.data.serializable_data import SerializableData
import socket
from typing import Any

MULTI_TYPE_DATA = "MultiTypeData"


class MultiTypeDataDecoder(DataDecoder):

    def __init__(self, decoders: dict[str, DataDecoder]):
        self.decoders = decoders

    def accept(self, sock: socket) -> DecodedData:
        size_header = self._recv_all(sock, 4)
        size = int.from_bytes(size_header, byteorder="little")
        name = self._recv_all(sock, size).decode()
        decoder = self.decoders.get(name)
        if decoder is None:
            raise Exception("Decoder does not found.")
        return decoder.accept(sock)


class MultiTypeData(SerializableData):
    def __init__(self, data: SerializableData):
        self.data = data

    def to_bytes(self) -> bytes:
        # TODO size name dataに変更
        encoded = self.data.name().encode()
        size = len(encoded)
        size_header = size.to_bytes(4, byteorder="little")
        return size_header + encoded + self.data.to_bytes()

    def name(self) -> str:
        return MULTI_TYPE_DATA
