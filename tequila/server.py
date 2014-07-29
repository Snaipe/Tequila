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

import errno
import logging
import os
from os.path import join, exists
from shutil import copytree, rmtree
from string import Template
from subprocess import call
from time import sleep

from tequila.config import ServerConfig
from tequila.exception import TequilaException
from tequila.maven import ArtifactResolver, Artifact, Repository
from tequila.screen import Screen


class ServerException(TequilaException):
    def __init__(self, message, server):
        super().__init__(message, name=server.name, home=server.home)
        self.server = server


class ServerDoesNotExistException(ServerException):
    def __init__(self, server):
        super().__init__('Server $name does not exist', server)


class ServerAlreadyExistsException(ServerException):
    def __init__(self, server):
        super().__init__('Server $name already exists', server)


class ServerConfigurationNotFoundException(ServerException):
    def __init__(self, server):
        super().__init__('Could not load server $name : configuration not found', server)


class ServerAlreadyRunningException(ServerException):
    def __init__(self, server):
        super().__init__('Server $name is already running', server)


class ServerNotRunningException(ServerException):
    def __init__(self, server):
        super().__init__('Server $name is not running', server)


def is_running(pid):
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
    return True


def waitpid(pid):
    while is_running(pid):
        sleep(0.2)


class Server(object):

    def __init__(self, name):
        from tequila import Tequila
        self.logger = logging.getLogger('ServerManager')
        self.name = name
        self.home = join(Tequila.instance().get_servers_dir(), name)
        self.config_dir = join(self.home, 'config')
        self.config = ServerConfig(join(self.config_dir, 'tequila.config'))
        self.screen = Screen(name)

    @property
    def exists(self):
        return exists(self.home)

    def load(self):
        if not self.exists:
            raise ServerDoesNotExistException(self)

        try:
            self.config.load()
        except Exception as e:
            raise ServerConfigurationNotFoundException(self) from e
        return self

    def create(self):
        from tequila import Tequila

        if self.exists:
            raise ServerAlreadyExistsException(self)

        copytree(join(Tequila.instance().get_resource_dir(), 'server_base'), self.home)
        call(['chmod', '-R', '755', self.home])
        self.logger.info('Created server %s at %s', self.name, self.home)

    def deploy(self):
        maven_resolver = ArtifactResolver()
        maven_resolver.repositories = [Repository(name, repo)
                                       for (name, repo) in self.config.get_repositories().items()]

        plugin_dir = join(self.home, self.config.get_plugins_dir())

        server = Artifact.from_string(self.config.get_server_bin())
        maven_resolver.enqueue(server)

        try:
            removed_plugins = set([f for f in os.listdir(plugin_dir) if f.endswith('.jar')])
        except FileNotFoundError:
            removed_plugins = set()

        for (plugin_name, plugin_url) in self.config.get_plugins().items():
            plugin = Artifact.from_string(plugin_url)
            plugin.filename = plugin_name + '.jar'
            maven_resolver.enqueue(plugin)
            removed_plugins.discard(plugin.filename)
        maven_resolver.resolve()

        maven_resolver.artifacts.pop(0)
        maven_resolver.deploy(plugin_dir)
        maven_resolver.deploy_artifact(server, join(self.home, 'server.jar'))

        for removed in removed_plugins:
            name = removed[:-4]
            self.logger.info('Removing plugin %s', name)
            os.remove(join(plugin_dir, removed))
            rmtree(join(plugin_dir, name), ignore_errors=True)

        self.logger.info('Successfully deployed server %s', self.name)

    @staticmethod
    def get_opts(directory, file, env):
        with open(os.path.join(directory, file), 'r') as f:
            return ((os.environ.get(env) or '') + f.read()).replace('\n', ' ').replace('\r', ' ')

    def get_jvm_opts(self):
        return self.get_opts(self.config_dir, self.config.get_jvm_opt_file(), 'JAVA_OPTS')

    def get_server_opts(self):
        return Template(self.get_opts(self.config_dir, self.config.get_app_opt_file(), 'SERVER_OPTS')).substitute(
            plugins_dir=self.config.get_plugins_dir(),
            worlds_dir=self.config.get_worlds_dir()
        )

    def start(self):
        if self.screen.exists:
            raise ServerAlreadyRunningException(self.name)
        old = os.getcwd()
        try:
            os.chdir(self.home)
            self.screen.start('java %s -jar server.jar %s' % (self.get_jvm_opts(), self.get_server_opts()))
            self.logger.info('Server %s started', self.name)
        finally:
            os.chdir(old)

    def stop(self, force=False, harder=False):
        if not self.screen.exists:
            return

        if force or harder:
            self.screen.kill(harder)
        else:
            self.screen.send(self.config.get_stop_command())
            waitpid(self.screen.pid)
        self.logger.info('Server %s stopped', self.name)

    def restart(self, force=False, harder=False):
        self.stop(force, harder)
        self.start()

    def send(self, mc_cmd):
        if not self.exists:
            raise ServerDoesNotExistException(self)

        if not self.screen.exists:
            raise ServerNotRunningException(self)

        self.screen.send(mc_cmd)
        self.logger.info('Command sent to server %s', self.name)

    def status(self):
        self.logger.info('Status of server %s : %s', self.name,
                         'Running' if self.screen.status != 'Dead' else 'Stopped')

    def delete(self):
        if self.screen.exists:
            raise ServerException('Server $name is running and cannot be deleted', self)

        if not self.exists:
            raise ServerDoesNotExistException(self)

        rmtree(self.home, ignore_errors=True)
        self.logger.info('Deleted server %s', self.name)