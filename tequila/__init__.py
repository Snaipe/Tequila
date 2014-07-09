

def build_environment():
    from tequila.path import expand
    return {
        'TEQUILA_HOME':       expand('~tequila/'),
        'RESOURCE_DIRECTORY': expand('~tequila/resources'),
        'ROOT_DIRECTORY':     expand('~tequila/../'),
        'SERVER_HOME':        expand('~tequila/../servers')
    }

Environment = build_environment()