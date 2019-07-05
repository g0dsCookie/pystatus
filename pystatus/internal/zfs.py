import os
import logging
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
from humanfriendly import parse_size, format_size
from pystatus.i3bar import Block
from pystatus.plugin import IPlugin, IInstance


def _check_path(path: str, log: logging.Logger):
    p = Popen([path, "version"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    if p.returncode != 0:
        log.critical("'%s version' returned non-zero exit code %d",
                     path, p.returncode)
        exit(p.returncode)


class ZFS(IPlugin):
    def __init__(self):
        super().__init__("zfs", "0.1", "g0dscookie", ZFSInstance)
        self.register_option("zfs", self._check_path)
        self.register_option("dataset", str, required=True)
        self.register_option("threshold_warn", self._xml_parse)
        self.register_option("threshold_err", self._xml_parse)

    def _xml_parse(self, xml: ET.Element) -> int:
        return parse_size(xml.text, binary=True)

    def _check_path(self, xml: ET.Element) -> str:
        path = xml.text
        _check_path(path, self.log)
        return path


class ZFSInstance(IInstance):
    PATHS = [
        "/sbin", "/usr/sbin", "/usr/local/sbin",
        "/bin", "/usr/bin", "/usr/local/bin",
    ]

    def __init__(self, *args, **kwargs):
        options = {
            "text": "Z: {}",
            "zfs": None,
            "dataset": None,
            "threshold_warn": None,
            "threshold_err": None,
            "color": None,
        }
        super().__init__(*args, options=options, **kwargs)

        if not self._zfs:
            self._zfs = self._peek_path()
            if not self._zfs:
                self.log.critical("zfs not found!")
                exit(6)

        if not self._threshold_warn:
            self._threshold_warn = parse_size("20g", binary=True)
        if not self._threshold_err:
            self._threshold_err = parse_size("10g", binary=True)

        if not self._color:
            self._color = {
                "ok": "#ffffff",
                "warn": "#ffff00",
                "err": "#ff0000",
            }

    def _peek_path(self) -> str:
        for p in self.PATHS:
            path = os.path.join(p, "zfs")
            if not os.path.exists(path):
                continue
            _check_path(path, self.log)
            return path
        return None

    def _get_available(self) -> int:
        p = Popen([self._zfs,
                   "list", "-H", "-p", "-o", "avail",
                   self._dataset],
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        if p.returncode != 0:
            self.log.error("Failed to get available size in dataset %s",
                           self._dataset)
            return 0
        return int(stdout)

    def _get_color(self, size: int) -> str:
        if size <= self._threshold_err:
            return self._color["err"]
        if size <= self._threshold_warn:
            return self._color["warn"]
        return self._color["ok"]

    def update(self):
        avail = self._get_available()
        text = self._text.format(format_size(avail, binary=True))
        with self.block:
            self.block.full_text = self.block.short_text = text
            self.block.color = self._get_color(avail)
