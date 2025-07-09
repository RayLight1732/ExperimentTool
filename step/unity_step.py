import tkinter as tk
from tkinter import ttk
from typing import Callable
from step.step import Step
from network.data.multi_type_data_decoder import MultiTypeDataDecoder
from network.data.string_data import STRING_DATA_TYPE, StringDataDecoder, StringData
from network.tcp_client import TCPClient
from network.data.data_decoder import DecodedData
from network.simple_serial import ArduinoSerial


class UnityStep(Step):
    def __init__(
        self,
        container: ttk.Frame,
        set_complete: Callable[[bool], None],
        condition: int,
        unity_client: TCPClient,
        arduino_client: ArduinoSerial,
    ):
        super().__init__(container, set_complete)
        self.set_complete = set_complete

        self.condition = condition

        self.unity_client = unity_client
        self.unity_client.on_receive = self.on_receive
        self.unity_client.on_disconnected = self.on_unity_disconnected
        self.unity_client.on_connected = self.on_unity_connected

        self.arduino_client = arduino_client
        self.arduino_client.on_disconnected = self.on_arduino_disconnected
        self.arduino_client.on_receive = self.on_arduino_receive
        self.arduino_client.on_connected = self.on_arduino_connected

        self.start_button = None
        self.started_text = None

    def build(self):
        ttk.Label(self.container, text="ipアドレス").pack(side="top")
        self.ip_entry = ttk.Entry(self.container)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(pady=(0, 10), side="top")
        self.connect_button = ttk.Button(
            master=self.container,
            command=self.try_connect_unity,
            text="Unityに接続",
        )
        self.connect_button.pack(side="top")
        self.arduino_connect_button = ttk.Button(
            master=self.container,
            command=self.try_connect_arduino,
            text="Arduinoに接続",
        )
        self.arduino_connect_button.pack(side="top")

        self.start_button = ttk.Button(
            master=self.container,
            text="開始",
            state="disabled",
            command=self.on_start_button_pressed,
        )
        self.start_button.pack(side="top")

        self.high_low_test_button = ttk.Button(
            master=self.container,
            text="ToHigh",
            command=self._on_high_low_test_button_pressed,
        )
        self.high_low_test_button.pack(side="top")
        self.to_high = True

    def _on_high_low_test_button_pressed(self):
        if self.arduino_client.connected:

            if self.to_high:
                self.arduino_client.send("high")
                new_text = "ToLow"
            else:
                self.arduino_client.send("low")
                new_text = "ToHigh"

            self.high_low_test_button["text"] = new_text
            self.to_high = not self.to_high

    # TODO 非同期にする
    def try_connect_unity(self):
        if not self.unity_client.connected:
            ip = self.ip_entry.get()
            self.connect_button["text"] = "Unityに接続中"
            self.unity_client.connect(host=ip, port=51234)

    # TODO 非同期にする
    def try_connect_arduino(self):
        if not self.arduino_client.connected:
            self.arduino_connect_button["text"] = "Arduinoに接続中"
            self.arduino_client.connect()

    def on_unity_connected(self):
        self._update_start_button_state()
        self.connect_button["text"] = "Unityに接続済"

    def on_unity_disconnected(self):
        self._update_start_button_state()
        self.connect_button["text"] = "Unityに接続"

    def on_arduino_connected(self):
        self._update_start_button_state()
        self.arduino_connect_button["text"] = "Arduinoに接続済"

    def on_arduino_disconnected(self):
        self._update_start_button_state()
        self.arduino_connect_button["text"] = "Arduinoに接続"

    def _can_start(self):
        return self.arduino_client.connected and self.unity_client.connected

    def _update_start_button_state(self):
        state = "normal" if self._can_start() else "disabled"
        self.start_button.config(state=state)

    def on_start_button_pressed(self):
        self.unity_client.send_data(StringData("start"))
        self.start_button.destroy()

    def on_dispose(self):
        self.unity_client.disconnect()
        self.arduino_client.disconnect()

    def before_next(self):
        pass

    def _on_remote_start(self):
        if self.started_text is None:
            self.started_text = tk.Label(self.container, text="実験中")
            self.started_text.pack(pady=20)

    def on_receive(self, decodedData: DecodedData):
        if decodedData.get_name() == STRING_DATA_TYPE:
            print(f"Receive StringData:{decodedData.get_data()}")
            message = decodedData.get_data()
            if message == "end":
                self._on_end()
            elif message == "started":
                self._on_remote_start()
            elif message == "high":
                self.arduino_client.send(f"high{self.condition}\n")
            elif message == "low":
                self.arduino_client.send("low\n")
        else:
            print(f"Recieve {decodedData.get_name()}")

    def on_arduino_receive(self, msg: str):
        print(f"receive:{msg}")

    def _on_end(self):
        self.started_text.destroy()
        tk.Label(self.container, text="終了しました").pack(pady=20)
        self.set_complete(True)


class UnityStepFactory:
    def __init__(self, data_container: dict):
        self.data_container = data_container

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> Step:
        condition = self.data_container["condition"]
        decoder = MultiTypeDataDecoder({STRING_DATA_TYPE: StringDataDecoder()})
        unity_client = TCPClient(decoder)
        arduino_client = ArduinoSerial(port="COM3")
        return UnityStep(frame, set_complete, condition, unity_client, arduino_client)
