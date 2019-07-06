import os
import xml.etree.ElementTree as ET
from pystatus.plugin import IPlugin, IInstance


class Temperature(IPlugin):
    def __init__(self):
        super().__init__("temperature", "0.1",
                         "g0dscookie", TemperatureInstance)
        self.register_option("path", self._check_path, required=True)
        self.register_option("threshold_warn", float)
        self.register_option("threshold_err", float)

    def _check_path(self, xml: ET.Element) -> str:
        path = xml.text
        if not os.path.exists(path):
            self.log.critical("%s does not exist", path)
            exit(2)
        return path


class TemperatureInstance(IInstance):
    def __init__(self, *args, **kwargs):
        options = {
            "text": "T: {:.0f}°C",
            "path": None,
            "threshold_warn": 40,
            "threshold_err": 50,
            "color": {
                "ok": "#ffffff",
                "warn": "#ffff00",
                "err": "#ff0000",
            },
        }
        super().__init__(*args, options=options, **kwargs)

    def read_temp(self) -> float:
        with open(self._path, "r") as f:
            return int(f.readline().strip()) / 1000

    def get_color(self, temp) -> str:
        if temp >= self._threshold_err:
            return self._color["err"]
        elif temp >= self._threshold_warn:
            return self._color["warn"]
        return self._color["ok"]

    def update(self):
        temp = self.read_temp()
        text = self._text.format(temp)
        with self.block:
            self.block.full_text = self.block.short_text = text
            self.block.color = self.get_color(temp)
