"""
Tequila: a command-line Minecraft server manager written in python

Copyright (C) 2014 Snaipe

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="tequila",
    version="1.0.0",
    author="Snaipe",
    author_email="franklinmathieu@gmail.com",
    description="A minecraft server manager",
    license="GPLv3",
    keywords="minecraft server manager",
    url="http://github.com/Snaipe/tequila",
    packages=['tequila'],
    long_description=read('README'),
    scripts=['bin/tequila'],
    include_package_data=True,
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
)
