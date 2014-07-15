from functools import wraps
from os import getcwd, chdir
from subprocess import call, getoutput


def cwd(fun):
    @wraps(fun)
    def wrapper(self, *args, **kwargs):
        old = getcwd()
        try:
            chdir(self.repository)
            return fun(self, *args, **kwargs)
        finally:
            chdir(old)
    return wrapper


class Git(object):

    def __init__(self, repository):
        self.repository = repository

    @cwd
    def init(self):
        call(['git', 'init'])

    @cwd
    def commit(self, message):
        call(['git', 'commit', '-m', message])

    @cwd
    def push(self, remote, branch):
        call(['git', 'push', remote, branch])