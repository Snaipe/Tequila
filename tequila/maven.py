import logging
import subprocess
from string import Template
from urllib.request import FancyURLopener
from tequila.download import download
from tequila.path import copy


class Artifact(object):

    def __init__(self, groupid, artifactid, version):
        self.groupid = groupid
        self.artifactid = artifactid
        self.version = version
        self.name = '%s:%s:%s' % (groupid, artifactid, version)
        self.filename = '%s-%s.jar' % (artifactid, version)

        template = Template('$groupid/$artifactid/$version/$artifactid-$version.$ext')

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

    @classmethod
    def from_url(cls, url):
        """
        Constructs an artifact from a maven url (maven://groupid:artifactid:version)
        :type url: string
        """
        return cls(*url[8:].split(':', 2))


class Repository(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url


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

        tmp = mkdtemp("tequila")
        try:
            jar = join(tmp, 'jar')
            pom = join(tmp, 'pom')

            download(urlopener, artifact.name + ':jar', repository.url + artifact.jar, jar, validate=True)

            try:
                download(urlopener, artifact.name + ':pom', repository.url + artifact.pom, pom, validate=True)
            except:
                self.install_with_meta(jar, artifact)
            else:
                self.install_with_pom(jar, pom)
        finally:
            rmtree(tmp, ignore_errors=True)
            pass

    def _download_artifact(self, urlopener, artifact):
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
            for artifact in self.artifacts:
                if not self._download_artifact(urlopener, artifact):
                    self.logger.error("Could not resolve artifact %s." % artifact.name)
                    self.artifacts.remove(artifact)
        except KeyboardInterrupt:
            self.logger.info('Download interrupted by user.')
            raise
        finally:
            urlopener.close()

    def install(self, directory):
        from os.path import join, expanduser
        for artifact in self.artifacts:
            copy(join(expanduser('~'), '.m2', 'repository', artifact.jar), join(directory, artifact.filename))

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



