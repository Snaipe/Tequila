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
from os.path import join

from .instance import InstancePolicy, BindingPolicy

from ..config import Config, config_node


class ServerConfig(Config):

    def __init__(self, server):
        super().__init__(join(server.configuration_directory, 'tequila.config'))

    @config_node('server')
    def get_server_bin(self):
        return 'org.bukkit:craftbukkit:1.7.9-R0.3'

    @config_node('stop-command')
    def get_stop_command(self):
        return 'stop'

    @config_node('wrapper-type')
    def get_wrapper_type(self):
        return 'screen'

    @config_node('user')
    def get_user(self):
        return 'minecraft'

    @config_node('enabled', section='version-control', type=bool)
    def is_version_control_enabled(self):
        return False

    @config_node('config-files', section='version-control', type=list)
    def get_version_control_config_files(self):
        return ['*.yml', '*.properties']

    @config_node('data-files', section='version-control', type=list)
    def get_version_control_data_files(self):
        return ['*.dat', '*.dat_old', '*.dat_mcr', '*.mca', '*.json']

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

    @config_node('enabled', section='multiple-instances')
    def are_instances_enabled(self):
        return False

    @config_node('startup-policy', section='multiple-instances', type=InstancePolicy)
    def get_instance_policy(self):
        return InstancePolicy.copy

    @config_node('binding-policy', section='multiple-instances', type=BindingPolicy)
    def get_instance_binding_policy(self):
        return BindingPolicy.fixed

    @config_node('port-range', section='multiple-instances', type=list)
    def get_instance_port_range(self):
        return [25565, 25665]

    def get_directories(self):
        return self.get_section('directories')

    def get_repositories(self):
        return self.get_section('repositories')

    def get_plugins(self):
        return self.get_section('plugins')