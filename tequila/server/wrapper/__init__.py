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

from enum import Enum
import os
import errno
from time import sleep
import signal


class Status(Enum):
    alive = 0
    dead = 1


def is_running(pid):
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
    return True


def waitpid(pid, dt=0.2):
    while is_running(pid):
        sleep(dt)


class Wrapper(object):

    __wrappers = {}

    @classmethod
    def register(cls, name, wrapper):
        cls.__wrappers[name] = wrapper

    @classmethod
    def get_wrapper(cls, name):
        return cls.__wrappers[name]

    def __init__(self, server, id):
        self.server = server
        self.wrapper_id = id

    def get_jvm_opts(self, **kwargs):
        return self.server.get_jvm_opts(**kwargs)

    def get_server_opts(self, **kwargs):
        return self.server.get_server_opts(**kwargs)

    def running(self):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError

    def pid(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def send(self, command):
        raise NotImplementedError

    def kill(self, force=False):
        os.kill(self.pid(), signal.SIGKILL if force else signal.SIGTERM)

    def wait(self, dt=0.2):
        while is_running(self.pid()):
            sleep(dt)

    def stop(self, force=False, harder=False, ignore_stopped=True):
        if not self.running():
            if ignore_stopped:
                return
            from ..exception import ServerNotRunningException
            raise ServerNotRunningException(self.server)

        if force or harder:
            self.kill(harder)
        else:
            self.send(self.server.config.get_stop_command())
            waitpid(self.pid())

    def restart(self, force=False, harder=False):
        self.stop(force, harder, ignore_stopped=True)
        self.start()


def wrapper(name):
    def decorator(cls):
        Wrapper.register(name, cls)
        return cls
    return decorator


from .screen import Screen
from .daemon import Daemon

