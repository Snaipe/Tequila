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

import hashlib
import math
import sys

from ..exception import TequilaException


class ChecksumNotMatchingError(TequilaException):
    def __init__(self, actual, expected):
        super().__init__("File hashes not matching, got \"%s\" where expecting \"%s\"" % (actual, expected))


def checksum(file):
    sha1 = hashlib.sha1()
    with open(file, 'rb') as f, \
            open(file + '.sha1', 'r') as file_hash:
        sha1.update(f.read())
        sum1 = sha1.hexdigest()
        sum2 = file_hash.read().strip()
        if sum1 != sum2:
            raise ChecksumNotMatchingError(sum1, sum2)


def bytes_to_human(bytes):
    suffixes = ['k', 'M', 'G', 'T', 'P']
    n, s = bytes, ''
    for suffix in suffixes:
        bytes /= 1024.0
        if bytes < 1:
            break
        n, s = bytes, suffix
    return ('%.2f' % n)[:4].strip('0.') + ' %sB' % s


def download(urlopener, name, url, target, validate=False):
    max_name_size = 26
    bar_size = 15
    last = 0

    def reporthook(blocknum, blocksize, totalsize):
        nonlocal last
        nonlocal name

        # skip first handling to let propagate any error
        if blocknum == 0:
            return

        if len(name) > max_name_size:
            half = math.floor(max_name_size / 2)
            name = '...'.join([name[:half], name[-half:]])

        percent = min(1e2, blocknum * blocksize * 1e2 / totalsize)
        progress = min(bar_size, math.floor(blocknum * blocksize * bar_size / totalsize))

        if blocknum == 1:
            # dirty hack until I find the time to make this better
            sys.stdout.write('Downloading %s (%s): [%s]   0%%' % (name, bytes_to_human(totalsize), ' ' * bar_size))
            sys.stdout.write('\033[%dD' % (bar_size + 6))

        if last < progress:
            sys.stdout.write('#' * (progress - last))
            sys.stdout.write(
                '\033[%dC%3d%%\033[%dD' % ((bar_size - progress + 2), percent, (bar_size - progress + 6)))

        if percent >= 1e2:
            sys.stdout.write('\033[%dC\n' % 6)

        sys.stdout.flush()
        last = progress

    try:
        sys.stdout.write('\x1B[?25l')  # deactivate cursor
        urlopener.retrieve(url, target, reporthook)

        if validate:
            urlopener.retrieve(url + '.sha1', target + '.sha1')
            checksum(target)
    finally:
        sys.stdout.write('\x1B[?25h')  # activate cursor
        sys.stdout.flush()