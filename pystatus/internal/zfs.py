import os
import logging
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
from .bases import StorAvailPlugin, StorAvailInstance
from pystatus.helpers import peek_binary


def _check_path(path: str, log: logging.Logger):
    p = Popen([path, "version"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = p.communicate()
    if p.returncode != 0:
        log.critical("'%s version' returned non-zero exit code %d",
                     path, p.returncode)
        exit(p.returncode)


class ZFS(StorAvailPlugin):
    def __init__(self):
        super().__init__("zfs", "0.1", "g0dscookie", ZFSInstance)
        self.register_option("zfs", self._check_path)
        self.register_option("dataset", str, required=True)

    def _check_path(self, xml: ET.Element) -> str:
        path = xml.text
        _check_path(path, self.log)
        return path


class ZFSInstance(StorAvailInstance):
    def __init__(self, *args, **kwargs):
        options = {
            "text": None,
            "threshold_warn": "20g",
            "threshold_err": "10g",
            "zfs": None,
            "dataset": None,
        }
        super().__init__(*args, options=options, **kwargs)

        if not self._text:
            self._text = self._dataset + ": {}"
        if not self._zfs:
            self._zfs = self._peek_path()
            if not self._zfs:
                self.log.critical("zfs not found!")
                exit(6)

    def _peek_path(self) -> str:
        p = peek_binary("zfs")
        if not p:
            self.log.critical("Could not find 'zfs' in PATH")
            exit(2)
        _check_path(p, self.log)
        return p

    def get_available(self):
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
