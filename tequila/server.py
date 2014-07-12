import logging
import os
from shutil import copytree
from subprocess import call, Popen

from tequila import Environment
from tequila.config import Config, ServerConfig
from tequila.decorators import ctl_commands, command_syntax, wrap_exception
from tequila.exception import TequilaException
from tequila.maven import ArtifactResolver, Artifact, Repository


class NoSuchServerException(TequilaException):
    def __init__(self, servername):
        self.message = 'Could not find server %s' % servername


@ctl_commands(['start', 'stop', 'restart', 'status', 'send'])
class Server(object):

    def __init__(self, name):
        from os.path import join
        self.name = name
        self.home = join(Environment['SERVER_HOME'], name)
        self.config_dir = join(self.home, 'config')
        self.config = ServerConfig(join(self.config_dir, 'tequila.config'))

    def load(self):
        self.config.load()
        return self

    def setup(self):
        from os.path import join
        copytree(join(Environment['RESOURCE_DIRECTORY'], 'server_base'), self.home)
        self.load()
        call(['chmod', '-R', '755', self.home])

    def install(self):
        from os.path import join

        maven_resolver = ArtifactResolver()
        maven_resolver.repositories = [Repository(name, repo) for (name, repo) in self.config.get_repositories().items()]

        server = Artifact.from_url(self.config.get_server_bin())

        maven_resolver.enqueue(server)
        for (plugin_name, plugin_url) in self.config.get_plugins().items():
            maven_resolver.enqueue(Artifact.from_url(plugin_url))
        maven_resolver.resolve()

        maven_resolver.artifacts.pop(0)
        maven_resolver.install(join(self.home, self.config.get_plugins_dir()))

        maven_resolver.install_artifact(server, join(self.home, 'server.jar'))

    def get_ctl_env(self):
        from os.path import join
        env = os.environ.copy()
        env['TEQUILA'] = "true"
        env['SERVER_NAME'] = self.name
        env['SERVER_HOME'] = self.home
        env['SERVER_USER'] = self.config.get_user()
        env['TEQUILA_JVM_OPTS'] = join(self.config_dir, self.config.get_jvm_opt_file())
        env['TEQUILA_APP_OPTS'] = join(self.config_dir, self.config.get_app_opt_file())
        env['SERVER_OPTS'] = '-W%s' % self.config.get_worlds_dir() \
                             + ' -P%s' % self.config.get_plugins_dir()
        return env

    def invokectl(self, cmd):
        from os.path import join
        call([join(self.home, 'serverctl'), cmd], env=self.get_ctl_env())

    def wipe(self):
        from shutil import rmtree
        rmtree(self.home, ignore_errors=True)


class ServerManager(object):
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.servers = {}
        for servername in os.listdir(Environment['SERVER_HOME']):
            self.servers[servername] = server = Server(servername)
            try:
                server.load()
            except:
                self.logger.error('Server %s has configuration errors', servername)

    @wrap_exception
    @command_syntax("new <server name>")
    def cmd_new(self, name):
        if name in self.servers:
            self.logger.error('Could not create server %s : server already exists.', name)
            return

        server = Server(name)
        server.setup()

        self.logger.info('Successfully created the new server at %s. ', server.home)
        self.logger.info('Take the time to configure it, then run the install command to set it up.')

    @wrap_exception
    @command_syntax("install <server name>")
    def cmd_install(self, name):
        if name not in self.servers:
            raise NoSuchServerException(name)

        self.servers[name].install()
        self.logger.info('Successfully installed all the artifacts')

    @wrap_exception
    def invoke(self, fun, servers, *args):
        if len(servers) == 0:
            server_list = self.servers.values()
        else:
            try:
                server_list = [self.servers[s] for s in servers]
            except KeyError as e:
                raise NoSuchServerException(e.args[0])

        for server in server_list:
            getattr(server, fun)(*args)

    @command_syntax("start [server1 server2 ...]")
    def cmd_start(self, *servers):
        self.invoke('start', servers)

    @command_syntax("stop [server1 server2 ...]")
    def cmd_stop(self, *servers):
        self.invoke('stop', servers)

    @command_syntax("restart [server1 server2 ...]")
    def cmd_restart(self, *servers):
        self.invoke('restart', servers)

    @command_syntax("status [server1 server2 ...]")
    def cmd_status(self, *servers):
        self.invoke('status', servers)

    @command_syntax("send <command> [server1 server2 ...]")
    def cmd_send(self, command, *servers):
        self.invoke('send', servers, command)

    @command_syntax("wipe [server1 server2 ...]")
    def cmd_wipe(self, *servers):
        self.invoke('wipe', servers)