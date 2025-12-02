import serial
import serial.tools.list_ports
import threading
import time
from typing import Optional, Callable


class DataReceiver(threading.Thread):
    def __init__(
        self,
        serial_prot: serial.Serial,
        on_receive: Callable[[str], None],
        on_failed: Callable[[], None],
    ):
        super().__init__(daemon=True)
        self.running = True
        self.serial_port = serial_prot
        self.on_receive = on_receive
        self.on_failed = on_failed

    def run(self):
        while self.running:
            try:
                line = self.serial_port.readline().decode(errors="ignore").strip()
                if line:
                    print(f"[RECV] {line}")
            except Exception:
                if self.running:
                    self.on_failed()
                break

    def stop(self):
        self.running = False


class PingSender(threading.Thread):
    def __init__(self, send: Callable[[str, bool], None]):
        super().__init__(daemon=True)
        self.send = send
        self.running = True

    def run(self):
        while self.running:
            try:
                self.send("ping", False)
                time.sleep(0.01)  # 10ms
            except Exception:
                pass

    def stop(self):
        self.running = False


class ArduinoSerial:
    def __init__(self, baudrate=115200, port=None):
        self.baudrate = baudrate
        self.serial_port = None
        self.lock = threading.Lock()
        self.port = port
        self._receiver: Optional[DataReceiver] = None
        self._ping_sender: Optional[PingSender] = None
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None
        self.on_receive: Optional[Callable[[str], None]] = None
        self._connected = False

    def list_ports(self):
        return [
            (port.description.lower(), port.device)
            for port in serial.tools.list_ports.comports()
        ]

    def find_arduino_port(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            desc = port.description.lower()
            if any(
                keyword in desc
                for keyword in ["arduino", "ch340", "usb-serial", "user-serial"]
            ):
                print(
                    f"[INFO] Found candidate port: {port.device} ({port.description})"
                )
                return port.device
        return None

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self) -> bool:
        if self.connected:
            return False
        if self.port:
            port = self.port
        else:
            port = self.find_arduino_port()
        if port:
            try:
                self.serial_port = serial.Serial(port, self.baudrate, timeout=1)
                print(f"[INFO] Connected to {port}")
                self._receiver = DataReceiver(
                    self.serial_port, self.on_receive, self.disconnect
                )
                self._receiver.start()
                self._ping_sender = PingSender(self.send)
                self._ping_sender.start()
                self._connected = True
                if self.on_connected is not None:
                    self.on_connected()
                return True
            except Exception as e:
                print(f"[ERROR] Could not open {port}: {e}")
                self.on_disconnected()
        return False

    def send(self, msg: str, debug: bool = True):
        with self.lock:
            if self.connected:
                try:
                    self.serial_port.write((msg + "\n").encode())
                    if debug:
                        print(f"[SEND] {msg}")
                except serial.SerialException:
                    print("[ERROR] Failed to send, port might be closed.")

    def disconnect(self):
        if self.serial_port:
            self._connected = False
            self._receiver.stop()
            self._receiver = None
            self._ping_sender.stop()
            self._ping_sender = None
            try:
                self.serial_port.close()
                print("[INFO] Serial port closed.")
            except:
                pass
            self.serial_port = None
            if self.on_disconnected is not None:
                self.on_disconnected()

class ArduinoSerialMock:
    def __init__(self, baudrate=115200, port=None):
        self.baudrate = baudrate
        self.serial_port = None
        self.lock = threading.Lock()
        self.port = port
        self._receiver: Optional[DataReceiver] = None
        self._ping_sender: Optional[PingSender] = None
        self.on_connected: Optional[Callable[[], None]] = None
        self.on_disconnected: Optional[Callable[[], None]] = None
        self.on_receive: Optional[Callable[[str], None]] = None
        self._connected = False    

    def list_ports(self):
        return []

    def find_arduino_port(self):
        return None

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self) -> bool:
        if not self._connected:
            self._connected = True
            print("connect to arduino")
            if self.on_connected is not None:
                self.on_connected()
            return True
        else:
            print("failed to connect to arduino: already connected")
            return False

    def send(self, msg: str, debug: bool = True):
        if self._connected:
            print(f"successded to send message to arduino: {msg}")
        else:
            print("failed to send message to arduino: not connected")

    def disconnect(self):
        if self._connected:
            print("disconnected from aduino")
            if self.on_disconnected is not None:
                self.on_disconnected()
        else:
            print("failed to disconnected fro arduino: not connectedd")

# --- 実行例 ---
if __name__ == "__main__":
    # arduino = ArduinoSerial(port="COM3")
    # arduino.connect()
    # try:
    #     while True:
    #         user_input = input("Enter message to send (or 'exit'): ")
    #         if user_input.lower() == "exit":
    #             break
    #         arduino.send(user_input)
    # except KeyboardInterrupt:
    #     print("\n[INFO] Interrupted by user.")
    # finally:
    #     arduino.disconnect()
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        desc = port.description.lower()
        print(desc, port.device)
