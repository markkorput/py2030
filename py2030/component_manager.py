import copy, sys
from datetime import datetime
import logging
logging.basicConfig(level=logging.WARNING)

from .event_manager import EventManager
from .utils.config_file import ConfigFile

class Context:
    def __init__(self, event_manager):
        self.event_manager = event_manager

class ComponentManager:
    def __init__(self, options = {}):
        # config
        self.options = options

        logging.basicConfig()
        # logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        self.logger = logging.getLogger(__name__)
        if 'verbose' in self.options and self.options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        # attributes
        self.profile = self.options['profile'] if 'profile' in self.options else 'default'
        self.config_file = ConfigFile(self.options['config_file'] if 'config_file' in self.options and self.options['config_file'] else 'config.yml')
        self.components = []
        self.update_components = []
        self.destroy_components = []
        self.context = Context(EventManager())
        self._profile_data = None
        self.gotNextUpdateOps = False
        self.running = False
        self.restart = False
        self.shutdown_message = "py2030, over and out.\n"

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
                self.logger.warning("No profile data found for profile: {0}\nTrying 'default'".format(self.profile))
                self.profile = 'default'
                self._profile_data = self.config_file.get_value('py2030.profiles.'+self.profile, default_value={})

        # load components based on profile configuration
        self._load_components(self._profile_data)

        if 'reload_event' in self._profile_data:
            self.context.event_manager.get(self._profile_data['reload_event']).subscribe(self._onReloadEvent)

        if 'stop_event' in self._profile_data:
            self.context.event_manager.get(self._profile_data['stop_event']).subscribe(self._onStopEvent)

        if 'restart_event' in self._profile_data:
            self.context.event_manager.get(self._profile_data['restart_event']).subscribe(self._onRestartEvent)

        if len(self.components) > 0:
            self.running = True
        else:
            self.logger.warning('No components loaded. Abort.')

        if 'shutdown_message' in self._profile_data:
            self.shutdown_message = self._profile_data['shutdown_message']

        if 'start_event' in self._profile_data:
            self.logger.debug('triggering start_event: ' + str(self._profile_data['start_event']))
            self.context.event_manager.get(self._profile_data['start_event']).fire()
        else:
            if 'args' in self.options and self.options['args'] and len(self.options['args']) == 1:
                arg = self.options['args'][0]
                self.logger.debug('triggering arg: ' + arg)
                self.context.event_manager.get(arg).fire()

    def _onStopEvent(self):
        self.logger.debug('stop_event triggered')
        self.running = False

    def _onRestartEvent(self):
        self.logger.debug('restart_event triggered')
        self.restart = True
        self.running = False

    def _onReloadEvent(self):
        self.logger.debug('reload_event triggered')
        self.nextUpdate(self._reload)

    def _reload(self):
        self.logger.info('-- Reloading --')
        self.destroy()
        self.config_file.load({'force': True})
        self._profile_data = self.config_file.get_value('py2030.profiles.'+self.profile, default_value={})
        self.setup()

    def destroy(self):
        if self._profile_data and 'reload_event' in self._profile_data:
            self.context.event_manager.get(self._profile_data['reload_event']).unsubscribe(self._onReloadEvent)

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

        if self.gotNextUpdateOps:
            for op in self._op_queue:
                op()
            del self._op_queue
            self.gotNextUpdateOps = False

    def get_components_from(module, ignores=[]):
        comps = []
        # find component class inside the module
        for klass in module.__dict__.values():
            # skip ignored classes
            if klass in ignores:
                continue

            # only grab the classes that have config_name and create_components attributes
            if hasattr(klass, 'config_name') and hasattr(klass, 'create_components'):
                comps.append(klass)
        return comps

    def _found_component_classes(self):
        import py2030.components as comp_modules
        from py2030.base_component import BaseComponent

        mods = self.options['modules'].copy() if 'modules' in self.options else [] # provided modules

        # got local (default py2030) modules
        for module_name in comp_modules.__all__:
            # ignore the __init__.py file
            # if module_name == '__init__':
            #     continue

            # import file
            mod = __import__('py2030.components.'+module_name, fromlist=['py2030.components'])
            mods.append(mod)

        klasses = []
        for module in mods:
            klasses += ComponentManager.get_components_from(module, ignores=[BaseComponent])

        del comp_modules
        del BaseComponent
        # print('klasses: ',klasses)

        return klasses

    def _load_components(self, profile_data = None):
        klasses = self._found_component_classes()

        # loop over all configurations in our profile
        for config_name, config_data in profile_data.items():
            # let all classes that say they are responsible for this piece of configuration generate component(s)
            # print ('looking for component: ', config_name, config_data)
            for klass in klasses:
                if klass.config_name == config_name:
                    comps = klass.create_components(config_data, self.context)

                    if not hasattr(comps, '__iter__'):
                        self.logger.warning("Module with component_config_name {0} returned non-iterable components list".format(config_name))
                        continue

                    for comp in comps:
                        self._add_component(comp)

                    break


        return

    def _add_component(self, comp):
        if hasattr(comp, 'update'):
            if type(comp.update).__name__ == 'instancemethod' or type(comp.update).__name__ == 'method':
                self.update_components.append(comp)

        if hasattr(comp, 'destroy'):
            if type(comp.destroy).__name__ == 'instancemethod' or type(comp.destroy).__name__ == 'method':
                self.destroy_components.append(comp)

        self.components.append(comp)

    # operation

    def nextUpdate(self, func):
        if not hasattr(self, '_op_queue'):
            self._op_queue = []
        self._op_queue.append(func)
        self.gotNextUpdateOps = True
