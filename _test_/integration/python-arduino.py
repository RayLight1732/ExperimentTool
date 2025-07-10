from network.tcp_client import TCPClient
from network.simple_serial import ArduinoSerial
from step.unity_step import UnityStepController
from _test_.integration.network.tcp_client_mock import TCPClientMock
import step.util as sutil
from network.data.string_data import StringData
import time

arduino_message = []
class MockUnityStepController(UnityStepController):
    def on_arduino_receive(self, msg: str):
        global arduino_message
        arduino_message.append(msg)


if __name__ == "__main__":
    condition = sutil.calc_condition(0,0)
    unity_client = TCPClientMock()
    arduino_client = ArduinoSerial(port="COM3")
    controller = MockUnityStepController(unity_client,arduino_client,condition)
    controller.connect_arduino()
    unity_client.on_receive(StringData("start"))
    unity_client.on_receive(StringData("high"))
    unity_client.on_receive(StringData("low"))
    unity_client.on_receive(StringData("end"))
    result = ["mode:0","position:0","all off"]

    arduino_message = []
    condition = sutil.calc_condition(1,1)
    unity_client = TCPClientMock()
    arduino_client = ArduinoSerial(port="COM3")
    controller = MockUnityStepController(unity_client,arduino_client,condition)
    controller.connect_arduino()
    unity_client.on_receive(StringData("start"))
    unity_client.on_receive(StringData("high"))
    unity_client.on_receive(StringData("low"))
    unity_client.on_receive(StringData("end"))
    result = ["mode:1","position:1","back on","all off"]
    #TODO 値の検証