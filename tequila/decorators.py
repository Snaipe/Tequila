from functools import wraps
import inspect


def command_syntax(syntax):
    def wrapper(func):
        func.syntax = syntax
        return func
    return wrapper


def ctl_commands(commands):
    def wrapper(clazz):
        for cmd in commands:
            def ctl(self):
                self.invokectl('start')
            setattr(clazz, cmd, ctl)
    return wrapper


def initializer(fun):
    names, varargs, keywords, defaults = inspect.getargspec(fun)

    @wraps(fun)
    def wrapper(self, *args, **kargs):
        for name, arg in zip(names[1:], args) + kargs.items():
            setattr(self, name, arg)
        fun(self, *args, **kargs)
    return wrapper