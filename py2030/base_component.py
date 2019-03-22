import logging
from evento import Event

class BaseComponent:
    config_name = None

    def __init__(self, options):
        self.options = options
        self.name = ''
        self.event_manager = None # TODO: also pass this in through event_manager and call setup at end of __init__

        # setup logging
        self.verbose = self.getOption('verbose', False)
        self.logger = logging.getLogger(self.config_name)
        loglevel = self.getOption('loglevel', None)
        loglevelmapping = {'CRITICAL':logging.CRITICAL, 'ERROR':logging.CRITICAL, 'WARNING':logging.WARNING, 'INFO':logging.INFO, 'DEBUG':logging.DEBUG, 'NOTSET':logging.NOTSET}

        if loglevel and loglevel in loglevelmapping:
            self.logger.setLevel(loglevelmapping[loglevel])
        elif self.verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.destroy_funcs = []

    def __del__(self):
        self.destroy()

    def setup(self, event_manager):
        self.event_manager = event_manager
        self.logger.info("SETUP instance: "+self.config_name+"#"+self.name)

    def destroy(self):
        for func in self.destroy_funcs:
            func()
        self.destroy_funcs = []

    def onDestroy(self, func):
        self.destroy_funcs.append(func)

    @classmethod
    def create_components(cls, config, context):
        comps = []

        for key in config:
            comp = cls(config[key])
            comp.name = key
            comp.setup(context.event_manager)
            comps.append(comp)

        return comps

    # helper methods

    def opt(self, optName, default=None):
        return self.getOption(optName, default)

    def getOption(self, optName, default=None):
        if optName in self.options:
            return self.options[optName]
        # else
        return default

    def getInputEvent(self, eventName, dummy=True):
        return self.getEventFrom('input_events', eventName, dummy)

    def getOutputEventsData(self, fallback={}):
        return self.options['output_events'] if 'output_events' in self.options else fallback

    def getOutputEvent(self, eventName, dummy=True):
        return self.getEventFrom('output_events', eventName, dummy)

    def getEventFrom(self, configName, eventName, dummy=True):
        if configName in self.options and eventName in self.options[configName] and self.event_manager:
            return self.event_manager.get(self.options[configName][eventName])

        # else
        return Event() if dummy else None
