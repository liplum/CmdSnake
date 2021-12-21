from time import time, sleep


def now_milisecs() -> int:
    return int(round(time() * 1000))


def now_seconds() -> float:
    return time()


class timer:
    def __init__(self, seconds: float):
        self.time = seconds

    @staticmethod
    def byMilisecs(milisecs: int):
        return timer(milisecs / 1000)

    @staticmethod
    def byFps(fps: int):
        return timer(1 / fps)

    def reset(self):
        self.start_time = now_seconds()

    def delay(self):
        cur_time = now_seconds()
        duration = cur_time - self.start_time
        interval = duration - self.time
        if interval > 0:
            sleep(interval)
        self.reset()

    @property
    def is_end(self) -> bool:
        cur_time = now_seconds()
        duration = cur_time - self.start_time
        interval = duration - self.time
        if interval >= 0:
            return True
        else:
            return False
