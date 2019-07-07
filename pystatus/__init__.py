from pathlib import Path


__version__ = "1.0.0"


def config_path(file):
    return Path.joinpath(Path.home(), ".config", "pystatus", file)


def lib_path(directory):
    return Path.joinpath(Path.home(), ".local", "lib", directory)
