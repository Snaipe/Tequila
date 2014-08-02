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
from distutils.dir_util import copy_tree, remove_tree
from string import Template
from subprocess import call
from time import sleep

from tequila.config import Config, config_node
from tequila.exception import TequilaException
from tequila.maven import ArtifactResolver, Artifact, Repository
from tequila.wrapper import Wrapper


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
        self.wrapper = Wrapper.get_wrapper(self.config.get_wrapper_type())(self)

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

    def create(self, force=False, merge=False):
        from tequila import Tequila

        if self.exists and not force and not merge:
            raise ServerAlreadyExistsException(self)

        if merge:
            if self.exists:
                self.config.load()
                self.config.save()
                self.logger.info('Merged configuration of server %s with the current version of Tequila.', self.name)
                return
            else:
                raise ServerDoesNotExistException(self)

        copy_tree(join(Tequila.instance().get_resource_dir(), 'server_base'), self.home)
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
            remove_tree(join(plugin_dir, name), verbose=False)

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
        if self.wrapper.exists:
            raise ServerAlreadyRunningException(self.name)

        self.wrapper.start()
        self.logger.info('Server %s started', self.name)

    def stop(self, force=False, harder=False):
        self.wrapper.stop(force, harder)
        self.logger.info('Server %s stopped', self.name)

    def restart(self, force=False, harder=False):
        self.wrapper.restart(force, harder)
        self.logger.info('Server %s restarted', self.name)

    def send(self, mc_cmd):
        if not self.exists:
            raise ServerDoesNotExistException(self)

        if not self.wrapper.exists:
            raise ServerNotRunningException(self)

        self.wrapper.send(mc_cmd)
        self.logger.info('Command sent to server %s', self.name)

    def status(self):
        self.logger.info('Status of server %s : %s', self.name,
                         'Running' if self.wrapper.status != 'Dead' else 'Stopped')

    def delete(self):
        if self.wrapper.exists:
            raise ServerException('Server $name is running and cannot be deleted', self)

        if not self.exists:
            raise ServerDoesNotExistException(self)

        remove_tree(self.home, verbose=False)
        self.logger.info('Deleted server %s', self.name)


class ServerConfig(Config):

    @config_node('server')
    def get_server_bin(self):
        return 'org.bukkit:craftbukkit:1.7.9-R0.3'

    @config_node('stop-command')
    def get_stop_command(self):
        return 'stop'

    @config_node('wrapper-type')
    def get_wrapper_type(self):
        return 'screen'

    @config_node('plugins', section='directories')
    def get_plugins_dir(self):
        return 'plugins'

    @config_node('worlds', section='directories')
    def get_worlds_dir(self):
        return 'worlds'

    @config_node('jvm', section='options')
    def get_jvm_opt_file(self):
        return 'jvm.opts'

    @config_node('application', section='options')
    def get_app_opt_file(self):
        return 'application.opts'

    def get_repositories(self):
        return self.get_section('repositories')

    def get_plugins(self):
        return self.get_section('plugins')

