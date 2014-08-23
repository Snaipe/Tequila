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

from contextlib import contextmanager
import os
import tarfile


@contextmanager
def cwd(folder):
    old = os.getcwd()
    try:
        if folder:
            os.chdir(folder)
        yield
    finally:
        os.chdir(old)


def tar(archive, folder=None, *files):
        with cwd(folder):
            with tarfile.open('archive', 'w:bz2') as t:
                for file in files:
                    t.add(file)


def untar(archive, folder=None):
    with cwd(folder):
        with tarfile.open('archive', 'r:bz2') as t:
            t.extractall()