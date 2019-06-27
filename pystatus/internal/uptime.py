from datetime import datetime, timedelta
from time import time
from psutil import boot_time
from pystatus.plugin import IPlugin, IInstance


class Uptime(IPlugin):
    def __init__(self):
        super().__init__("uptime", "0.1", "g0dsCookie", UptimeInstance)


class UptimeInstance(IInstance):
    def __init__(self, *args, **kwargs):
        options = {"text": "U: %s"}
        super().__init__(*args, options=options, **kwargs)

    def _get_uptime(self) -> timedelta:
        current = datetime.fromtimestamp(int(time()))
        return current - datetime.fromtimestamp(boot_time())

    def update(self):
        with self.block:
            self.block.full_text = self.block.short_text \
                = self._text % self._get_uptime()
