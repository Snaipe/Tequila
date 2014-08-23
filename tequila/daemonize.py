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

import sys
import os


def detach():
    os.chdir('/')
    os.setsid()
    os.umask(0)


def redirect_stdio():
    sys.stdout.flush()
    sys.stderr.flush()

    stdin = open(os.devnull, 'r')
    stdout = open(os.devnull, 'a+')
    stderr = open(os.devnull, 'a+')

    os.dup2(stdin.fileno(), sys.stdin.fileno())
    os.dup2(stdout.fileno(), sys.stdout.fileno())
    os.dup2(stderr.fileno(), sys.stderr.fileno())


def fork_and_daemonize():

    try:
        pid = os.fork()
        if pid > 0:
            return False
    except OSError:
        print('Error: Cannot daemonize process.')
        sys.exit(1)

    detach()

    try:
        pid = os.fork()
        if pid > 0:
            os._exit(0)
    except OSError:
        sys.exit(1)

    #redirect_stdio()
    return True