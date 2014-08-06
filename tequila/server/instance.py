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
from copy import copy
from distutils.dir_util import copy_tree, remove_tree
from enum import Enum
from os import makedirs
import os
from os.path import join, exists
from shutil import chown
from subprocess import call
from tempfile import gettempdir

from .control import Controlled
from .exception import ServerRunningException, ServerException

from .wrapper import Wrapper

from .. import net
from ..daemonize import fork_and_daemonize
from ..exception import TequilaException
from ..util import delegate, do_as_user


def init_copy(instance):
    copy_tree(instance.server_home, instance.home)


def delete_copy(instance):
    remove_tree(instance.home)


def init_union(instance):
    makedirs(instance.home, mode=0o755, exist_ok=True)
    chown(instance.home, user=instance.server.config.get_user())
    call(['mount', '-t', 'aufs', '-o',
          'br=%s:%s' % (instance.home, instance.server_home),
          'none', instance.home])


def delete_union(instance):
    call(['umount', instance.home])
    remove_tree(instance.home)


class InstancePolicy(Enum):
    copy = (init_copy, delete_copy)
    union = (init_union, delete_union)

    @classmethod
    def from_string(cls, string):
        return getattr(cls, string.lower(), None) if string else None


class BindingPolicy(Enum):
    fixed = 0
    dynamic = 1

    @classmethod
    def from_string(cls, string):
        return getattr(cls, string.lower(), None) if string else None


class InstanceNotCleanException(ServerException):
    def __init__(self, instance):
        super().__init__('Instance #$id of server $name has not been cleaned up (did the watchdog crash?). '
                         'Please manually delete the directory $dir',
                         instance.server, id=instance.instance_id, dir=instance.home)


class ServerInstance(Controlled):

    def __init__(self, server, id):
        from . import ServerControl
        from copy import copy

        self.instance_directory = join(gettempdir(), 'tequila_instances', server.name)
        self.instance_id = self.get_id(id)

        self.server = copy(server)
        self.server_home = self.server.home
        self.server.home = self.home = join(self.instance_directory, str(self.instance_id))

        control = ServerControl(self.server)
        control.wrapper = InstanceWrapper(self, control.wrapper)

        super().__init__(self.server.name, control)

        start = self.start
        delegate(self, self.control_interface)
        self._start = self.start
        self.start = start

    def find_available_port(self, low, high):
        if os.name != 'posix':
            raise NotImplementedError('Scanning available ports is only available on *nix.')

        return net.get_open_ports(low, high)[0]

    def get_id(self, instance_id):
        if instance_id > 0:
            return instance_id

        i = 1
        root = self.instance_directory
        makedirs(root, exist_ok=True)

        directory = join(root, str(i))
        while exists(directory):
            i += 1
            directory = join(root, str(i))

        return i

    def start(self):
        if self.control_interface.wrapper.running():
            raise ServerRunningException(self.server)

        if exists(self.home):
            raise InstanceNotCleanException(self)

        self.server.logger.info('Starting instance #%d...', self.instance_id)

        if fork_and_daemonize():
            init, delete = self.server.config.get_instance_policy().value
            init(self)

            try:
                do_as_user(self.server.config.get_user(), self._start)

                self.control_interface.wrapper.wait(dt=5)
            except Exception as e:
                self.server.logger.exception(e)
            finally:
                delete(self)


class InstanceWrapper(Wrapper):

    def __init__(self, instance, wrapper):
        self.instance = instance
        self.wrapper = copy(wrapper)

        # hack in the new server and ID
        self.wrapper.server = instance.server
        self.wrapper.wrapper_id = wrapper.wrapper_id + '_' + str(instance.instance_id)

        super().__init__(instance.server, self.wrapper.wrapper_id)

        self.get_wrapper_jvm_opts = self.wrapper.get_jvm_opts
        self.get_wrapper_server_opts = self.wrapper.get_server_opts

        self.wrapper.get_jvm_opts = self.get_jvm_opts
        self.wrapper.get_server_opts = self.get_server_opts

    def port(self):
        port_range = self.server.config.get_instance_port_range()
        low = max(1 << 10, int(port_range[0]) if len(port_range) > 0 else 1 << 10)
        high = max(low, int(port_range[1]) if len(port_range) > 1 else (1 << 16) - 1)

        if self.server.config.get_instance_binding_policy() == BindingPolicy.dynamic:
            return self.instance.find_available_port(low, high)
        else:
            return min(high, low + self.instance.instance_id - 1)

    def get_jvm_opts(self, **kwargs):
        return self.get_wrapper_jvm_opts(**kwargs)

    def get_server_opts(self, **kwargs):
        kwargs['port'] = str(self.port())
        kwargs['instance_count'] = str(self.instance.instance_id)
        return self.get_wrapper_server_opts(**kwargs)

    def start(self):
        return self.wrapper.start()

    def pid(self):
        return self.wrapper.pid()

    def status(self):
        return self.wrapper.status()

    def running(self):
        return self.wrapper.running()

    def send(self, command):
        return self.wrapper.send(command)


class InstanceGroup(Controlled):

    def __init__(self, server, instances):
        super().__init__(server.name)
        self.server = server
        self.instances = instances

    def __getattr__(self, item):
        def call(*args, **kwargs):
            from .. import Tequila
            for i in self.instances:
                try:
                    getattr(i, item)(*args, **kwargs)
                except TequilaException as e:
                    Tequila().logger.info(e.message)
                except Exception as e:
                    Tequila().logger.exception(e)
        return call