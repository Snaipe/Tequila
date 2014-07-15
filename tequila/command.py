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

import argparse
import sys


def command(name, arguments):
    def decorator(func):
        if not hasattr(func, 'commands'):
            func.commands = []
        func.commands.append((name, arguments))
        return func
    return decorator


def arg(*args, **kwargs):
    return args, kwargs


class Commands(object):

    def __init__(self):
        self._parser = argparse.ArgumentParser()
        subparsers = self._parser.add_subparsers(
            dest='command',
            title='commands',
            description='valid commands'
        )

        self._commands = {}
        for method in dir(self):
            attr = getattr(self, method)
            if callable(attr) and hasattr(attr, 'commands'):
                for name, args in attr.commands:
                    subparser = subparsers.add_parser(name)
                    for (fargs, kwargs) in args:
                        subparser.add_argument(*fargs, **kwargs)
                    self._commands[name] = attr

    def handle(self):
        if len(sys.argv) == 1:
            self.handle_no_arg()
            return
        namespace = self._parser.parse_args()
        self._commands[namespace.command](**vars(namespace))

    def handle_no_arg(self):
        self._parser.print_help()

    def get_commands(self):
        return self._commands