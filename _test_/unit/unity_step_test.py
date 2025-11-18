from step.unity_step import PeriodicalSignalSender
from datetime import datetime, timedelta
from unittest.mock import Mock, patch


class TimeController:
    def __init__(self, base_time):
        self.current = base_time

    def now(self):
        return self.current

    def advance(self, seconds):
        self.current += timedelta(seconds=seconds)


# ==========================================================
# 1. 不要な時間に send が呼ばれていないかの確認
# ==========================================================
def test_periodical_signal_sender():
    base = datetime(2025, 1, 1, 0, 0, 0)
    tc = TimeController(base)

    arduino = Mock()
    send_log = []

    def send_side_effect(message):
        offset = (tc.current - base).total_seconds()
        send_log.append((offset, message))

    arduino.send.side_effect = send_side_effect

    sender = PeriodicalSignalSender(1, arduino)

    with patch("step.unity_step.datetime") as md:
        md.now.side_effect = tc.now
        md.timedelta = timedelta

        sender.start()

        # 0.5秒後（まだ period に達していない）
        tc.advance(0.5)
        sender.update()
        assert send_log == []  # 呼ばれてはいけない

        # 1秒後
        tc.advance(0.5)
        sender.update()
        assert len(send_log) == 1
        assert send_log[0][0] == 1
        assert send_log[0][1] == "high"

        # 1.5秒後（呼ばれない）
        tc.advance(0.5)
        sender.update()
        assert len(send_log) == 1

        # 2秒後（2回目）
        tc.advance(0.5)
        sender.update()
        assert len(send_log) == 2
        assert send_log[1][0] == 2
        assert send_log[1][1] == "low"
