from pathlib import Path


def config_path(file):
    return Path.joinpath(Path.home(), ".config", "pystatus", file)


def lib_path(directory):
    return Path.joinpath(Path.home(), ".local", "lib", directory)
