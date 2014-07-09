import logging
import sys
from tequila import Environment
from tequila.maven import ArtifactResolver, Repository, Artifact

from tequila.server import ServerManager


def main():
    from os import makedirs
    logging.basicConfig(level='INFO', format="[%(name)s] %(message)s")
    logger = logging.getLogger("Tequila")

    # resolver = ArtifactResolver()
    # resolver.repositories = [
    #     Repository('md5', 'http://repo.md-5.net/content/groups/public/'),
    #     Repository('sk89q', 'http://maven.sk89q.com/repo/')
    # ]
    #
    # resolver.enqueue(Artifact('com.sk89q', 'worldedit', '6.0.0-SNAPSHOT'))
    # resolver.enqueue(Artifact('com.sk89q', 'worldedit', '5.6.2'))
    # resolver.enqueue(Artifact('com.sk89q', 'worldedit', '5.6.1'))
    # resolver.enqueue(Artifact('com.sk89q', 'worldedit', '5.6'))
    #
    # resolver.resolve()
    #
    # return

    makedirs(Environment['SERVER_HOME'], 0o775, True)

    mgr = ServerManager()

    methods = {}
    for method in dir(mgr):
        attr = getattr(mgr, method)
        if callable(attr) and method.startswith('cmd_'):
            methods[method] = attr

    if len(sys.argv) == 0:
        logger.error(
            "Usage: tequila <command> [parameters]. Valid commands are: %s",
            [k[4:] for k in methods.keys()])

    try:
        key = 'cmd_' + sys.argv[1]
        if key in methods:
            methods[key](*sys.argv[2:])
        else:
            logger.error(
                "Unknown command %s, valid commands are: %s",
                sys.argv[1],
                [k[4:] for k in methods.keys()])
    except TypeError:
        logger.error(
            "Invalid argument: syntax is \"%s\".",
            methods['cmd_' + sys.argv[1]].syntax)


if __name__ == '__main__':
    main()