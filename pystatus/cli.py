from argparse import ArgumentParser
import logging
import logging.config
import os
import signal
import sys
import time
from pystatus import config_path
from pystatus.config import Config
from pystatus.i3bar import Statusline
from pystatus.plugin import PluginParent


class PystatusCli:
    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument("-d", "--debug",
                            action="store_true",
                            help="Enable debug output.")
        parser.add_argument("-c", "--config",
                            type=str,
                            default=config_path("pystatus.cfg"),
                            help="Path to configuration file.")
        parser.add_argument("--log-config",
                            type=str,
                            default=config_path("logging.cfg"),
                            help="Path to log configuration file.")
        self._args = parser.parse_args()

        if os.path.exists(self._args.log_config):
            logging.config.fileConfig(self._args.log_config)
        else:
            logfmt = "%(asctime)-15s %(name)s [%(levelname)s]: %(message)s"
            logging.basicConfig(level=logging.DEBUG
                                if self._args.debug else logging.INFO,
                                format=logfmt,
                                stream=sys.stderr)

        self._cfg = Config()
        self._parent = PluginParent()
        self._statusline = Statusline(sys.stdout,
                                      4 if self._args.debug else None)

        signal.signal(signal.SIGINT, self.sighandler)

    @property
    def cfg(self) -> Config:
        return self._cfg

    @property
    def parent(self) -> PluginParent:
        return self._parent

    @property
    def statusline(self) -> Statusline:
        return self._statusline

    @property
    def log(self) -> logging.Logger:
        return logging.getLogger("pystatus")

    def load(self):
        self.cfg.load(self._args.config)
        self.parent.load_plugins(self.cfg.plugindir)
        self.cfg.load_blocks()

    def setup(self):
        for block in self.cfg.blocks:
            self.parent.instance(block.plugin, block.name,
                                 self.statusline.new_block(block.plugin,
                                                           block.name),
                                 block.interval, block.options())
        self.statusline.start()

    def sighandler(self, signum, frame):
        if signum == signal.SIGINT:
            self.log.info("Received SIGINT")
            self.statusline.stop()
            self.parent.stop()

    def run(self):
        time.sleep(0.1)
        while self.statusline.is_open:
            self.statusline.sendline()
            time.sleep(self.cfg.interval)


def main():
    cli = PystatusCli()
    cli.load()
    cli.setup()
    cli.run()


if __name__ == "__main__":
    main()
