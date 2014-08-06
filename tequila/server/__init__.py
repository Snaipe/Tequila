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
import logging
import os
from os.path import join, exists
from string import Template

from .control import Controlled, Control
from .filesystem import ServerFilesystem
from .config import ServerConfig
from .exception import \
    ServerDoesNotExistException, \
    ServerConfigurationNotFoundException, \
    ServerNotRunningException, \
    ServerRunningException
from .wrapper import Wrapper

from ..util import delegate


class Server(Controlled):

    def __init__(self, name):
        from tequila import Tequila

        super().__init__(name)
        self.tequila = Tequila()

        self.home = join(self.tequila.get_servers_dir(), self.name)
        self.configuration_directory = join(self.home, 'config')

        self.logger = logging.getLogger(name)
        self.config = ServerConfig(self)
        self.filesystem = ServerFilesystem(self)
        self.control_interface = ServerControl(self)

        delegate(self, self.filesystem)
        delegate(self, self.control_interface)

    def load(self):
        if not self.exists:
            raise ServerDoesNotExistException(self)

        try:
            self.config.load()
        except Exception as e:
            raise ServerConfigurationNotFoundException(self) from e
        return self

    @property
    def exists(self):
        return exists(self.home)

    @staticmethod
    def get_opts(directory, file, env):
        with open(os.path.join(directory, file), 'r') as f:
            return ((os.environ.get(env) or '') + f.read()).replace('\n', ' ').replace('\r', ' ')

    def get_jvm_opts(self, **kwargs):
        opts = self.get_opts(self.configuration_directory, self.config.get_jvm_opt_file(), 'JAVA_OPTS')
        return Template(opts).substitute(**kwargs)

    def get_server_opts(self, **kwargs):
        opts = self.get_opts(self.configuration_directory, self.config.get_app_opt_file(), 'SERVER_OPTS')

        kwargs.setdefault('plugins_dir', self.config.get_plugins_dir())
        kwargs.setdefault('worlds_dir', self.config.get_worlds_dir())

        return Template(opts).substitute(**kwargs)


class ServerControl(Control):

    def __init__(self, server: Server):
        self.server = server
        self.logger = server.logger
        self.wrapper = Wrapper.get_wrapper(self.server.config.get_wrapper_type())(self.server, self.server.name)

    def running(self):
        return self.wrapper.running()

    def start(self):
        if self.running():
            raise ServerRunningException(self.server)

        self.wrapper.start()
        self.logger.info('Server started')

    def stop(self, force=False, harder=False):
        self.wrapper.stop(force, harder)
        self.logger.info('Server stopped')

    def restart(self, force=False, harder=False):
        self.wrapper.restart(force, harder)
        self.logger.info('Server restarted')

    def send(self, mc_cmd):
        if not self.server.exists:
            raise ServerDoesNotExistException(self.server)

        if not self.running():
            raise ServerNotRunningException(self)

        self.wrapper.send(mc_cmd)
        self.logger.info('Sent command \'%s\'', mc_cmd)

    def status(self):
        self.logger.info('Status: %s', 'Running' if self.running() else 'Stopped')