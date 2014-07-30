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
import sys

if sys.version_info < (3, 0, 0):
    print('Tequila is not supported on versions lower than 3.x, sorry !')
    print('Your version of python is %s, try installing it with a more recent version.'
          % '.'.join(map(str, sys.version_info[:3])))
    sys.exit(1)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="tequila",
    version="1.0.4",
    author="Snaipe",
    author_email="franklinmathieu@gmail.com",
    description="A minecraft server manager",
    license="GPLv3",
    keywords="minecraft server manager",
    url="http://github.com/Snaipe/tequila",
    packages=['tequila'],
    long_description=read('README.md'),
    scripts=['bin/tequila'],
    data_files=[('/etc/tequila/', ['config/tequila.conf'])],
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
)
