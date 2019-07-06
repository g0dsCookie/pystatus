from enum import Enum
import xml.etree.ElementTree as ET
from typing import List, Tuple
from psutil import virtual_memory, swap_memory
from humanfriendly import parse_size, format_size
from .bases import StorAvailPlugin, StorAvailInstance


class MemorySource(Enum):
    RAM = 1
    SWAP = 2


class Memory(StorAvailPlugin):
    def __init__(self):
        super().__init__("memory", "0.1", "g0dsCookie", MemoryInstance)
        self.register_option("source", self._xml_source)

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


class MemoryInstance(StorAvailInstance):
    def __init__(self, *args, **kwargs):
        options = {"source": MemorySource.RAM}
        super().__init__(*args, options=options, **kwargs)

        mem = self._get_total()
        if not self._threshold_warn:
            self._threshold_warn = mem * 0.4
        if not self._threshold_err:
            self._threshold_err = mem * 0.1

    def _get_total(self) -> int:
        if self._source == MemorySource.RAM:
            return virtual_memory().total
        elif self._source == MemorySource.SWAP:
            return swap_memory().total
        raise ValueError("Unknown memory source %s" % self._source)

    def get_available(self):
        if self._source == MemorySource.RAM:
            return virtual_memory().available
        elif self._source == MemorySource.SWAP:
            return virtual_memory().available
        raise ValueError("Unknown memory source %s" % self._source)
