import os
from os.path import dirname, realpath, normpath
import shutil


def expand(path):
    return normpath(path.replace('~tequila', dirname(dirname(realpath(__file__)))))


def copy(src, dest):
    os.makedirs(dirname(dest), 0o755, exist_ok=True)
    shutil.copy(src, dest)