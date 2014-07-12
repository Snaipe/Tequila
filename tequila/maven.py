import logging
import subprocess
from string import Template
from urllib.request import FancyURLopener
from tequila.download import download
from tequila.exception import TequilaException
from tequila.path import copy
import xml.etree.cElementTree as ET


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

    def __init__(self, groupid, artifactid, version):
        self.groupid = groupid
        self.artifactid = artifactid
        self.version = version
        self.name = '%s:%s:%s' % (groupid, artifactid, version)
        self.filename = '%s-%s.jar' % (artifactid, version)

        self.template = Template('$groupid/$artifactid/$version1/$artifactid-$version2.$ext')

        self.jar = self.get_uri()
        self.pom = self.get_uri(packaging='pom')

    def get_uri(self, base='', packaging='jar', meta=None):
        version = self.version
        if meta is not None:
            version = version.replace('SNAPSHOT', '%s-%s' % (meta.get_snapshot_timestamp(), meta.get_snapshot_build_number()))
        return base + self.template.substitute(
            groupid=self.groupid.replace('.', '/'),
            artifactid=self.artifactid,
            version1=self.version,
            version2=version,
            ext=packaging)

    def is_snapshot(self):
        return self.version.endswith('SNAPSHOT')

    @classmethod
    def from_url(cls, url):
        """
        Constructs an artifact from a maven url (maven://groupid:artifactid:version)
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

    def install(self, directory):
        for artifact in self.artifacts:
            self.install_artifact(artifact, directory, True)

    @staticmethod
    def install_artifact(artifact, target, directory=False):
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