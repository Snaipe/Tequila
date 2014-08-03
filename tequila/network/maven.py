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

import logging
import subprocess
import xml.etree.cElementTree as ET
from string import Template
from urllib.request import FancyURLopener

from ..exception import TequilaException, UnhandledException
from ..util import copy
from . import download


class MavenMetadata(object):

    def __init__(self, file):
        self.tree = ET.parse(file)

    def is_unique(self):
        return self.tree.find('./versioning/snapshotVersions') is None

    def get_snapshot_build_number(self):
        return self.tree.findtext('./versioning/snapshot/buildNumber')

    def get_snapshot_timestamp(self):
        return self.tree.findtext('./versioning/snapshot/timestamp')


class Artifact(object):

    def __init__(self, groupid, artifactid, version, filename=None):
        self.groupid = groupid
        self.artifactid = artifactid
        self.version = version
        self.name = '%s:%s:%s' % (groupid, artifactid, version)
        self.filename = filename or '%s-%s.jar' % (artifactid, version)

        self.template = Template('$groupid/$artifactid/$version1/$artifactid-$version2.$ext')

        self.jar = self.get_uri()
        self.pom = self.get_uri(packaging='pom')

    def get_uri(self, base='', packaging='jar', meta=None):
        version = self.version
        if meta is not None:
            version = version.replace('SNAPSHOT', '%s-%s' % (meta.get_snapshot_timestamp(),
                                                             meta.get_snapshot_build_number()))
        return base + self.template.substitute(
            groupid=self.groupid.replace('.', '/'),
            artifactid=self.artifactid,
            version1=self.version,
            version2=version,
            ext=packaging)

    def is_snapshot(self):
        return self.version.endswith('SNAPSHOT')

    @classmethod
    def from_string(cls, url):
        """
        Constructs an artifact from a maven syntax (groupid:artifactid:version)
        :type url: string
        """
        return cls(*url.split(':', 2))


