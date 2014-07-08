import logging
import os
from shutil import copytree
from subprocess import call
from tequila import Environment

from tequila.config import Config
#from tequila.download import DownloadManager
from tequila.decorators import ctl_commands, command_syntax


@ctl_commands(['start', 'stop', 'restart', 'status', 'send'])
class Server(object):

    def __init__(self, name):
        from os.path import join
        self.name = name
        self.home = join(Environment['SERVER_HOME'], name)
        self.config_dir = join(self.home, "config")
        self.config = Config(self.config_dir)

    def setup(self):
        copytree(Environment['RESOURCE_HOME'], self.home)
        os.chmod(self.home, 0o755)

    def invokectl(self, cmd):
        from os.path import join
        call([join(self.home, 'serverctl'), cmd])


class ServerManager(object):
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self.servers = {}
        for server in os.listdir(Environment['SERVER_HOME']):
            self.servers[server] = Server(server)

        #self.download_manager = DownloadManager()

    @command_syntax("new <server name>")
    def cmd_new(self, name):
        if name in self.servers:
            self.logger.error('Could not create server %s : server already exists.', name)
            return

        self.logger.info('Successfully created the new server at %s. '
                         'Take the time to configure it, then run the install command to set it up.',
                         self.servers[name].home)

    @command_syntax("install <server name>")
    def cmd_install(self, name):
        if name not in self.servers:
            print('Server %s does not exist.' % name)
            return

        #self.download_manager.install(name)

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