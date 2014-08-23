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
from distutils.dir_util import copy_tree, remove_tree
from os.path import join
from subprocess import call

from ..network import ArtifactResolver, Repository, Artifact
from .exception import ServerAlreadyExistsException, \
    ServerDoesNotExistException, \
    ServerRunningException


def copy_server_root(target):
    from tequila import Tequila
    copy_tree(join(Tequila().get_resource_dir(), 'server_base'), target)


class ServerFilesystem(object):

    def __init__(self, server):
        self.server = server
        self.config = server.config
        self.server_jar = join(server.home, 'server.jar')
        self.logger = server.logger

    def init(self, force=False, merge=False):
        if self.server.running() and not force and not merge:
            raise ServerAlreadyExistsException(self.server)

        if merge:
            if self.server.running():
                self.config.load()
                self.config.save()
                self.logger.info('Merged configuration with the current version of Tequila.')
                return
            else:
                raise ServerDoesNotExistException(self.server)

        if self.server.running():
            raise ServerRunningException(self.server)

        copy_server_root(self.server.home)
        call(['chmod', '-R', '755', self.server.home])
        self.logger.info('Created server at %s', self.server.home)

    @property
    def plugin_directory(self):
        return join(self.server.home, self.server.config.get_plugins_dir())

    def deploy(self):
        if self.server.running():
            raise ServerRunningException(self.server)

        resolver = ArtifactResolver()
        resolver.repositories = [Repository(name, repo) for (name, repo) in self.config.get_repositories().items()]

        server = Artifact.from_string(self.config.get_server_bin())
        resolver.enqueue(server)

        try:
            removed_plugins = set([f for f in os.listdir(self.plugin_directory) if f.endswith('.jar')])
        except FileNotFoundError:
            removed_plugins = set()

        for (plugin_name, plugin_url) in self.config.get_plugins().items():
            plugin = Artifact.from_string(plugin_url)
            plugin.filename = plugin_name + '.jar'
            resolver.enqueue(plugin)
            removed_plugins.discard(plugin.filename)
        resolver.resolve()

        resolver.artifacts.pop(0)
        resolver.deploy(self.plugin_directory)
        resolver.deploy_artifact(server, self.server_jar)

        for removed in removed_plugins:
            name = removed[:-4]
            self.logger.info('Removing plugin %s', name)
            os.remove(join(self.plugin_directory, removed))
            remove_tree(join(self.plugin_directory, name), verbose=False)

        self.logger.info('Successfully deployed server')

    def delete(self):
        if self.server.running():
            raise ServerRunningException(self.server)

        if not self.server.running():
            raise ServerDoesNotExistException(self.server)

        remove_tree(self.server.home, verbose=False)
        self.logger.info('Deleted server')