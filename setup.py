#!/usr/bin/env python
import codecs
import os
import re
from setuptools import setup, find_packages


def abspath(*args):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)


def get_contents(*args):
    with codecs.open(abspath(*args), "r", "utf-8") as handle:
        return handle.read()


def get_version(*args):
    contents = get_contents(*args)
    metadata = dict(re.findall(r'__([a-z]+)__\s+=\s+[\'"]([^\'"]+)', contents))
    return metadata["version"]


setup(
    name="pystatus",
    version=get_version("pystatus", "__init__.py"),
    description="i3bar compatible statusline generator",
    url="https://github.com/g0dsCookie/pystatus",
    author="g0dsCookie",
    author_email="g0dscookie@cookieprojects.de",
    license="MIT",
    packages=find_packages(),
    entry_points=dict(console_scripts=[
        "pystatus = pystatus.cli:main",
    ]),
    install_requires=["psutil", "humanfriendly"],
)
