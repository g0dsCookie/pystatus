from psutil import getloadavg
from pystatus.plugin import IPlugin, IInstance


class Loadavg(IPlugin):
    def __init__(self):
        super().__init__("loadavg", "0.1", "g0dsCookie", LoadavgInstance)


class LoadavgInstance(IInstance):
    def __init__(self, *args, **kwargs):
        options = {
            "text": "L: {:.2f} {:.2f} {:.2f}",
            "short": "L: {0:.2f}",
        }
        super().__init__(*args, options=options, **kwargs)

    def update(self):
        avg = getloadavg()
        with self.block:
            if self._text:
                self.block.full_text = self._text.format(*avg)
            if self._short:
                self.block.short_text = self._short.format(*avg)
