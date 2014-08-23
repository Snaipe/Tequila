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
from os.path import join
from subprocess import call, check_output, STDOUT, CalledProcessError

from . import VersionControl

from ..util import directory


def _getoutput(cmd, **kwargs):
    kwargs.pop('stderr', None)
    kwargs.pop('universal_newlines', None)
    try:
        data = check_output(cmd, universal_newlines=True, stderr=STDOUT)
    except CalledProcessError as ex:
        data = ex.output
    if data[-1:] == '\n':
        data = data[:-1]
    return data


class Git(VersionControl):

    def __init__(self, repository, dir='.git', filter=lambda path: True):
        self.repository = repository
        self.dir = join(self.repository, dir)
        self.filter = filter

    def __call_git(self, *args, fun=call, **kwargs):
        return fun(['git', '--git-dir=%s' % self.dir, '--work-tree=%s' % self.repository] + list(args), **kwargs)

    def is_init(self):
        from os.path import join, isdir
        return isdir(join(self.repository, self.dir))

    def restore(self, version=None):
        self.__call_git('reset', '--hard', version if version else 'HEAD')

    def init(self):
        self.__call_git('init')

    def commit(self, files, message, version=None):
        if len(files) == 0:
            return

        self.add(files)

        self.__call_git('commit', '-m', message)

        if version:
            self.retag(version)

    def push(self, remote, branch, force=False):
        self.__call_git('push', remote, branch, *(['--force'] if force else []))

    def add(self, files):
        self.__call_git('add', '-A', *files)

    def get_changes(self, dir=''):
        args = ['status', '--porcelain', '-uall'] + ([dir] if len(dir) > 0 else [])

        return [line[3:] for line in self.__call_git(*args, fun=_getoutput).split('\n')
                if (line[1] == 'M' or line[1] == '?') and self.filter(line[3:])]

    def retag(self, version):
        self.__call_git('tag', '-f', version)

    def get_commit_count(self):
        return int(self.__call_git('rev-list', 'HEAD', '--count', fun=_getoutput).strip())

    def filter_tags(self, predicate):
        for tag in self.__call_git('tag', '-l', fun=_getoutput):
            if not predicate(tag):
                self.__call_git('tag', '-d', tag)

    def trim(self, length=15):
        diff = self.get_commit_count() - length
        if diff <= 0:
            return

        env = os.environ.copy()
        env['EDITOR'] = "sed -E '/^(#.*)?$/d; 2,%d s/pick/fixup/g'" % diff + 1
        self.__call_git('rebase', '-i', '--root', env=env)
        self.__call_git('prune')
        self.__call_git('gc')