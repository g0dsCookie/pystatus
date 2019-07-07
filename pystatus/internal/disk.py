import os
import xml.etree.ElementTree as ET
from .bases import StorAvailPlugin, StorAvailInstance


class Disk(StorAvailPlugin):
    def __init__(self):
        super().__init__("disk", "0.1", "g0dscookie", DiskInterface)
        self.register_option("dir", self._check_path)

    def _check_path(self, xml: ET.Element) -> str:
        path = xml.text
        if not os.path.isabs(path):
            self.log.warn("%s is not absolute, trying to resolve...", path)
            path = os.path.abspath(path)
            self.log.debug("Path resolved to %s", path)
        if not os.path.isdir(path):
            self.log.critical("%s does not exist or is not a directory", path)
            exit(2)
        return path


class DiskInterface(StorAvailInstance):
    def __init__(self, *args, **kwargs):
        options = {
            "text": None,
            "threshold_warn": "20g",
            "threshold_err": "10g",
            "dir": None
        }
        super().__init__(*args, options=options, **kwargs)
        if not self._dir:
            if not self.name.startswith("disk_/"):
                self.log.critical("No directory specified")
                exit(2)
            self._dir = self.name.split("_", 1)[1]
        if not self._text:
            self._text = self._dir + ": {}"

    def get_available(self):
        st = os.statvfs(self._dir)
        return st.f_bavail * st.f_frsize
