import logging
import xml.etree.ElementTree as ET
from typing import Union, Callable, List


def _xml_int(xml: ET.Element) -> int:
    return int(xml.text)


def _xml_text(xml: ET.Element) -> str:
    return xml.text


def _xml_bool(xml: ET.Element) -> bool:
    return xml.text.lower() in ["1", "true"]


def _xml_color(xml: ET.Element) -> Union[str, dict]:
    single = _xml_single_color(xml)
    if single:
        return single
    colors = {}
    for child in xml:
        single = _xml_single_color(child)
        colors[child.tag] = single
    return colors


def _xml_single_color(xml: ET.Element) -> str:
    if xml.text.startswith("#"):
        return xml.text
    r, g, b = xml.get("r"), xml.get("g"), xml.get("b")
    if not r or not g or not b:
        return None
    return "#%02x%02x%02x" % (r, g, b)


class Block:
    VARS_BANNED = [
        "plugin",
        "name",
        "interval"
    ]

    _BLOCK_OPTIONS = {
        "interval": _xml_int,
        "color": _xml_color,
        "background": _xml_color,
        "border": _xml_single_color,
        "separator": _xml_bool,
        "separator_block_width": _xml_int,
    }

    _PLUGIN_OPTIONS = {
    }

    log = logging.getLogger("Block")

    def __init__(self, xml: ET.Element):
        if xml.tag != "block":
            self.log.critical("Invalid section name for Block: %s", xml.tag)
            exit(2)

        self.plugin = xml.get("plugin")
        self.name = xml.get("name")
        if not self.name:
            self.name = self.plugin

        self.interval = 1

        for child in xml:
            p = self._get_option_fn(child.tag)
            setattr(self, child.tag, p(child))

    def _get_option_fn(self, name: str) -> Callable:
        if (self.plugin in self._PLUGIN_OPTIONS
                and name in self._PLUGIN_OPTIONS[self.plugin]):
            return self._PLUGIN_OPTIONS[self.plugin][name]
        return self._BLOCK_OPTIONS.get(name, _xml_text)

    @staticmethod
    def _normalize_option_fn(fn: Union[type, Callable]) -> Callable:
        if fn == int:
            return _xml_int
        elif fn == bool:
            return _xml_bool
        return fn

    @staticmethod
    def register_option(plugin: str, name: str,
                        fn: Union[type, Callable]) -> None:
        fn = Block._normalize_option_fn(fn)
        Block.log.debug("Registering option %s for %s", name, plugin)
        if plugin not in Block._PLUGIN_OPTIONS:
            Block._PLUGIN_OPTIONS[plugin] = {name: fn}
            return
        if name in Block._PLUGIN_OPTIONS[plugin]:
            Block.log.warn("Overwriting option %s for %s", name, plugin)
        Block._PLUGIN_OPTIONS[plugin][name] = fn

    def options(self) -> dict:
        return {k: v for k, v in vars(self).items()
                if v and k not in Block.VARS_BANNED}


class Config:
    def __init__(self):
        self._log = logging.getLogger("Config")
        self._blocks = []

    @property
    def blocks(self) -> List[Block]:
        return self._blocks

    @property
    def log(self) -> logging.Logger:
        return self._log

    def _load_blocks(self, blocks: ET.Element) -> None:
        if not blocks:
            self.log.critical("Missing blocks section in config.")
            exit(2)
        self._blocks = list([Block(xml) for xml in blocks])

    def load(self, file: str):
        tree = ET.parse(file)
        root = tree.getroot()
        if root.tag != "pystatus":
            self.log.critical("Configuration doesn't start with pystatus")
            exit(2)
        for child in root:
            if child.tag == "blocks":
                self._load_blocks(child)
