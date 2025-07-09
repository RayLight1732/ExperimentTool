import socket
import threading
from network.data.serializable_data import SerializableData
from typing import Callable, Optional
from network.data.multi_type_data_decoder import MultiTypeDataDecoder
from network.data.string_data import StringData, STRING_DATA_TYPE, StringDataDecoder
from network.data.data_decoder import DataDecoder, DecodedData
from network.tcp_common import DataReceiver, DataSender


class TCPClient:
    def __init__(self, decoder: DataDecoder):
        self._sock: Optional[socket.socket] = None
        self._connected = False
        self._lock = threading.Lock()
        self._sender_lock = threading.Lock()
        self._sender: Optional[DataSender] = None
        self._receiver: Optional[DataReceiver] = None
        self._decoder: DataDecoder = decoder
        self.on_receive: Callable[[DecodedData], None] = None
        self.on_disconnected: Optional[Callable[[], None]] = None
        self.on_connected: Optional[Callable[[], None]] = None

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(
        self,
        host="127.0.0.1",
        port=12345,
    ) -> bool:
        with self._lock:
            if self._connected:
                return False

            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.connect((host, port))
                print("Connected to server")
                self._connected = True
                self._sender = DataSender(self._sock)
                # Start receiver thread
                if self.on_receive and self._decoder:
                    self._receiver = DataReceiver(
                        self._sock, self._decoder, self.on_receive, self.disconnect
                    )
                    self._receiver.start()
                if self.on_connected is not None:
                    self.on_connected()
                return True
            except Exception as e:
                print(f"Connection failed: {e}")
                if self.on_disconnected is not None:
                    self.on_connected()
                return False

    def disconnect(self):
        with self._lock:
            print("Disconnecting...")
            if self._receiver:
                self._receiver.stop()
                self._receiver = None

            if self._sock:
                self._sock.close()
                self._sock = None
            self._connected = False
            self._sender = None
            if self.on_disconnected is not None:
                self.on_disconnected()

    def send_data(self, data: SerializableData):
        with self._sender_lock:
            if self._sender:
                self._sender.send(data)


def on_receive(decodedData: DecodedData):
    if decodedData.get_name() == STRING_DATA_TYPE:
        print(f"Receive StringData:{decodedData.get_data()}")
    else:
        print(f"Recieve {decodedData.get_name()}")


# TODO connectedはisConnectedを用意してロックを取った方がいいかも
if __name__ == "__main__":

    decoder = MultiTypeDataDecoder({STRING_DATA_TYPE: StringDataDecoder()})
    client = TCPClient(decoder, on_receive, port=51234)
    client.set_on_disconnect(
        lambda: print("Disconnected. Enter something to continue.")
    )
    client.connect()
    try:
        while client._connected:
            user_input = input("Enter message to send (or 'exit'): ")
            if user_input.lower() == "exit":
                break
            client.send_data(StringData(user_input))
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        if client._connected:
            client.disconnect()
