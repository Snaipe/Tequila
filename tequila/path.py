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
import shutil
from os.path import dirname, realpath, normpath

TEQUILA_HOME = os.environ.get('TEQUILA_HOME')


def get_home():
    return TEQUILA_HOME or '/home/minecraft'


def expand(path):
    return normpath(path.replace('${tequila_home}', get_home()).replace('${bin_dir}', dirname(realpath(__file__))))


def copy(src, dest):
    os.makedirs(dirname(dest), 0o755, exist_ok=True)
    shutil.copy(src, dest)