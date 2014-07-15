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
from tequila.config import Config, config_node
from tequila.exception import TequilaException
from tequila.server import Server
from tequila.command import Commands, command, arg


class Tequila(object):

    @classmethod
    def instance(cls):
        return cls._instance

    def __init__(self):
        self.__class__._instance = self

        logging.basicConfig(level='INFO', format="[%(name)s] %(message)s")

        self.logger = logging.getLogger('Tequila')
        self.commands = TequilaCommands(self)
        self.config = TequilaConfig('/etc/tequila/tequila.conf')

        try:
            self.config.load()
        except:
            pass

    def main(self):
        self.commands.handle()
        pass

    @staticmethod
    def get_dir():
        from os.path import dirname, realpath
        return dirname(realpath(__file__))

    def get_home(self):
        return os.environ.get('TEQUILA_HOME') or self.config.get_default_home()

    def get_resource_dir(self):
        from os.path import join
        return join(self.get_dir(), 'resources')

    def get_servers_dir(self):
        from os.path import join
        return join(self.get_home(), 'servers')

    def get_servers(self):
        return os.listdir(self.get_servers_dir())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# noinspection PyCallingNonCallable
class TequilaCommands(Commands):

    def __init__(self, tequila):
        super().__init__()
        self.tequila = tequila

    @command(name='start', arguments=[
        arg('servers', metavar='server', type=Server, nargs='+', help='The name of the server to start')
    ])
    @command(name='restart', arguments=[
        arg('-f', '--force', dest='force', action='store_true', help='Sends a SIGTERM to the specified servers'),
        arg('-F', '--Force', dest='harder', action='store_true', help='Sends a SIGKILL to the specified servers'),
        arg('servers', metavar='server', type=Server, nargs='+', help='The name of the server to restart')
    ])
    @command(name='deploy', arguments=[
        arg('servers', metavar='server', type=Server, nargs='+', help='The name of the server to deploy')
    ])
    def invoke_ctl(self, command, servers, **kwargs):
        for server in servers:
            try:
                server.load()
                getattr(server, command)(**kwargs)
            except TequilaException as e:
                self.tequila.logger.error(e.message)

    @command(name='create', arguments=[
        arg('servers', metavar='server', type=Server, nargs='+', help='The name of the server to create')
    ])
    @command(name='delete', arguments=[
        arg('servers', metavar='server', type=Server, nargs='+', help='The name of the server to delete')
    ])
    @command(name='status', arguments=[
        arg('servers', metavar='server', type=Server, nargs='+', help='The name of the server to get the status from')
    ])
    @command(name='send', arguments=[
        arg('mc_cmd', metavar='command', help='The command to send'),
        arg('servers', metavar='server', type=Server, nargs='+', help='The name of the server to send the command to')
    ])
    @command(name='stop', arguments=[
        arg('-f', '--force', dest='force', action='store_true', help='Sends a SIGTERM to the specified servers'),
        arg('-F', '--Force', dest='harder', action='store_true', help='Sends a SIGKILL to the specified servers'),
        arg('servers', metavar='server', type=Server, nargs='+', help='The name of the server to stop')
    ])
    def invoke_ctl_noload(self, command, servers, **kwargs):
        for server in servers:
            try:
                getattr(server, command)(**kwargs)
            except TequilaException as e:
                self.tequila.logger.error(e.message)

    @command(name='download', arguments=[
        arg('urls', metavar='URL', nargs='+', help='An URL to download the artifact from')
    ])
    def download(self, command, urls):
        from urllib.request import FancyURLopener
        from tequila.maven import ArtifactResolver

        maven_resolver = ArtifactResolver()
        for url in urls:
            maven_resolver.install_plugin_jar(FancyURLopener(), url)


class TequilaConfig(Config):

    @config_node('general', 'default_home')
    def get_default_home(self):
        return '/home/minecraft'