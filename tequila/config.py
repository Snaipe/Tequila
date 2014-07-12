import os
import configparser
from tequila.decorators import config_node


class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()

    def load(self):
        self.config.read(self.config_file)

    def save(self):
        self.config.write(self.config_file)

    def __getitem__(self, section):
        self.get_section(section)

    def get_section(self, section):
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
            except:
                print("Could not get %s option." % option)
                dict1[option] = None
        return dict1

    def get(self, section, entry, default=None):
        try:
            return self.config.get(section, entry)
        except:
            return default

    def sections(self):
        return self.config.sections()


class ServerConfig(Config):

    @config_node('general', 'server')
    def get_server_bin(self):
        return 'org.bukkit:craftbukkit:1.7.9-R0.3'

    @config_node('general', 'user')
    def get_user(self):
        return 'minecraft'

    @config_node('directories', 'plugins')
    def get_plugins_dir(self):
        return 'plugins'

    @config_node('directories', 'worlds')
    def get_worlds_dir(self):
        return 'worlds'

    @config_node('options', 'jvm')
    def get_jvm_opt_file(self):
        return 'jvm.opts'

    @config_node('directories', 'application')
    def get_app_opt_file(self):
        return 'application.opts'

    def get_repositories(self):
        return self.get_section('repositories')

    def get_plugins(self):
        return self.get_section('plugins')
