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
import baker

# register all commands
from .command import *

from .config import Config, config_node
from .exception import TequilaException
from .server import Server


class Tequila(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Tequila, cls).__new__(cls, *args, **kwargs)
            cls._instance.init()

        return cls._instance

    def init(self):
        logging.basicConfig(level='INFO', format="[%(name)s] %(message)s")

        self.logger = logging.getLogger('Tequila')
        self.config = TequilaConfig('/etc/tequila/tequila.conf')

        try:
            self.config.load()
        except:
            pass

    def main(self):
        try:
            baker.run()
        except TequilaException as e:
            self.logger.error(e.message)

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

    def get_groups_dir(self):
        from os.path import join
        return join(self.get_home(), 'groups')

    def get_servers(self):
        return os.listdir(self.get_servers_dir())

    def get_groups(self):
        return [f[:-6] for f in os.listdir(self.get_groups_dir())]


class TequilaConfig(Config):

    @config_node('default_home')
    def get_default_home(self):
        return '/home/minecraft'

    @config_node('general', 'use-git')
    def uses_git(self):
        return True
