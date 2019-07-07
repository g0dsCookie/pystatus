from pathlib import Path
import os


def config_path(file):
    return Path.joinpath(Path.home(), ".config", "pystatus", file)


def lib_path(directory):
    return Path.joinpath(Path.home(), ".local", "lib", directory)


def peek_binary(binary, path=None):
    if not path:
        path = os.getenv("PATH", "/sbin:/bin:/usr/sbin:/usr/bin")
    for d in path.split(":"):
        p = os.path.join(d, binary)
        if os.path.exists(p):
            return p
    return None