class Repository(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url


class ArtifactUnresolvedException(TequilaException):
    def __init__(self, unresolved):
        super().__init__('Could not resolve the following artifacts: %s, '
                         'please check your configuration.'
                         % [artifact.name for artifact in unresolved])


class NotAPluginException(TequilaException):
    def __init__(self):
        super().__init__("The downloaded jar file is not a plugin and cannot be installed")


class InvalidPluginMetaException(TequilaException):
    def __init__(self):
        super().__init__("The downloaded plugin has an invalid plugin.yml")


class ArtifactResolver(object):
    def __init__(self):
        self.artifacts = []
        self.repositories = []
        self.logger = logging.getLogger("ArtifactResolver")

    def enqueue(self, artifact):
        self.logger.info('Added artifact %s', artifact.name)
        self.artifacts.append(artifact)

    def _try_download_artifact(self, urlopener, artifact, repository):
        from tempfile import mkdtemp
        from shutil import rmtree
        from os.path import join
        import posixpath

        tmp = mkdtemp("tequila")
        try:
            jar = join(tmp, artifact.filename)
            pom = join(tmp, artifact.filename + '.pom')

            jar_uri = artifact.get_uri(base=repository.url)
            pom_uri = artifact.get_uri(base=repository.url, packaging='pom')

            if artifact.is_snapshot():
                meta_uri = posixpath.join(posixpath.dirname(repository.url + artifact.jar), 'maven-metadata.xml')
                meta_file = join(tmp, 'maven-metadata.xml')

                download(urlopener, artifact.name + ':metadata', meta_uri, meta_file, validate=True)
                meta = MavenMetadata(meta_file)

                if not meta.is_unique():
                    jar_uri = artifact.get_uri(base=repository.url, meta=meta)
                    pom_uri = artifact.get_uri(base=repository.url, packaging='pom', meta=meta)

            download(urlopener, artifact.name + ':jar', jar_uri, jar, validate=True)

            try:
                download(urlopener, artifact.name + ':pom', pom_uri, pom, validate=True)
            except:
                self.install_with_meta(jar, artifact)
            else:
                self.install_with_pom(jar, pom)
        finally:
            rmtree(tmp)
            pass

    def _download_artifact(self, urlopener, artifact):
        from os.path import expanduser, exists
        if exists(expanduser('~/.m2/repository/') + artifact.jar):
            return True

        for repo in self.repositories:
            try:
                self._try_download_artifact(urlopener, artifact, repo)
                return True
            except (IOError, ValueError):
                continue
        return False

    def resolve(self):
        urlopener = FancyURLopener()
        try:
            unresolved = []
            for artifact in self.artifacts:
                if not self._download_artifact(urlopener, artifact):
                    unresolved.append(artifact)
                    self.logger.error("Could not resolve artifact %s." % artifact.name)

            if len(unresolved) > 0:
                raise ArtifactUnresolvedException(unresolved)
        except KeyboardInterrupt as e:
            raise TequilaException('Download interrupted by user.') from e
        finally:
            urlopener.close()

    def deploy(self, directory):
        for artifact in self.artifacts:
            self.deploy_artifact(artifact, directory, True)

    @staticmethod
    def deploy_artifact(artifact, target, directory=False):
        from os.path import join, expanduser
        copy(expanduser('~/.m2/repository/') + artifact.jar, join(target, artifact.filename) if directory else target)

    def install_external_jar(self, urlopener, artifact, url):
        from os.path import join
        from tempfile import mkdtemp
        from shutil import rmtree

        tmp = mkdtemp("tequila")
        try:
            jar = join(tmp, 'jar')

            download(urlopener, artifact.name + ':jar', url, jar, validate=False)
            self.install_with_meta(jar, artifact)
        finally:
            rmtree(tmp, ignore_errors=True)
            pass

    def install_plugin_jar(self, urlopener, url):
        from os.path import join
        from tempfile import mkdtemp
        from shutil import rmtree
        import zipfile
        import io

        tmp = mkdtemp("tequila")
        try:
            jar = join(tmp, 'jar')

            download(urlopener, url.split('/')[-1], url, jar, validate=False)

            with zipfile.ZipFile(jar, 'r') as jar_file:

                artifact_id = None
                version = None
                group_id = None
                try:
                    with jar_file.open('plugin.yml', 'rU') as plugin_meta:
                        wrapper = io.TextIOWrapper(plugin_meta)
                        for line in wrapper:
                            if line.startswith('name:') and artifact_id is None:
                                artifact_id = line.split(':', 1)[1].strip()
                            if line.startswith('version:') and version is None:
                                version = line.split(':', 1)[1].strip()
                            if line.startswith('main:') and group_id is None:
                                main = line.split(':', 1)[1].strip()
                                group_id = '.'.join(main.split('.', 2)[:2])
                            if artifact_id is not None and version is not None and group_id is not None:
                                break
                except Exception as e:
                    raise UnhandledException() from e
                    #raise NotAPluginException()

                if artifact_id is None and version is None and group_id is None:
                    raise InvalidPluginMetaException()

                self.install_with_meta(jar, Artifact(group_id, artifact_id, version))
        finally:
            rmtree(tmp, ignore_errors=True)
            pass

    def install_with_pom(self, file, pom):
        self.logger.info('Installing artifact...')
        subprocess.call(['mvn', '-q', 'install:install-file',
                         '-Dfile=%s' % file,
                         '-DpomFile=%s' % pom])

    def install_with_meta(self, file, artifact):
        self.logger.info('Installing artifact...')
        subprocess.call(['mvn', '-q', 'install:install-file',
                         '-Dfile=%s' % file,
                         '-Dpackaging=jar',
                         '-DgroupId=%s' % artifact.groupid,
                         '-DartifactId=%s' % artifact.artifactid,
                         '-Dversion=%s' % artifact.version])