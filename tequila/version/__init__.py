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
from ..util import ask


class VersionControl(object):

    def is_init(self):
        return False

    def init(self):
        raise NotImplementedError()

    def commit(self, files, message, version=None):
        raise NotImplementedError()

    def get_changes(self):
        raise NotImplementedError()

    def push(self, remote, branch, force=False):
        raise NotImplementedError()

    def pull(self, remote, branch, rebase=True):
        raise NotImplementedError()

    def clone(self):
        raise NotImplementedError()

    def restore(self, version=None):
        raise NotImplementedError()

    def watch(self, version_changer):
        if not self.is_init():
            self.init()

        changes = self.get_changes()
        if len(changes) > 0:
            print('Some files have changed in the repository:')
            for file in changes:
                print('\t' + file)
            if ask('Would you like to commit those files ?'):
                print('Commiting the files. Please enter a message:')
                message = input()
                self.commit(changes, message, version_changer())
            else:
                print('Changes not commited.')


class NoVersionControl(VersionControl):

    def watch(self, version_changer):
        pass