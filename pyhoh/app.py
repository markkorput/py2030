import copy
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from utils.config_file import ConfigFile

class App:
    def __init__(self, options = {}):
        # config
        self.options = options
        self.profile = self.options['profile'] if 'profile' in self.options else 'default'

        # attributes
        self.config_file = ConfigFile('config/config.yml')
        # self.profile_data = {}

        # components
        self.components = []

    def __del__(self):
        self.destroy()

    def setup(self):
        # read config file content
        self.config_file.load()

        # apply config data
        self._apply_config(self.config_file)

    def destroy(self):
        for comp in self.components:
            comp.destroy()

    def update(self):
        for comp in self.components:
            comp.update()

    def _apply_config(self, config_file):
        pass



if __name__ == '__main__':
    app = App()
    app.setup()

    try:
        while True:
            app.update()
    except KeyboardInterrupt:
        print 'KeyboardInterrupt. Quitting.'

    app.destroy()
