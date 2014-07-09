import os
import configparser


class Config:
    def __init__(self, config_dir):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(config_dir, "tequila.config"))

    def __getitem__(self, section):
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
            except:
                print("Could not get %s option." % option)
                dict1[option] = None
        return dict1

    def sections(self):
        return self.config.sections()