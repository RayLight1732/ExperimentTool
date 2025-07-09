from network.data.data_decoder import DataDecoder, DecodedData
import socket
from typing import Any


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
