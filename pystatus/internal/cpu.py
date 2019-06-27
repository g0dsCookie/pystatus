from psutil import cpu_percent, cpu_count
from pystatus.plugin import IPlugin, IInstance


class CPU(IPlugin):
    def __init__(self):
        super().__init__("cpu", "0.1", "g0dscookie", CPUInstance)
        self.register_option("threshold_warn", int)
        self.register_option("threshold_err", int)
        self.register_option("cpu", int)


class CPUInstance(IInstance):
    def __init__(self, *args, **kwargs):
        options = {
            "text": "C: {:.1f}%",
            "threshold_warn": 80,
            "threshold_err": 90,
            "cpu": -1,
            "color": None,
        }
        super().__init__(*args, options=options, **kwargs)

        if self._cpu >= 0:
            count = cpu_count()
            if self._cpu > count:
                self.log.critical("Unknown cpu core with number %d", self._cpu)
                exit(2)
        if not self._color:
            self._color = {
                "ok": "#ffffff",
                "warn": "#ffff00",
                "err": "#ff0000",
            }

        # first call may return 0.0 per documentation
        # so we simply ignore this
        self._get_percent()

    def _get_percent(self):
        if self._cpu >= 0:
            return cpu_percent(percpu=True)[self._cpu]
        return cpu_percent()

    def _get_color(self, perc):
        if perc > self._threshold_err:
            return self._color["err"]
        elif perc > self._threshold_warn:
            return self._color["warn"]
        return self._color["ok"]

    def update(self):
        perc = self._get_percent()
        text = self._text.format(perc)
        with self.block:
            self.block.full_text = self.block.short_text = text
            self.block.color = self._get_color(perc)
