import os
from os.path import dirname, realpath, normpath
import shutil

TEQUILA_HOME = os.environ.get('TEQUILA_HOME')


def get_home():
    return TEQUILA_HOME if TEQUILA_HOME is not None else '/home/minecraft'


def expand(path):
    return normpath(path.replace('${tequila_home}', get_home()).replace('${bin_dir}', dirname(realpath(__file__))))


def copy(src, dest):
    os.makedirs(dirname(dest), 0o755, exist_ok=True)
    shutil.copy(src, dest)