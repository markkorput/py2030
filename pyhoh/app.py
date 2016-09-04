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

        omxvideo = None
        if 'omxvideo' in profile_data:
            from components.omxvideo import OmxVideo
            omxvideo = OmxVideo(profile_data['omxvideo'])
            self.components.append(omxvideo)
            del OmxVideo

        if 'omxvideo_osc_inputs' in profile_data:
            from components.omx_video_osc_input import OmxVideoOscInput

            # loop over each osc_input profile
            for data in profile_data['omxvideo_osc_inputs'].values():
                comp = OmxVideoOscInput(data)
                comp.set_omxvideo(omxvideo)
                comp.setup()
                self.components.append(comp) # auto-starts

            del OmxVideoOscInput

        if 'omxsync' in profile_data:
            from components.omxsync import OmxSync
            comp = OmxSync(profile_data['omxsync'])
            comp.setup(omxvideo)
            self.components.append(comp)
            del OmxSync

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
