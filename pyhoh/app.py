import copy
from datetime import datetime
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

from utils.config_file import ConfigFile

class App:
    def __init__(self, options = {}):
        # config
        self.options = options
        self.profile = self.options['profile'] if 'profile' in self.options else 'default'

        # attributes
        self.config_file = ConfigFile('config/config.yml')
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
        # read profile data form config file
        profile_data = config_file.get_value('pyhoh.profiles.'+self.profile)
        if not profile_data:
            profile_data = {}

        if 'osc_inputs' in profile_data:
            from components.osc_input import OscInput

            # loop over each osc_input profile
            for data in profile_data['osc_inputs'].values():
                comp = OscInput(data)
                comp.setup()
                self.components.append(comp) # auto-starts

            del OscInput

if __name__ == '__main__':
    app = App()
    app.setup()

    try:
        while True:
            app.update()
    except KeyboardInterrupt:
        print 'KeyboardInterrupt. Quitting.'

    app.destroy()
