from enum import Enum
import xml.etree.ElementTree as ET
from typing import List, Tuple
from psutil import virtual_memory, swap_memory
from humanfriendly import parse_size, format_size
from pystatus.plugin import IPlugin, IInstance


class MemorySource(Enum):
    AVAILABLE = 1
    USED = 2


class MemoryType(Enum):
    RAM = 1
    SWAP = 2


class Memory(IPlugin):
    def __init__(self):
        super().__init__("memory", "0.1", "g0dsCookie", MemoryInstance)
        self.register_option("threshold_warn", self._xml_parse)
        self.register_option("threshold_err", self._xml_parse)
        self.register_option("source", self._xml_source)
        self.register_option("type", self._xml_type)

    def _xml_parse(self, xml: ET.Element) -> int:
        return parse_size(xml.text, binary=True)

    def _xml_source(self, xml: ET.Element) -> MemorySource:
        try:
            i = int(xml.text)
        except ValueError:
            try:
                return MemorySource[xml.text.upper()]
            except KeyError:
                self.log.critical("Invalid memory source %s", xml.text)
                exit(2)
        try:
            return MemorySource(i)
        except ValueError:
            self.log.critical("Invalid memory source %d", i)
            exit(2)

    def _xml_type(self, xml: ET.Element) -> MemoryType:
        try:
            i = int(xml.text)
        except ValueError:
            try:
                return MemoryType[xml.text.upper()]
            except KeyError:
                self.log.critical("Invalid memory type %s", xml.text)
                exit(2)
        try:
            return MemoryType(i)
        except ValueError:
            self.log.critical("Invalid memory type %d", i)
            exit(2)


class MemoryInstance(IInstance):
    def __init__(self, *args, **kwargs):
        options = {
            "text": "M: {}",
            "source": MemorySource.AVAILABLE,
            "type": MemoryType.RAM,
            "threshold_warn": None,
            "threshold_err": None,
            "color": None,
        }
        super().__init__(*args, options=options, **kwargs)

        mem = self._get_mem()[0]
        if self._source == MemorySource.AVAILABLE:
            if not self._threshold_warn:
                self._threshold_warn = mem * 0.4
            if not self._threshold_err:
                self._threshold_err = mem * 0.1
        elif self._source == MemorySource.USED:
            if not self._threshold_warn:
                self._threshold_warn = mem * 0.6
            if not self._threshold_err:
                self._threshold_err = mem * 0.9

        if not self._color:
            self._color = {
                "ok": "#ffffff",
                "warn": "#ffff00",
                "err": "#ff0000",
            }

    def _get_swap(self) -> List[int]:
        mem = swap_memory()
        return [mem.total, mem.free, mem.used]

    def _get_ram(self) -> List[int]:
        mem = virtual_memory()
        return [mem.total, mem.available, mem.used]

    def _get_mem(self) -> List[int]:
        if self._type == MemoryType.RAM:
            return self._get_ram()
        elif self._type == MemoryType.SWAP:
            return self._get_swap()
        else:
            raise ValueError("Unknown memory type %s" % self._type)

    def _color_available(self, avail: int) -> str:
        if avail <= self._threshold_err:
            return self._color["err"]
        if avail <= self._threshold_warn:
            return self._color["warn"]
        return self._color["ok"]

    def _color_used(self, used: int) -> str:
        if used >= self._threshold_err:
            return self._color["err"]
        if used >= self._threshold_warn:
            return self._color["warn"]
        return self._color["ok"]

    def _check_mem(self) -> Tuple[int, str]:
        mem = self._get_mem()
        if self._source == MemorySource.AVAILABLE:
            return (mem[1], self._color_available(mem[1]))
        elif self._source == MemorySource.USED:
            return (mem[2], self._color_used(mem[2]))
        else:
            raise ValueError("Unknown memory source %s" % self._source)

    def update(self):
        mem, color = self._check_mem()
        text = self._text.format(format_size(mem, binary=True))
        with self.block:
            self.block.full_text = self.block.short_text = text
            self.block.color = color
