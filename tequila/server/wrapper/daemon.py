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
import socket
from os.path import join, exists
from subprocess import Popen, PIPE

from . import Wrapper, wrapper
import select

from ..exception import ServerNotRunningException, ServerException, ServerCannotBeJoinedException

from ...daemonize import fork_and_daemonize
from ...net import socket_connection
from ...util import directory


@wrapper('daemon')
class Daemon(Wrapper):

    def __init__(self, server, id):
        super().__init__(server, 'tequila_' + re.sub(r'[^a-zA-Z0-9\-_]', '', id))

        self.socket = '.instance'

    def running(self):
        return exists(join(self.server.home, '.pid'))

    def status(self):
        return 'Alive' if self.running() else 'Dead'

    def pid(self):
        try:
            with open(join(self.server.home, '.pid'), 'r') as f:
                return int(f.read())
        except IOError as e:
            return 0

    def socket_dir(self):
        return self.server.home

    def socket_address(self):
        return join(self.socket_dir(), self.socket)

    def serve_commands(self, sock, proc):
        try:
            sock.listen(1)

            while proc.poll() is None:
                readable, _, errored = select.select([sock], [], [sock], 1)

                if sock in readable:
                    connection, client_address = sock.accept()
                    try:
                        if proc.poll() is not None:
                            return

                        while True:
                            data = connection.recv(512)
                            if not data:
                                break

                            proc.stdin.write(data)
                            proc.stdin.flush()
                    except Exception as e:
                        self.server.logger.exception(e)
                    finally:
                        connection.close()

                if sock in errored:
                    return
        finally:
            sock.close()

    def start(self):
        env = os.environ.copy()
        env['TEQUILA'] = 'true'
        env['JAVA_OPTS'] = self.get_jvm_opts()
        env['APP_OPTS'] = self.get_server_opts()

        os.makedirs(self.socket_dir(), exist_ok=True)

        if not exists(self.socket_dir()):
            raise ServerException('Could not create socket path for server $name', self.server)

        if fork_and_daemonize():

            try:
                with directory(self.server.home):
                    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    sock.setblocking(0)
                    sock.bind(self.socket_address())

                    proc = Popen(['./start'], env=env, stdin=PIPE)

                    with open(join(self.server.home, '.pid'), 'w') as f:
                        f.write(ascii(proc.pid))

                    self.serve_commands(sock, proc)
                    proc.wait()
            finally:
                os._exit(0)

    def send(self, command):
        pid = self.pid()

        if pid == 0:
            raise ServerNotRunningException(self.server)

        try:
            with socket_connection(self.socket_address()) as sock:
                sock.send((command + '\r').encode('utf-8'))
        except ConnectionRefusedError as e:
            raise ServerCannotBeJoinedException(self.server) from e