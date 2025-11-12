from network.simple_serial import ArduinoSerial
import step.util as sutil
import time
def test_arduino():
    condition = sutil.calc_condition(2,1)
    client = ArduinoSerial(port="COM3")
    if client.connect():
        try:
            client.send(f"mode{condition}")
            client.send("start")
            client.send("high")
            while True:
                time.sleep(1)
        finally:
            client.send("end")
        

if __name__ == "__main__":
    test_arduino()
