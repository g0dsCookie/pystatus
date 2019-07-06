#!/usr/bin/env python
from distutils.core import setup


setup(name="pystatus",
      version="1.0.0",
      description="i3bar compatible status line generator",
      author="g0dsCookie",
      author_email="g0dscookie@cookieprojects.de",
      url="https://github.com/g0dsCookie/pystatus",
      packages=["pystatus", "pystatus/internal"],
      scripts=["pystatus.py"])
