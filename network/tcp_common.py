import socket
import threading
from network.data.serializable_data import SerializableData
from typing import Callable
from network.data.data_decoder import DataDecoder, DecodedData
import select


class DataSender:
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.lock = threading.Lock()

    def send(self, data: SerializableData):
        try:
            with self.lock:
                # TODO length dataに変更
                encoded = data.name().encode()
                size = len(encoded)
                size_header = size.to_bytes(4, byteorder="little")
                self.sock.sendall(size_header)
                self.sock.sendall(encoded)
                bytes_data = data.to_bytes()
                size_header = len(bytes_data).to_bytes(4, byteorder="little")
                self.sock.sendall(size_header)
                self.sock.sendall(bytes_data)
        except Exception as e:
            print(f"Failed to send data: {e}")


class DataReceiver(threading.Thread):
    def __init__(
        self,
        sock: socket.socket,
        decoder: DataDecoder,
        on_receive: Callable[[DecodedData], None],
        on_failed: Callable[[], None],
    ):
        super().__init__(daemon=True)
        self.sock = sock
        self.running = True
        self.decoder = decoder
        self.on_receive = on_receive
        self.on_failed = on_failed

    def run(self):
        try:
            while self.running:
                readable, _, _ = select.select([self.sock], [], [], 0.0)
                if readable:
                    data = self.decoder.accept(self.sock)
                    self.on_receive(data)
        except Exception as e:
            print(f"Receive error: {e}")
            if self.running:
                self.on_failed()

    def stop(self):
        self.running = False
