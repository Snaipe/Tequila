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
import signal
import re
from subprocess import call, getoutput


class Screen(object):

    def __init__(self, name):
        self.name = 'tequila_' + re.sub(r'[^a-zA-Z0-9\-_]', '', name)

    @property
    def exists(self):
        return self.pid != 0

    @property
    def status(self):
        Screen.wipe()
        lines = getoutput('screen -ls | grep -E "[0-9]+\.%s"' % self.name).splitlines(keepends=False)
        return lines[0].split('\t')[2].strip('()') if len(lines) > 0 else 'Dead'

    @property
    def pid(self):
        lines = getoutput('screen -ls | grep -E "[0-9]+\.%s"' % self.name).splitlines(keepends=False)
        return int(lines[0].split('\t')[1].split('.')[0]) if len(lines) > 0 else 0

    def start(self, command):
        call(['screen', '-q', '-dmS', self.name] + command.split())

    def kill(self, force=False):
        os.kill(self.pid, signal.SIGKILL if force else signal.SIGTERM)

    def send(self, command):
        call(['screen', '-q', '-S', self.name, '-p', '0', '-X', 'stuff', command + '\r'])

    @classmethod
    def wipe(cls):
        call(['screen', '-q', '-wipe'])