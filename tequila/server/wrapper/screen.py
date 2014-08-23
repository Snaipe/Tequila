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
import re
from subprocess import call, getoutput

from ...util import directory
from . import Wrapper, wrapper


@wrapper('screen')
class Screen(Wrapper):

    def __init__(self, server, id):
        super().__init__(server, 'tequila_' + re.sub(r'[^a-zA-Z0-9\-_]', '', id))

    def running(self):
        return self.pid() != 0

    def status(self):
        Screen.wipe()
        lines = getoutput('screen -ls | grep -E "[0-9]+\.%s"' % self.wrapper_id).splitlines(keepends=False)
        return lines[0].split('\t')[2].strip('()') if len(lines) > 0 else 'Dead'

    def pid(self):
        Screen.wipe()
        lines = getoutput('screen -ls | grep -E "[0-9]+\\.%s"' % self.wrapper_id).splitlines(keepends=False)
        return int(lines[0].split('\t')[1].split('.')[0]) if len(lines) > 0 else 0

    def start(self):
        env = os.environ.copy()
        env['TEQUILA'] = 'true'
        env['JAVA_OPTS'] = self.get_jvm_opts()
        env['APP_OPTS'] = self.get_server_opts()

        with directory(self.server.home):
            call(['screen', '-q', '-dmS', self.wrapper_id, './start'], env=env)

    def send(self, command):
        call(['screen', '-q', '-S', self.wrapper_id, '-p', '0', '-X', 'stuff', command + '\r'])

    @classmethod
    def wipe(cls):
        call(['screen', '-q', '-wipe'])