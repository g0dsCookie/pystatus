from time import strftime, localtime
from pystatus.plugin import IPlugin, IInstance


class Clock(IPlugin):
    def __init__(self):
        super().__init__("clock", "0.1", "g0dsCookie", ClockInstance)


class ClockInstance(IInstance):
    def __init__(self, *args, **kwargs):
        options = {
            "text": "%Y-%m-%d %H:%M:%S",
            "short": "%H:%M:%S",
        }
        super().__init__(*args, options=options, **kwargs)

    def update(self):
        time = localtime()
        with self.block:
            if self._text:
                self.block.full_text = strftime(self._text, time)
            if self._short:
                self.block.short_text = strftime(self._short, time)
