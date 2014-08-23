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
import os
from baker import command, Baker
import sys

from .server import Server
from .server.instance import ServerInstance, InstancePolicy, InstanceGroup
from .server.group import ServerGroup
from .util import get_uid


def get_controllable(name, load=False, watch=True):

    if name[0] == '@':
        group = ServerGroup(name[1:])
        group.load(load, watch)

        return group

    elif '#' in name:
        real_name, instance_id = name.split('#', 1)

        server = Server(real_name)
        if load:
            server.load(watch)

        if '-' in instance_id:
            smin, smax = instance_id.split('-', 1)
            min, max = int(smin), int(smax)

            instances = []
            for i in range(max - min + 1):
                instances.append(ServerInstance(server, min + i))
            controllable = InstanceGroup(server, instances)
        else:
            controllable = ServerInstance(server, int(instance_id))

        return controllable
    else:
        server = Server(name)
        return server.load(watch) if load else server


@command(name='init')
def cmd_init(server, force=False, merge=False):
    """
    Creates a new server and populates it with configuration files
    :param server: The server to initialize
    """
    Server(server).init(force, merge)


@command(name='delete')
def cmd_delete(server):
    """
    Deletes an existing server
    :param server: The server to delete
    """
    Server(server).load(watch=False).delete()


@command(name='deploy')
def cmd_deploy(server):
    """
    Deploys a server, copying all binaries where they belong
    :param server: The server to deploy
    """
    server = Server(server).load()
    if get_uid(server.config.get_user()) != os.getuid():
        server.logger.error('Please run this command as user \'%s\'.', server.config.get_user())
        return

    server.deploy()


@command(name='status')
def cmd_status(entity=None):
    """
    Prints the status of Tequila or one entity.
    :param entity: The entity to get the status from.
    """
    if entity:
        print(get_controllable(entity, load=True, watch=False).status())
    else:
        from . import Tequila
        tequila = Tequila()

        print('[== Servers ==]')
        for s in tequila.get_servers():
            server = Server(s)
            try:
                msg = server.load(watch=False).status()
            except:
                msg = server.get_status_error()

            print('  - ' + msg)

        print('\n[== Groups ==]')
        for g in tequila.get_groups():
            group = ServerGroup(g)
            try:
                msg = group.load(load_servers=False, watch=False).status()
            except:
                msg = group.name + ': Error'

            print('  - ' + msg)

@command(name='start')
def cmd_start(server):
    """
    Starts an entity.
    :param entity: The entity to start
    """
    controllable = get_controllable(server, load=True)
    if isinstance(controllable, ServerInstance) or isinstance(controllable, InstanceGroup):

        serv = controllable.server

        if not serv.config.are_instances_enabled():
            serv.logger.error('Multiple instances are not enabled for this server.')
            return

        if serv.config.get_instance_policy() == InstancePolicy.union:
            error = False
            if os.getuid() != 0:
                serv.logger.error('Union-type instances must be started as root. '
                                  'Do not worry, the server jar will still be run '
                                  'as the user specified in the configuration.')
                error = True

            if serv.config.get_wrapper_type() == 'screen':
                serv.logger.error('Union-type instances must not use screen as a wrapper. '
                                  'You cannot hope to send commands or do anything other than reattaching with '
                                  'multiple users, meaning you would have to manually stop and clean up yourself.')
                error = True

            if error:
                return

        elif get_uid(serv.config.get_user()) != os.getuid():
            serv.logger.error('Please run this command as user \'%s\'.', serv.config.get_user())
            return

    elif isinstance(controllable, Server):
        if get_uid(controllable.config.get_user()) != os.getuid():
            controllable.logger.error('Please run this command as user \'%s\'.', controllable.config.get_user())
            return

    controllable.start()


@command(name='stop', shortopts={'force': 'f', 'Force': 'F'})
def cmd_stop(entity, force=False, Force=False):
    """
    Stops an entity.
    :param entity: The entity to stop
    :param force: send a SIGTERM to the entity
    :param Force: send a SIGKILL to the entity
    """
    get_controllable(entity, load=True, watch=False).stop(force, Force)


@command(name='restart', shortopts={'force': 'f', 'Force': 'F'})
def cmd_restart(entity, force=False, Force=False):
    """
    Restarts an entity.
    :param server: The entity to restart
    :param force: send a SIGTERM to the entity
    :param Force: send a SIGKILL to the entity
    """
    get_controllable(entity, load=True, watch=False).stop(force, Force)
    cmd_start(entity)


@command(name='send')
def cmd_send(entity, *command):
    """
    Send a command to an entity.
    :param entity: The entity to start
    :param command: the command to send
    """
    get_controllable(entity, load=True, watch=False).send(' '.join(command))


group_bakery = Baker()


@command(name='group')
def cmd_group(*args, **kwargs):
    """
    The main group subcommand.
    """
    group_bakery.run(argv=[' '.join(sys.argv[:2])] + sys.argv[2:])


@group_bakery.command(name='init')
def cmd_group_init(name):
    """
    Create a new server group.
    :param name: The name of the group to create (without @)
    """
    ServerGroup(name).save()


@group_bakery.command(name='add')
def cmd_group_add(name, server):
    """
    Adds a server to the server group.
    :param name: The name of the server group
    :param server: The name of the server to add
    """
    ServerGroup(name).load(watch=False).add_server(Server(server)).save()


@group_bakery.command(name='rm')
def cmd_group_rm(name, server):
    """
    Removes a server from the server group.
    :param name: The name of the server group
    :param server: The name of the server to remove
    """
    ServerGroup(name).load(watch=False).remove_server(Server(server)).save()


@group_bakery.command(name='delete')
def cmd_group_delete(name):
    """
    Deletes a server group.
    :param name: The name of the server group to delete
    """
    os.remove(ServerGroup(name).file)


@command(name='download')
def cmd_download(*urls):
    """
    Download and install an artifact from an url.
    :param urls: the urls to download
    """
    from urllib.request import FancyURLopener
    from tequila.network.maven import ArtifactResolver

    maven_resolver = ArtifactResolver()
    for url in urls:
        maven_resolver.install_plugin_jar(FancyURLopener(), url)