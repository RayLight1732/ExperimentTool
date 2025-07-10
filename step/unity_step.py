import tkinter as tk
from tkinter import ttk
from typing import Callable
from step.step import Step
from network.data.multi_type_data_decoder import MultiTypeDataDecoder
from network.data.string_data import STRING_DATA_TYPE, StringDataDecoder, StringData
from network.tcp_client import TCPClient
from network.data.data_decoder import DecodedData
from network.simple_serial import ArduinoSerial


class UnityStepUI:
    def __init__(self, container: ttk.Frame):
        self.container = container
        self.ip_entry = None
        self.port_entry = None
        self.connect_button = None
        self.arduino_connect_button = None
        self.start_button = None
        self.started_text = None

    def build(self, on_connect_unity, on_connect_arduino, on_start):
        ttk.Label(self.container, text="IPアドレス").pack(side="top")

        self.ip_var = tk.StringVar()
        self.ip_var.trace_add("write", self._validate_ip_port)
        self.ip_entry = ttk.Entry(self.container, textvariable=self.ip_var)

        self.ip_entry.pack(pady=(0, 10), side="top")

        # port: 数字のみを許可する validatecommand の設定
        ttk.Label(self.container, text="ポート番号").pack(side="top")
        vcmd = (self.container.register(self._validate_port_entry), "%P")

        self.port_var = tk.StringVar()
        self.port_var.trace_add("write", self._validate_ip_port)
        self.port_entry = ttk.Entry(
            self.container,
            textvariable=self.port_var,
            validate="key",
            validatecommand=vcmd,
        )
        self.port_entry.pack(pady=(0, 10), side="top")

        self.connect_button = ttk.Button(
            self.container,
            text="Unityに接続",
            command=on_connect_unity,
            state="disabled",
        )
        self.connect_button.pack(side="top")

        self.arduino_connect_button = ttk.Button(
            self.container, text="Arduinoに接続", command=on_connect_arduino
        )
        self.arduino_connect_button.pack(side="top")

        self.start_button = ttk.Button(
            self.container, text="開始", state="disabled", command=on_start
        )
        self.start_button.pack(side="top")

        self.ip_entry.insert(0, "127.0.0.1")
        self.port_entry.insert(0, "51234")

    def _validate_port_entry(self, new_value):
        return new_value == "" or new_value.isdigit()

    def _validate_ip_port(self, *args):
        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()
        if ip and port:
            self.connect_button["state"] = "normal"
        else:
            self.connect_button["state"] = "disabled"

    def get_ip(self):
        return self.ip_var.get()

    def get_port(self):
        return int(self.port_var.get()) if self.port_var.get().isdigit() else None

    def set_unity_status(self, connected: bool):
        self.connect_button["text"] = "Unityに接続済" if connected else "Unityに接続"

    def set_arduino_status(self, connected: bool):
        self.arduino_connect_button["text"] = (
            "Arduinoに接続済" if connected else "Arduinoに接続"
        )

    def set_start_button_enabled(self, enabled: bool):
        self.start_button["state"] = "normal" if enabled else "disabled"

    def show_started(self):
        if self.started_text is None:
            self.started_text = tk.Label(self.container, text="実験中")
            self.started_text.pack(pady=20)

    def show_finished(self):
        if self.started_text:
            self.started_text.destroy()
        tk.Label(self.container, text="終了しました").pack(pady=20)

    def destroy_start_button(self):
        self.start_button.destroy()


class UnityStepController:
    def __init__(
        self, unity_client: TCPClient, arduino_client: ArduinoSerial, condition: int
    ):
        self.unity_client = unity_client
        self.arduino_client = arduino_client
        self.condition = condition
        self.on_started = None
        self.on_finished = None

        self.unity_client.on_receive = self.on_receive
        self.unity_client.on_connected = self._on_unity_connected
        self.unity_client.on_disconnected = self._on_unity_disconnected

        self.arduino_client.on_receive = self.on_arduino_receive
        self.arduino_client.on_connected = self._on_arduino_connected
        self.arduino_client.on_disconnected = self._on_arduino_disconnected

        self.on_status_change = None  # 状態変化時のUI更新用

    def connect_unity(self, ip: str, port: int):
        if not self.unity_client.connected:
            self.unity_client.connect(ip, port)

    def connect_arduino(self):
        if not self.arduino_client.connected:
            self.arduino_client.connect()

    def can_start(self):
        return self.arduino_client.connected and self.unity_client.connected

    def start(self):
        self.arduino_client.send("start")
        # TODO MultiType dataに変更
        self.unity_client.send_data(StringData("start"))

    def _on_unity_connected(self):
        if self.on_status_change:
            self.on_status_change()

    def _on_unity_disconnected(self):
        if self.on_status_change:
            self.on_status_change()

    def _on_arduino_connected(self):
        if self.on_status_change:
            self.on_status_change()

    def _on_arduino_disconnected(self):
        if self.on_status_change:
            self.on_status_change()

    def on_receive(self, decodedData: DecodedData):
        if decodedData.get_name() == STRING_DATA_TYPE:
            message = decodedData.get_data()
            if message == "end":
                self.arduino_client.send("end")
                if self.on_finished:
                    self.on_finished()
            elif message == "started":
                self.arduino_client.send(f"mode{self.condition}")
                self.arduino_client.send("start")
                if self.on_started:
                    self.on_started()
            elif message == "high":
                self.arduino_client.send("high")
            elif message == "low":
                self.arduino_client.send("low")
        else:
            print(f"Receive {decodedData.get_name()}")

    def on_arduino_receive(self, msg: str):
        print(f"receive: {msg}")

    def dispose(self):
        self.unity_client.disconnect()
        self.arduino_client.disconnect()


class UnityStep(Step):
    def __init__(
        self,
        container: ttk.Frame,
        set_complete: Callable[[bool], None],
        step_ui: UnityStepUI,
        controller: UnityStepController,
    ):
        super().__init__(container, set_complete)

        self.ui = step_ui
        self.controller = controller
        self.set_complete = set_complete

        self.controller.on_started = self.ui.show_started
        self.controller.on_finished = self._on_finished
        self.controller.on_status_change = self._update_status

    def build(self):
        self.ui.build(
            on_connect_unity=self._connect_unity,
            on_connect_arduino=self._connect_arduino,
            on_start=self._start,
        )

    def _connect_unity(self):
        ip = self.ui.get_ip()
        port = self.ui.get_port()
        self.controller.connect_unity(ip, port)

    def _connect_arduino(self):
        self.controller.connect_arduino()

    def _start(self):
        self.controller.start()
        self.ui.destroy_start_button()

    def _update_status(self):
        self.ui.set_unity_status(self.controller.unity_client.connected)
        self.ui.set_arduino_status(self.controller.arduino_client.connected)
        self.ui.set_start_button_enabled(self.controller.can_start())

    def _on_finished(self):
        self.ui.show_finished()
        self.set_complete(True)

    def on_dispose(self):
        self.controller.dispose()

    def before_next(self):
        pass


class UnityStepFactory:
    def __init__(self, data_container: dict):
        self.data_container = data_container

    def create(self, frame: ttk.Frame, set_complete: Callable[[bool], None]) -> Step:
        condition = self.data_container["condition"]
        ui = UnityStepUI(frame)
        decoder = MultiTypeDataDecoder({STRING_DATA_TYPE: StringDataDecoder()})
        unity_client = TCPClient(decoder)
        arduino_client = ArduinoSerial(port="COM3")
        controller = UnityStepController(unity_client, arduino_client, condition)
        print(type(frame))
        return UnityStep(frame, set_complete, ui, controller)
