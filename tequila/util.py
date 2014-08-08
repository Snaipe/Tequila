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
from contextlib import contextmanager
from fnmatch import fnmatch

import os
from pwd import getpwnam
import shutil
import sys


def copy(src, dst):
    from os.path import dirname
    os.makedirs(dirname(dst), 0o755, exist_ok=True)
    shutil.copy(src, dst)


@contextmanager
def directory(dirname):
    old = os.getcwd()
    try:
        os.chdir(dirname)
        yield
    finally:
        os.chdir(old)


@contextmanager
def umask(mask):
    old = os.umask(mask)
    try:
        yield
    finally:
        os.umask(old)


class FileMatcher(object):

    def __init__(self, patterns):
        self.patterns = patterns

    def __call__(self, file):
        for pattern in self.patterns:
            if fnmatch(file, pattern):
                return True
        return False


def ask(message, default=False):
    if default:
        return input(message + " [Y/n]:").lower().strip() == "n"
    else:
        return input(message + " [y/N]:").lower().strip() == "y"


def get_uid(username):
    return getpwnam(username).pw_uid


def do_as_user(username, func, *args, **kwargs):
    _, _, uid, gid, _, _, _ = getpwnam(username)

    pid = os.fork()
    if pid == 0:
        if os.getgid() != gid:
            os.setregid(gid, gid)
        if os.getuid() != uid:
            os.setreuid(uid, uid)
        func(*args, **kwargs)
        os._exit(0)
    else:
        os.waitpid(pid, 0)


def delegate(obj, delegate):
    public_attributes = [(a, getattr(delegate, a)) for a in dir(delegate) if not a.startswith('_')]
    methods = [(n, m) for (n, m) in public_attributes if callable(m)]

    for (n, m) in methods:
        setattr(obj, n, m)