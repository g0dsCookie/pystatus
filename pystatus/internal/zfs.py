import os
import logging
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
from .bases import StorAvailPlugin, StorAvailInstance


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
    PATHS = [
        "/sbin", "/usr/sbin", "/usr/local/sbin",
        "/bin", "/usr/bin", "/usr/local/bin",
    ]

    def __init__(self, *args, **kwargs):
        options = {
            "zfs": None,
            "dataset": None,
        }
        super().__init__(*args,
                         text="Z: {}",
                         threshold_warn="20g",
                         threshold_err="10g",
                         options=options,
                         **kwargs)

        if not self._zfs:
            self._zfs = self._peek_path()
            if not self._zfs:
                self.log.critical("zfs not found!")
                exit(6)

    def _peek_path(self) -> str:
        for p in self.PATHS:
            path = os.path.join(p, "zfs")
            if not os.path.exists(path):
                continue
            _check_path(path, self.log)
            return path
        return None

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
