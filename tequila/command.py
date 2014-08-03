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
from baker import command

from .server import Server


@command(name='init')
def cmd_init(server, force=False, merge=False):
    """
    :param server: The server to initialize
    """
    Server(server).init(force, merge)


@command(name='delete')
def cmd_delete(server):
    """
    :param server: The server to delete
    """
    Server(server).load().delete()


@command(name='deploy')
def cmd_deploy(server):
    """
    :param server: The server to deploy
    """
    Server(server).load().deploy()


@command(name='status')
def cmd_status(server):
    """
    :param server: The server to deploy
    """
    Server(server).load().status()


@command(name='start')
def cmd_start(server):
    """
    :param server: The server to start
    """
    Server(server).load().start()


@command(name='stop', shortopts={'force': 'f', 'Force': 'F'})
def cmd_stop(server, force=False, Force=False):
    """
    :param server: The server to stop
    :param force: send a SIGTERM to the server
    :param Force: send a SIGKILL to the server
    """
    Server(server).load().stop(force, Force)


@command(name='restart', shortopts={'force': 'f', 'Force': 'F'})
def cmd_restart(server, force=False, Force=False):
    """
    :param server: The server to restart
    :param force: send a SIGTERM to the server
    :param Force: send a SIGKILL to the server
    """
    Server(server).load().restart(force, Force)


@command(name='send')
def cmd_send(server, *command):
    """
    :param server: The server to start
    :param command: the command to send
    """
    Server(server).load().send(' '.join(command))


@command(name='list')
def cmd_list():
    from . import Tequila
    tequila = Tequila()
    tequila.logger.info('Available servers: %s', ', '.join(tequila.get_servers()))


@command(name='download')
def cmd_download(*urls):
    """
    :param urls: the urls to download
    """
    from urllib.request import FancyURLopener
    from tequila.network.maven import ArtifactResolver

    maven_resolver = ArtifactResolver()
    for url in urls:
        maven_resolver.install_plugin_jar(FancyURLopener(), url)