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

from functools import wraps
from os import getcwd, chdir
from subprocess import call, getoutput


def cwd(fun):
    @wraps(fun)
    def wrapper(self, *args, **kwargs):
        old = getcwd()
        try:
            chdir(self.repository)
            return fun(self, *args, **kwargs)
        finally:
            chdir(old)
    return wrapper


class Git(object):

    def __init__(self, repository):
        self.repository = repository

    @cwd
    def init(self):
        call(['git', 'init'])

    @cwd
    def commit(self, message):
        call(['git', 'commit', '-m', message])

    @cwd
    def push(self, remote, branch):
        call(['git', 'push', remote, branch])