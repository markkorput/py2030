import copy
from datetime import datetime
import logging
logging.basicConfig(level=logging.WARNING)


from utils.config_file import ConfigFile

class ComponentManager:
    def __init__(self, options = {}):
        # config
        self.options = options
        self.logger = logging.getLogger(__name__)
        if self.options.verbose:
            self.logger.setLevel(logging.DEBUG)

        # attributes
        self.profile = self.options.profile
        self.config_file = ConfigFile('config/config.yml')
        self.components = []
        self.update_components = []
        self.destroy_components = []
        self.running = True

    def __del__(self):
        self.destroy()

    def setup(self):
        self.logger.debug('profile: {0}'.format(self.profile))

        # read config file content
        self.config_file.load()

        # load components based on profile configuration
        self._load_components(self.config_file.get_value('pyhoh.profiles.'+self.profile))

    def destroy(self):
        for comp in self.destroy_components:
            comp.destroy()

        self.components = []
        self.update_components = []
        self.destroy_components = []

    def update(self):
        for comp in self.update_components:
            comp.update()

    def _load_components(self, profile_data = None):
        # read profile data form config file
        if not profile_data:
            profile_data = {}

        omxvideo = None
        if 'omxvideo' in profile_data:
            from components.omxvideo import OmxVideo
            omxvideo = OmxVideo(profile_data['omxvideo'])
            self._add_component(omxvideo)
            del OmxVideo

        if 'omxvideo_osc_inputs' in profile_data:
            from components.omx_video_osc_input import OmxVideoOscInput

            # loop over each osc_input profile
            for data in profile_data['omxvideo_osc_inputs'].values():
                comp = OmxVideoOscInput(data)
                comp.set_omxvideo(omxvideo)
                comp.setup()
                self._add_component(comp) # auto-starts

            del OmxVideoOscInput

        if 'omxsync' in profile_data:
            from components.omxsync import OmxSync
            comp = OmxSync(profile_data['omxsync'])
            comp.setup(omxvideo)
            self._add_component(comp)
            del OmxSync

        if 'osc_inputs' in profile_data:
            from components.osc_input import OscInput

            # loop over each osc_input profile
            for data in profile_data['osc_inputs'].values():
                comp = OscInput(data)
                comp.setup()
                self._add_component(comp) # auto-starts

            del OscInput

        osc_outputs = []
        if 'osc_outputs' in profile_data:
            from components.osc_output import OscOutput
            # loop over each osc_output profile
            for data in profile_data['osc_outputs'].values():
                comp = OscOutput(data)
                comp.setup()
                self._add_component(comp) # auto-starts
                osc_outputs.append(comp)
            del OscOutput

        midi_inputs = {}
        if 'midi_inputs' in profile_data:
            from components.midi_input import MidiInput
            for name in profile_data['midi_inputs']:
                data = profile_data['midi_inputs'][name]
                comp = MidiInput(data)
                comp.setup()
                self._add_component(comp)
                midi_inputs[name] = comp
            del MidiInput

        if 'midi_to_osc' in profile_data:
            from components.midi_to_osc import MidiToOsc
            for name in profile_data['midi_to_osc']:
                if not name in midi_inputs:
                    self.logger.warning('unknown midi_input name: {0}'.format(name))
                    continue

                data = profile_data['midi_to_osc'][name]
                comp = MidiToOsc(data)
                comp.setup(midi_inputs[name], osc_outputs) # give it a midi_input component and all the osc_output components
                self._add_component(comp)
            del MidiToOsc

    def _add_component(self, comp):
        if hasattr(comp, 'update') and type(comp.update).__name__ == 'instancemethod':
            self.update_components.append(comp)

        if hasattr(comp, 'destroy') and type(comp.destroy).__name__ == 'instancemethod':
            self.destroy_components.append(comp)

        self.components.append(comp)
