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
from os.path import join, exists
from subprocess import Popen

from . import Wrapper, wrapper

from ..exception import ServerNotRunningException

from ...daemonize import fork_and_daemonize
from ...util import directory


@wrapper('daemon')
class Daemon(Wrapper):

    def __init__(self, server, id):
        super().__init__(server, 'tequila_' + re.sub(r'[^a-zA-Z0-9\-_]', '', id))

    def running(self):
        return exists(join(self.server.home, '.pid'))

    def status(self):
        return 'Alive' if self.running() else 'Dead'

    def pid(self):
        try:
            with open(join(self.server.home, '.pid'), 'r') as f:
                return int(f.read())
        except IOError:
            return 0

    def start(self):
        env = os.environ.copy()
        env['TEQUILA'] = 'true'
        env['JAVA_OPTS'] = self.get_jvm_opts()
        env['APP_OPTS'] = self.get_server_opts()

        if fork_and_daemonize():

            with directory(self.server.home):
                proc = Popen(['./start'], env=env)
                with open(join(self.server.home, '.pid'), 'w') as f:
                    f.write(ascii(proc.pid))

                proc.wait()

    def send(self, command):
        pid = self.pid()

        if pid == 0:
            raise ServerNotRunningException(self.server)

        with open('/proc/' + pid + '/fd/0', 'a') as stdin:
            stdin.write(command + '\r')