from abc import ABC, abstractmethod
import socket
from typing import Any


class DecodedData:
    def __init__(self, name: str, data: Any):
        self._name = name
        self._data = data

    def get_name(self):
        return self._name

    def get_data(self):
        return self._data


class DataDecoder(ABC):
    @abstractmethod
    def accept(
        self,
        sock: socket.socket,
    ) -> DecodedData:
        pass

    def _recv_all(self, sock: socket.socket, size, timeout=-1):
        data = b""
        while len(data) < size:
            packet = sock.recv(size - len(data))
            if not packet:
                raise ConnectionError("Connection closed during recv")
            data += packet
        return data
