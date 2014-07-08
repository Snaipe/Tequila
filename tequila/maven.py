import hashlib
from string import Template
from urllib.request import FancyURLopener
import sys
import math


class ChecksumNotMatchingError(Exception):
    pass


class Artifact(object):
    def __init__(self, groupid, artifactid, version,
                 template=Template('$groupid/$artifactid/$version/$artifactid-$version.$ext')):
        self.groupid = groupid
        self.artifactid = artifactid
        self.version = version

        self.jar = template.substitute(
            groupid=groupid.replace('.', '/'),
            artifactid=artifactid,
            version=version,
            ext='jar')

        self.pom = template.substitute(
            groupid=groupid.replace('.', '/'),
            artifactid=artifactid,
            version=version,
            ext='pom')


class ArtifactResolver(object):
    def __init__(self):
        self.artifacts = []

    def enqueue(self, artifact):
        self.artifacts += artifact

    def download_artifact(self, urlopener, artifact):
        pass

    def resolve(self):
        urlopener = FancyURLopener()
        try:
            for artifact in self.artifacts:
                self.download_artifact(urlopener, artifact)
        finally:
            urlopener.close()

    @staticmethod
    def checksum(file):
        sha1 = hashlib.sha1()
        with open(file, 'rb') as f, \
                open(file + '.sha1', 'r') as file_hash:

            sha1.update(f.read())
            return sha1.hexdigest() == file_hash.read()

    @staticmethod
    def download(urlopener, name, url, target, validate=True):
        bar_size = 30
        last = 0

        def reporthook(blocknum, blocksize, totalsize):
            nonlocal last
            percent = blocknum * blocksize * 1e2 / totalsize
            progress = math.floor(blocknum * blocksize * bar_size / totalsize)

            if blocknum == 0:
                sys.stdout.write('Downloading %s (%d Bytes): [%s]   0%%' % (name, totalsize, ' ' * bar_size))
                sys.stdout.write('\033[%dD' % (bar_size + 6))
            elif last < progress <= bar_size:
                sys.stdout.write('#')
                sys.stdout.write('\033[%dC%3d%%\033[%dD' % ((bar_size - progress + 2), percent, (bar_size - progress + 6)))

            if percent >= 1e2:
                sys.stdout.write('\033[%dC\n' % 6)

            sys.stdout.flush()
            last = progress

        try:
            sys.stdout.write('\x1B[?25l') # deactivate cursor
            urlopener.retrieve(url, target, reporthook)

            if validate:
                urlopener.retrieve(url + '.sha1', name + '.sha1')
                if not checksum(name):
                    raise ChecksumNotMatchingError()
        finally:
            sys.stdout.write('\x1B[?25h') # activate cursor
            sys.stdout.flush()








#urlopener = FancyURLopener()
#download(urlopener, 'worldedit.jar',
#         'http://maven.sk89q.com/repo/com/sk89q/worldedit/6.0.0-SNAPSHOT/worldedit-6.0.0-SNAPSHOT.jar')
#urlopener.close()


