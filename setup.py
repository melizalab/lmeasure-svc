#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- mode: python -*-
import sys
from setuptools import setup, find_packages

if sys.hexversion < 0x02070000:
    raise RuntimeError("Python 2.7 or higher required")

VERSION = '0.1.0'

cls_txt = """
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: Scientific/Engineering
Operating System :: Unix
Operating System :: POSIX :: Linux
Operating System :: MacOS :: MacOS X
Natural Language :: English
"""

short_desc = "Microservice for L-Measure"

long_desc = """ Run L-Measure as a friendly JSON-based web app!

"""


setup(
    name='lmeasure-svc',
    version=VERSION,
    description=short_desc,
    long_description=long_desc,
    classifiers=[x for x in cls_txt.split("\n") if x],
    author='Dan Meliza',
    maintainer='Dan Meliza',
    url="https://github.com/melizalab/lmeasure-svc",

    packages=find_packages(exclude=["*test*"]),

    install_requires=[],
    tests_require=["nose"],
    test_suite='nose.collector'
)

# Variables:
# End:
