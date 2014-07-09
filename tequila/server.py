import logging
import os
from shutil import copytree
from subprocess import call
from tequila import Environment

from tequila.config import Config
from tequila.decorators import ctl_commands, command_syntax
from tequila.maven import ArtifactResolver, Artifact, Repository


@ctl_commands(['start', 'stop', 'restart', 'status', 'send'])
class Server(object):

    def __init__(self, name):
        from os.path import join
        self.name = name
        self.home = join(Environment['SERVER_HOME'], name)
        self.config_dir = join(self.home, 'config')
        self.config = None
        self.plugin_home = None

    def load(self):
        from os.path import join, normpath
        self.config = Config(self.config_dir)
        self.plugin_home = normpath(join(self.home, self.config['directories']['plugins']))
        return self

    def setup(self):
        from os.path import join
        copytree(join(Environment['RESOURCE_DIRECTORY'], 'server_base'), self.home)
        for dir in self.config['directories'].values():
            os.makedirs(join(self.home, dir), 0o755, exist_ok=True)
        os.chmod(self.home, 0o755)

    def install(self):
        manual_downloads = {}
        maven_resolver = ArtifactResolver()
        maven_resolver.repositories = [Repository(name, repo) for (name, repo) in self.config['repositories'].items()]
        for (plugin_name, plugin_url) in self.config['plugins'].items():
            if plugin_url.startswith('maven://'):
                maven_resolver.enqueue(Artifact.from_url(plugin_url))
            elif plugin_url.startswith('http://') or \
                    plugin_url.startswith('https://') or \
                    plugin_url.startswith('ftp://'):
                manual_downloads[plugin_name] = plugin_url

        maven_resolver.resolve()
        maven_resolver.install(self.plugin_home)

    def invokectl(self, cmd):
        from os.path import join
        call([join(self.home, 'serverctl'), cmd])


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

    @command_syntax("new <server name>")
    def cmd_new(self, name):
        if name in self.servers:
            self.logger.error('Could not create server %s : server already exists.', name)
            return

        server = Server(name)
        server.setup()

        self.logger.info('Successfully created the new server at %s. '
                         'Take the time to configure it, then run the install command to set it up.',
                         server.home)

    @command_syntax("install <server name>")
    def cmd_install(self, name):
        if name not in self.servers:
            print('Server %s does not exist.' % name)
            return

        self.servers[name].install()

    def invoke(self, fun, servers, *args):
        if len(servers) == 0:
            servers = self.servers.values()

        for server in servers:
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
    def cmd_status(self, command, *servers):
        self.invoke('status', servers, command)