import hashlib
import math
import sys


class ChecksumNotMatchingError(Exception):
    pass


def checksum(file):
    sha1 = hashlib.sha1()
    with open(file, 'rb') as f, \
            open(file + '.sha1', 'r') as file_hash:
        sha1.update(f.read())
        sum1 = sha1.hexdigest()
        sum2 = file_hash.read()
        return sum1 == sum2


def download(urlopener, name, url, target, validate=False):
    bar_size = 20
    last = 0

    def reporthook(blocknum, blocksize, totalsize):
        nonlocal last

        # skip first handling to let propagate any error
        if blocknum == 0:
            return

        percent = min(1e2, blocknum * blocksize * 1e2 / totalsize)
        progress = min(bar_size, math.floor(blocknum * blocksize * bar_size / totalsize))

        if blocknum == 1:
            # dirty hack until I find the time to make this better
            sys.stdout.write('Downloading %s (%d Bytes): [%s]   0%%' % (name, totalsize, ' ' * bar_size))
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
            if not checksum(target):
                raise ChecksumNotMatchingError()
    finally:
        sys.stdout.write('\x1B[?25h')  # activate cursor
        sys.stdout.flush()