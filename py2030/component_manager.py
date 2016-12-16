import copy
from datetime import datetime
import logging
logging.basicConfig(level=logging.WARNING)

from .event_manager import EventManager
from .utils.config_file import ConfigFile

class ComponentManager:
    def __init__(self, options = {}):
        # config
        self.options = options

        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        if 'verbose' in self.options and self.options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        # attributes
        self.profile = self.options['profile'] if 'profile' in self.options else 'default'
        self.config_file = ConfigFile(self.options['config_file'] if 'config_file' in self.options and self.options['config_file'] else 'config.yml')
        self.components = []
        self.update_components = []
        self.destroy_components = []
        self.event_manager = EventManager()
        self._profile_data = None
        self._operation_queue = []
        self.running = False

    def __del__(self):
        self.destroy()

    def setup(self):
        self.logger.debug('config file: {0}'.format(self.config_file.path))
        self.logger.debug('profile: {0}'.format(self.profile))

        # load from option
        if self._profile_data == None and 'profile_data' in self.options:
            self._profile_data = self.options['profile_data']

        # load from config file
        if self._profile_data == None:
            # read config file content
            self.config_file.load()
            self._profile_data = self.config_file.get_value('py2030.profiles.'+self.profile, default_value={})
            if self._profile_data == {}:
                self.logger.warning("No profile data found")

        # load components based on profile configuration
        self._load_components(self._profile_data)

        if 'reload_event' in self._profile_data:
            self.event_manager.get(self._profile_data['reload_event']).subscribe(self._onReloadEvent)

        if 'stop_event' in self._profile_data:
            self.event_manager.get(self._profile_data['stop_event']).subscribe(self._onStopEvent)

        if len(self.components) > 0:
            self.running = True
        else:
            self.logger.warning('No components loaded. Abort.')

        if 'start_event' in self._profile_data:
            self.logger.debug('triggering start_event: ' + str(self._profile_data['start_event']))
            self.event_manager.get(self._profile_data['start_event']).fire()

    def _onStopEvent(self):
        self.logger.debug('stop_event triggered')
        self.running = False

    def _onReloadEvent(self):
        self.logger.debug('reload_event triggered')
        self._operation_queue.append(self._reload)

    def _reload(self):
        self.logger.info('-- Reloading --')
        self.destroy()
        self.config_file.load({'force': True})
        self._profile_data = self.config_file.get_value('py2030.profiles.'+self.profile, default_value={})
        self.setup()

    def destroy(self):
        if self._profile_data and 'reload_event' in self._profile_data:
            self.event_manager.get(self._profile_data['reload_event']).unsubscribe(self._onReloadEvent)

        for comp in self.destroy_components:
            comp.destroy()

        self.components = []
        self.update_components = []
        self.destroy_components = []
        self._profile_data = None
        self.running = False

    def update(self):
        for comp in self.update_components:
            comp.update()

        for op in self._operation_queue:
            op()
        self._operation_queue = []

    def _load_components(self, profile_data = None):
        # read profile data form config file
        if not profile_data:
            profile_data = {}

        if 'event_to_event' in profile_data:
            from .components.event_to_event import EventToEvent
            comp = EventToEvent(profile_data['event_to_event'])
            comp.setup(self.event_manager)
            self._add_component(comp)
            del EventToEvent

        if 'delay_events' in profile_data:
            from .components.delay_events import DelayEvents
            comp = DelayEvents(profile_data['delay_events'])
            comp.setup(self.event_manager)
            self._add_component(comp)
            del DelayEvents

        omxvideo = None
        if 'omxvideo' in profile_data:
            from .components.omxvideo import OmxVideo
            omxvideo = OmxVideo(profile_data['omxvideo'])
            omxvideo.setup(self.event_manager)
            self._add_component(omxvideo)
            del OmxVideo

        if omxvideo and 'omxsyncer' in profile_data:
            from .components.omxsyncer import OmxSyncer
            comp = OmxSyncer(profile_data['omxsyncer'])
            comp.setup(omxvideo)
            self._add_component(comp)
            del OmxSyncer

        osc_inputs = {}
        if 'osc_inputs' in profile_data:
            from .components.osc_input import OscInput

            # loop over each osc_input profile
            for name in profile_data['osc_inputs']:
                data = profile_data['osc_inputs'][name]
                comp = OscInput(data)
                comp.setup(self.event_manager)
                self._add_component(comp) # auto-starts
                osc_inputs[name] = comp

            del OscInput

        osc_outputs = {}
        if 'osc_outputs' in profile_data:
            from .components.osc_output import OscOutput
            # loop over each osc_output profile
            for name in profile_data['osc_outputs']:
                data = profile_data['osc_outputs'][name]
                comp = OscOutput(data)
                comp.setup(self.event_manager)
                self._add_component(comp) # auto-starts
                osc_outputs[name] = comp
            del OscOutput

        midi_inputs = {}
        if 'midi_inputs' in profile_data:
            from .components.midi_input import MidiInput
            for name in profile_data['midi_inputs']:
                data = profile_data['midi_inputs'][name]
                comp = MidiInput(data)
                comp.setup(self.event_manager)
                self._add_component(comp)
                midi_inputs[name] = comp
            del MidiInput

        if 'osx_osc_video_resumer' in profile_data:
            from .components.osx_osc_video_resumer import OsxOscVideoResumer
            for name in profile_data['osx_osc_video_resumer']:
                if not name in osc_inputs:
                    self.logger.warning('unknown osc_input name: {0}'.format(name))
                    continue
                comp = OsxOscVideoResumer(profile_data['osx_osc_video_resumer'][name])
                comp.setup(osc_inputs[name])
                self._add_component(comp)
            del OsxOscVideoResumer

        if 'ssh_remotes' in profile_data:
            from .components.ssh_remote import SshRemote
            for data in profile_data['ssh_remotes'].values():
                comp = SshRemote(data)
                comp.setup(self.event_manager)
                self._add_component(comp)
            del SshRemote

    def _add_component(self, comp):
        if hasattr(comp, 'update') and type(comp.update).__name__ == 'instancemethod':
            self.update_components.append(comp)

        if hasattr(comp, 'destroy') and type(comp.destroy).__name__ == 'instancemethod':
            self.destroy_components.append(comp)

        self.components.append(comp)
