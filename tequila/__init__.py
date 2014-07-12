

def build_environment():
    from tequila.path import expand
    return {
        'TEQUILA_HOME':       expand('${tequila_home}/'),
        'RESOURCE_DIRECTORY': expand('${bin_dir}/resources'),
        'SERVER_HOME':        expand('${tequila_home}/servers')
    }

Environment = build_environment()