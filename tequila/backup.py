from contextlib import contextmanager
import os
import tarfile


@contextmanager
def cwd(folder):
    old = os.getcwd()
    try:
        if folder:
            os.chdir(folder)
        yield
    finally:
        os.chdir(old)


def tar(archive, folder=None, *files):
        with cwd(folder):
            with tarfile.open('archive', 'w:bz2') as t:
                for file in files:
                    t.add(file)


def untar(archive, folder=None):
    with cwd(folder):
        with tarfile.open('archive', 'r:bz2') as t:
            t.extractall()