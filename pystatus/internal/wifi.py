import re
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
from pystatus.plugin import IPlugin, IInstance
from pystatus.helpers import peek_binary


class WifiPlugin(IPlugin):
    def __init__(self):
        super().__init__("wifi", "0.1", "g0dscookie", WifiInstance)
        self.register_option("text", self._text)
        self.register_option("iface", str)
        self.register_option("wpa_cli", str)

    def _text(self, xml: ET.Element) -> dict:
        return dict({child.tag: child.text for child in xml})


class WifiInstance(IInstance):
    RE_STATUS = re.compile(r"^([^=]+)=(.*)$")

    def __init__(self, *args, **kwargs):
        options = {
            "text": None,
            "wpa_cli": None,
            "iface": None,
            "color": {
                "default": "#ffffff",
                "completed": "#00ff00",
                "scanning": "#ffff00",
                "disconnected": "#ff0000",
            },
        }
        super().__init__(*args, options=options, **kwargs)

        if not self._iface:
            self._iface = self.name if self.name != "wifi" else "wlan0"
        if not self._text:
            self._text = {
                "default": self._iface + ": {wpa_state}",
                "completed": self._iface + ": {ssid}",
            }
        if not self._wpa_cli:
            self._wpa_cli = peek_binary("wpa_cli")
            if not self._wpa_cli:
                self.log.critical("Could not find 'wpa_cli'")
                exit(2)

    def _wifi_status(self):
        p = Popen([self._wpa_cli, "-i", self._iface, "status"],
                  stdin=PIPE, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = p.communicate()
        if p.returncode != 0:
            self.log.critical("Got non-zero exit code from wpa_cli: %d",
                              p.returncode)
            exit(p.returncode)
        status = {}
        for line in stdout.decode("utf8").split("\n"):
            if not line:
                continue
            match = self.RE_STATUS.match(line)
            if not match:
                self.log.warn("Failed to match line '%s'", line)
                continue
            status[match.group(1)] = match.group(2)
        return status

    def update(self):
        status = self._wifi_status()
        wpa_state = status["wpa_state"].lower()
        text = (self._text[wpa_state] if wpa_state in self._text else
                self._text["default"]).format_map(status)
        color = (self._color[wpa_state] if wpa_state in self._color else
                 self._color["default"])

        with self.block:
            self.block.full_text = self.block.short_text = text
            self.block.color = color
