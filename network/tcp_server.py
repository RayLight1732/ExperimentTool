import socket
import threading
from network.data.serializable_data import SerializableData
from typing import Callable, Optional, Tuple
from network.data.data_decoder import DataDecoder, DecodedData
from network.data.string_data import StringData, STRING_DATA_TYPE, StringDataDecoder
from network.data.multi_type_data_decoder import MultiTypeDataDecoder
from network.tcp_common import DataSender, DataReceiver
from network.data.image_data import ImageDataDecoder, IMAGE_DATA_TYPE
import time


class TCPServer:
    def __init__(
        self,
        decoder: DataDecoder,
        on_receive: Callable[[DecodedData], None],
        host="0.0.0.0",
        port=12345,
    ):
        self.host = host
        self.port = port
        self.server_sock: Optional[socket.socket] = None
        self.running = False
        self.client_threads: list[Tuple[socket.socket, DataSender, DataReceiver]] = []
        self.decoder: DataDecoder = decoder
        self.on_receive: Callable[[DecodedData], None] = on_receive

    def start_server(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen()
        self.running = True
        print(f"Server started on {self.host}:{self.port}")

        threading.Thread(target=self._accept_clients, daemon=True).start()

    def _accept_clients(self):
        while self.running:
            try:
                client_sock, addr = self.server_sock.accept()
                print(f"Client connected from {addr}")
                sender = DataSender(client_sock)

                def on_disconnect():
                    print(f"Client {addr} disconnected")
                    self._remove_client(client_sock)

                receiver = DataReceiver(
                    client_sock,
                    self.decoder,
                    self.on_receive,
                    on_disconnect,
                )
                receiver.start()
                self.client_threads.append((client_sock, sender, receiver))
            except Exception as e:
                print(f"Accept error: {e}")

    def _remove_client(self, sock: socket.socket):
        for i, (client_sock, sender, receiver) in enumerate(self.client_threads):
            if client_sock == sock:
                receiver.stop()
                client_sock.close()
                del self.client_threads[i]
                break

    def stop_server(self):
        self.running = False
        for sock, sender, receiver in self.client_threads:
            receiver.stop()
            sock.close()
        if self.server_sock:
            self.server_sock.close()

        print("Server stopped")

    def send_all(self, data: SerializableData):
        for client_sock, sender, _ in self.client_threads:
            sender.send(data)


image = None


def on_receive(decodedData: DecodedData):
    if decodedData.get_name() == STRING_DATA_TYPE:
        print(f"Receive StringData:{decodedData.get_data()}")
    elif decodedData.get_name() == IMAGE_DATA_TYPE:
        image = decodedData.get_data()
    else:
        print(f"Recieve {decodedData.get_name()}")


if __name__ == "__main__":
    # decoder = MultiTypeDataDecoder({STRING_DATA_TYPE: StringDataDecoder()})
    decoder = ImageDataDecoder()
    server = TCPServer(decoder, on_receive)
    server.start_server()
    try:
        while True:
            if image is not None:
                image.show(title=f"Image")
                image = None
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        server.stop_server()
