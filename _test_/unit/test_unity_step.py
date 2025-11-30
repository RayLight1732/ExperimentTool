from step.unity_step import PeriodicalSignalSender
from datetime import datetime, timedelta


class TimeController:
    def __init__(self, base_time):
        self.current = base_time

    def now(self):
        return self.current

    def advance(self, seconds):
        self.current += timedelta(seconds=seconds)


# ==========================================================
# 1. sendが正しく呼ばれているかのテスト
# ==========================================================
def test_periodical_signal_sender(mocker):
    base = datetime(2025, 1, 1, 0, 0, 0)
    tc = TimeController(base)

    arduino = mocker.Mock()
    send_log = []

    def send_side_effect(message):
        offset = (tc.current - base).total_seconds()
        send_log.append((offset, message))

    arduino.send.side_effect = send_side_effect

    # datetime の patch を mocker 経由で行う
    patched_dt = mocker.patch("step.unity_step.datetime")
    patched_dt.now.side_effect = tc.now
    patched_dt.timedelta = timedelta

    sender = PeriodicalSignalSender(1, arduino)

    sender.start()

    # 0.5 秒 → まだ送られない
    tc.advance(0.5)
    sender.update()
    assert send_log == []

    # 1 秒 → "high"
    tc.advance(0.5)
    sender.update()
    assert len(send_log) == 1
    assert send_log[0] == (1, "high")

    # 1.5 秒 → 呼ばれない
    tc.advance(0.5)
    sender.update()
    assert len(send_log) == 1

    # 2 秒 → "low"
    tc.advance(0.5)
    sender.update()
    assert len(send_log) == 2
    assert send_log[1] == (2, "low")


def test_unity_step(mocker):
    pass
