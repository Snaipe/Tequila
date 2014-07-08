import logging
import sys

from tequila.server import ServerManager


def main():
    from os import makedirs
    logging.basicConfig(format="[%(name)s] %(message)s")
    logger = logging.getLogger("Tequila")

    makedirs('servers', 0o775, True)

    mgr = ServerManager()

    methods = {}
    for method in dir(mgr):
        attr = getattr(mgr, method)
        if callable(attr) and method.startswith('cmd_'):
            methods[method] = attr

    try:
        methods['cmd_' + sys.argv[1]](*sys.argv[2:])
    except KeyError:
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