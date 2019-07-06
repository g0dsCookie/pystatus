from pystatus.plugin import IPlugin, IInstance


class Battery(IPlugin):
    def __init__(self):
        super().__init__("battery", "0.1", "g0dscookie", BatteryInstance)
        self.register_option("threshold_warn", int)
        self.register_option("threshold_crit", int)


class BatteryInstance(IInstance):
    def __init__(self, *args, **kwargs):
        options = {
            "text": "B: {}%",
            "threshold_warn": 30,
            "threshold_crit": 15,
            "color": {
                "ok": "#ffffff",
                "warn": "#ffff00",
                "crit": "#ff0000",
                "charge": "#00ff00",
            }
        }
        super().__init__(*args, options=options, **kwargs)

    @property
    def is_charging(self) -> bool:
        with open("/sys/class/power_supply/ACAD/online", "r") as f:
            return bool(int(f.read()))

    @property
    def charge(self) -> int:
        with open("/sys/class/power_supply/BAT1/capacity", "r") as f:
            return int(f.readline().strip())

    def get_color(self, charge: int, is_charging: bool) -> str:
        if is_charging:
            return self._color["charge"]
        elif charge <= self._threshold_crit:
            return self._color["crit"]
        elif charge <= self._threshold_warn:
            return self._color["warn"]
        return self._color["ok"]

    def update(self):
        is_charging = self.is_charging
        charge = self.charge
        text = self._text.format(charge)
        with self.block:
            self.block.full_text = self.block.short_text = text
            self.block.color = self.get_color(charge, is_charging)
