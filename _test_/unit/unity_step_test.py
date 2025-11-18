from step.unity_step import UnityStep,PeriodicalSignalSender
import step.util as sutil
from time import time,sleep
from types import MethodType
def MockUnityStepUI():
    pass

def MockUnityStepController():
    pass

def MockSoundPlater():
    pass

def MockPeriodicalSignalSender():
    pass

def MockFrame():
    pass

class ArduinoMock:
    def send(self,message):
        pass

def test_step():
    container = {"condition":sutil.calc_condition(3,1)}
    completed = False
    def set_complete(f:bool):
        completed = f

    def save_ip_port(ip:str,port:int):
        pass

    ui = MockUnityStepUI()
    controller = MockUnityStepController()
    player = MockSoundPlater()
    sender = MockPeriodicalSignalSender()
    frame = MockFrame()
    step = UnityStep(set_complete,ui,controller,save_ip_port,player,sender,frame)
    step.build()
    step._start()
    step._on_started()
    step._update_status()
    
def test_periodical_signal_sender():
    period = []
    start = time()
    arduino = ArduinoMock()
    def send(self,message):
        period.append((time()-start,message))
        print("send")
    arduino.send = MethodType(send,arduino)
    
    sender = PeriodicalSignalSender(1,arduino)
    sender.start()
    while time()-start <= 6.5:
        sender.update()
        sleep(0.1)
    sender.stop()
    delta = 0.05
    assert len(period) == 6
    print(period)
    for t in range(1,7):
        target = period[t-1]
        assert t-delta < target[0]
        assert target[0] < t+delta
        if t % 2 == 1:
            assert target[1] == "high"
        else:
            assert target[1] == "low"
