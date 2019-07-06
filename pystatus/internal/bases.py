import abc
import xml.etree.ElementTree as ET
from typing import Type
from humanfriendly import parse_size, format_size
from pystatus.plugin import IPlugin, IInstance


class StorAvailPlugin(IPlugin):
    def __init__(self, name: str, version: str,
                 author: str, inst: Type[IInstance]):
        super().__init__(name, version, author, inst)
        self.register_option("threshold_warn", self._xml_parse)
        self.register_option("threshold_err", self._xml_parse)

    def _xml_parse(self, xml: ET.Element) -> int:
        return parse_size(xml.text, binary=True)


class StorAvailInstance(IInstance):
    def __init__(self, *args, **kwargs):
        options = {
            "text": "{}",
            "threshold_err": None,
            "threshold_warn": None,
            "color": {
                "ok": "#ffffff",
                "warn": "#ffff00",
                "err": "#ff0000",
            },
        }
        if "options" in kwargs:
            kopts = kwargs["options"]
            del kwargs["options"]
        else:
            kopts = {}

        for k, v in kopts.items():
            if k == "threshold_err" or k == "threshold_warn":
                try:
                    options[k] = int(v)
                except ValueError:
                    options[k] = parse_size(v)
                continue
            options[k] = v

        super().__init__(*args, options=options, **kwargs)

    @abc.abstractmethod
    def get_available(self) -> int:
        raise NotImplementedError()

    def get_color(self, avail) -> str:
        if avail <= self._threshold_err:
            return self._color["err"]
        if avail <= self._threshold_warn:
            return self._color["warn"]
        return self._color["ok"]

    def update(self):
        avail = self.get_available()
        text = self._text.format(format_size(avail, binary=True))
        with self.block:
            self.block.full_text = self.block.short_text = text
            self.block.color = self.get_color(avail)
