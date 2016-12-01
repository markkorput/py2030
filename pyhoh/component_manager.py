import copy
from datetime import datetime
import logging
logging.basicConfig(level=logging.WARNING)

from event_manager import EventManager
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
        self.event_manager = EventManager()

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

        if 'event_to_event' in profile_data:
            from components.event_to_event import EventToEvent
            comp = EventToEvent(profile_data['event_to_event'])
            comp.setup(self.event_manager)
            self._add_component(comp)
            del EventToEvent

        if 'delay_events' in profile_data:
            from components.delay_events import DelayEvents
            comp = DelayEvents(profile_data['delay_events'])
            comp.setup(self.event_manager)
            self._add_component(comp)
            del DelayEvents

        omxvideo = None
        if 'omxvideo' in profile_data:
            from components.omxvideo import OmxVideo
            omxvideo = OmxVideo(profile_data['omxvideo'])
            self._add_component(omxvideo)
            del OmxVideo

        if 'event_to_omx' in profile_data:
            if omxvideo == None:
                self.logger.warning("No omxvideo loaded, can't initialize event_to_omx component")
            else:
                from components.event_to_omx import EventToOmx
                comp = EventToOmx(profile_data['event_to_omx'])
                comp.setup(self.event_manager, omxvideo)
                self._add_component(comp)
                del EventToOmx

        if 'omxvideo_osc_inputs' in profile_data:
            from components.omx_video_osc_input import OmxVideoOscInput

            # loop over each osc_input profile
            for data in profile_data['omxvideo_osc_inputs'].values():
                comp = OmxVideoOscInput(data)
                comp.set_omxvideo(omxvideo)
                comp.setup()
                self._add_component(comp) # auto-starts

            del OmxVideoOscInput

        if omxvideo and 'omxsyncer' in profile_data:
                from components.omxsyncer import OmxSyncer
                comp = OmxSyncer(profile_data['omxsyncer'])
                comp.setup(omxvideo)
                self._add_component(comp)
                del OmxSyncer

        osc_inputs = {}
        if 'osc_inputs' in profile_data:
            from components.osc_input import OscInput

            # loop over each osc_input profile
            for name in profile_data['osc_inputs']:
                data = profile_data['osc_inputs'][name]
                comp = OscInput(data)
                comp.setup()
                self._add_component(comp) # auto-starts
                osc_inputs[name] = comp

            del OscInput

        osc_outputs = {}
        if 'osc_outputs' in profile_data:
            from components.osc_output import OscOutput
            # loop over each osc_output profile
            for name in profile_data['osc_outputs']:
                data = profile_data['osc_outputs'][name]
                comp = OscOutput(data)
                comp.setup()
                self._add_component(comp) # auto-starts
                osc_outputs[name] = comp
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

        if 'midi_to_event' in profile_data:
            from components.midi_to_event import MidiToEvent
            for name in profile_data['midi_to_event']:
                if not name in midi_inputs:
                    self.logger.warning('unknown midi_input name `{0}` in midi_to_event config'.format(name))
                    continue

                data = profile_data['midi_to_event'][name]
                comp = MidiToEvent(data)
                comp.setup(midi_inputs[name], self.event_manager)
                self._add_component(comp)
            del MidiToEvent

        if 'midi_to_osc' in profile_data:
            from components.midi_to_osc import MidiToOsc
            for name in profile_data['midi_to_osc']:
                if not name in midi_inputs:
                    self.logger.warning('unknown midi_input name: {0}'.format(name))
                    continue

                data = profile_data['midi_to_osc'][name]
                comp = MidiToOsc(data)
                comp.setup(midi_inputs[name], osc_outputs.values()) # give it a midi_input component and all the osc_output components
                self._add_component(comp)
            del MidiToOsc

        if omxvideo and 'midi_to_omx' in profile_data:
            from components.midi_to_omx import MidiToOmx
            for name in profile_data['midi_to_omx']:
                if not name in midi_inputs:
                    self.logger.warning('unknown midi_input name: {0}'.format(name))
                    continue
                comp = MidiToOmx(profile_data['midi_to_omx'][name])
                comp.setup(midi_inputs[name], omxvideo)
                self._add_component(comp)
            del MidiToOmx

        if omxvideo and 'omx_osc_output' in profile_data:
            from components.omx_osc_output import OmxOscOutput
            for name in profile_data['omx_osc_output']:
                if not name in osc_outputs:
                    self.logger.warning('unknown osc_output name: {0}'.format(name))
                    continue
                comp = OmxOscOutput(profile_data['omx_osc_output'][name])
                comp.setup(omxvideo, osc_outputs[name])
                self._add_component(comp)
            del OmxOscOutput

        if 'osx_osc_video_resumer' in profile_data:
            from components.osx_osc_video_resumer import OsxOscVideoResumer
            for name in profile_data['osx_osc_video_resumer']:
                if not name in osc_inputs:
                    self.logger.warning('unknown osc_input name: {0}'.format(name))
                    continue
                comp = OsxOscVideoResumer(profile_data['osx_osc_video_resumer'][name])
                comp.setup(osc_inputs[name])
                self._add_component(comp)
            del OsxOscVideoResumer

    def _add_component(self, comp):
        if hasattr(comp, 'update') and type(comp.update).__name__ == 'instancemethod':
            self.update_components.append(comp)

        if hasattr(comp, 'destroy') and type(comp.destroy).__name__ == 'instancemethod':
            self.destroy_components.append(comp)

        self.components.append(comp)
