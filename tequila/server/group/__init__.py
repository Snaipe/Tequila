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
from os.path import join
from string import Template

from .config import ServerGroupConfig
from .exception import ServerGroupDoesNotExistException

from .. import Controlled, Server
from ...exception import TequilaException


class ServerGroup(Controlled):

    def __init__(self, name):
        from ... import Tequila

        super().__init__(name)
        self.logger = logging.getLogger('@' + name)

        self.tequila = Tequila()
        self.servers = {}
        self.file = join(self.tequila.get_groups_dir(), self.name + '.config')
        self.config = ServerGroupConfig(self)

    def exists(self):
        return os.path.exists(self.file)

    def load(self, load_servers=False, watch=True):
        if not self.exists():
            raise ServerGroupDoesNotExistException(self)

        self.config.load()
        for s in self.config.servers():
            try:
                server = Server(s)
                if load_servers:
                    server.load(watch)
                self.servers[server.name] = server
            except TequilaException as e:
                self.logger.info(e.message)
            except Exception as e:
                self.logger.exception(e)

        return self

    def save(self):
        self.config.servers([s.name for s in self.servers.values()])
        self.config.save()
        return self

    def add_server(self, server):
        self.servers[server.name] = server
        return self

    def remove_server(self, server):
        self.servers.pop(server.name)
        return self

    def status(self):
        return Template('$name: $servers').substitute(
            name=self.name,
            servers=str(list(self.servers.keys()))
        )

    def __getattr__(self, item):
        def call(*args, **kwargs):
            for server in self.servers.values():
                try:
                    getattr(server, item)(*args, **kwargs)
                except TequilaException as e:
                    self.logger.info(e.message)
                except Exception as e:
                    self.logger.exception(e)
        return call