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

from configparser import ConfigParser
from functools import wraps


def config_node(section, node):
    def decorator(fun):
        @wraps(fun)
        def wrapper(self, *args, **kargs):
            return self.get(section, node, fun(self, *args, **kargs))
        return wrapper
    return decorator


class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = ConfigParser()

        # case-sensitive keys
        self.config.optionxform = str

    def load(self):
        self.config.read(self.config_file)

    def save(self):
        self.config.write(self.config_file)

    def __getitem__(self, section):
        self.get_section(section)

    def get_section(self, section):
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
            except:
                print("Could not get %s option." % option)
                dict1[option] = None
        return dict1

    def get(self, section, entry, default=None):
        try:
            return self.config.get(section, entry)
        except:
            return default

    def sections(self):
        return self.config.sections()


class ServerConfig(Config):

    @config_node('general', 'server')
    def get_server_bin(self):
        return 'org.bukkit:craftbukkit:1.7.9-R0.3'

    @config_node('general', 'stop-command')
    def get_stop_command(self):
        return 'stop'

    @config_node('directories', 'plugins')
    def get_plugins_dir(self):
        return 'plugins'

    @config_node('directories', 'worlds')
    def get_worlds_dir(self):
        return 'worlds'

    @config_node('options', 'jvm')
    def get_jvm_opt_file(self):
        return 'jvm.opts'

    @config_node('directories', 'application')
    def get_app_opt_file(self):
        return 'application.opts'

    def get_repositories(self):
        return self.get_section('repositories')

    def get_plugins(self):
        return self.get_section('plugins')
