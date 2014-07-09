from functools import wraps
import inspect


def command_syntax(syntax):
    def wrapper(func):
        func.syntax = syntax
        return func
    return wrapper


def ctl_commands(commands):
    def decorator(clz):
        for cmd in commands:
            def ctl(self):
                self.invokectl(cmd)
            setattr(clz, cmd, ctl)
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