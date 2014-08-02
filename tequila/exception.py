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


class TequilaException(Exception):
    def __init__(self, message='', **kwargs):
        from string import Template
        self.message = Template(message).substitute(**kwargs)


class UnhandledException(Exception):
    pass


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