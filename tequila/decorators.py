from functools import wraps
import inspect
from tequila.exception import UnhandledException, TequilaException


def command_syntax(syntax):
    def wrapper(func):
        func.syntax = syntax
        return func
    return wrapper


def ctl_commands(commands):
    def add_function(clz, cmd):
        def ctl(self):
            self.invokectl(cmd)
        setattr(clz, cmd, ctl)

    def decorator(clz):
        for cmd in commands:
            add_function(clz, cmd)
        return clz
    return decorator


def initializer(fun):
    names, varargs, keywords, defaults = inspect.getargspec(fun)

    @wraps(fun)
    def wrapper(self, *args, **kargs):
        for name, arg in zip(names[1:], args) + kargs.items():
            setattr(self, name, arg)
        fun(self, *args, **kargs)
    return wrapper


def wrap_exception(fun):
    @wraps(fun)
    def wrapper(self, *args, **kargs):
        try:
            fun(self, *args, **kargs)
        except TequilaException:
            raise
        except Exception as e:
            raise UnhandledException() from e
    return wrapper


def config_node(section, node):
    def decorator(fun):
        @wraps(fun)
        def wrapper(self, *args, **kargs):
            return self.get(section, node, fun(self, *args, **kargs))
        return wrapper
    return decorator