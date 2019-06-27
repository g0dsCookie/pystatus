#!/usr/bin/env python3
import argparse
import time
import signal
import sys
import os
from pathlib import Path
import logging
import logging.config
import pystatus.config
import pystatus.i3bar
import pystatus.plugin


def sighandler(signum, frame):
    if signum == signal.SIGINT:
        log.info("Received SIGINT")
        statusline.stop()
        parent.stop()


def config_path(file):
    return Path.joinpath(Path.home(), ".config", "pystatus", file)


def setup_log(file, loglvl):
    logfile = file
    if os.path.exists(logfile):
        logging.config.fileConfig(logfile)
    else:
        logopts = {
            "level": loglvl,
            "format": "%(asctime)-15s %(name)s [%(levelname)s]: %(message)s",
            "stream": sys.stderr,
        }
        logging.basicConfig(**logopts)
    return logging.getLogger("pystatus")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Enable debug output.")
    parser.add_argument("-c", "--config",
                        type=str,
                        default=config_path("pystatus.cfg"),
                        help="Path to configuration file.")
    parser.add_argument("--log-config",
                        type=str,
                        default=config_path("logging.cfg"),
                        help="Path to log configuration file.")
    args = parser.parse_args()

    log = setup_log(args.log_config,
                    logging.DEBUG if args.debug else logging.INFO)
    signal.signal(signal.SIGINT, sighandler)

    parent = pystatus.plugin.PluginParent()
    parent.load_plugins(None)

    cfg = pystatus.config.Config()
    cfg.load(args.config)

    statusline = pystatus.i3bar.Statusline(sys.stdout,
                                           4 if args.debug else None)

    for block in cfg.blocks:
        b = statusline.new_block(block.plugin, block.name)
        parent.instance(block.plugin, block.name,
                        b, block.interval,
                        block.options())

    # TODO: Wait until every plugin has set atleast full_text set
    # Just a quick fix for full_text unset
    # on first line sent
    time.sleep(1)

    statusline.start()
    while statusline.is_open:
        statusline.sendline()
        time.sleep(1)
