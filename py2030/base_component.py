import logging
from evento import Event

class BaseComponent:
    config_name = None

    def __init__(self, options):
        self.options = options

        self.logger = logging.getLogger(self.config_name)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

    def setup(self, event_manager):
        self.event_manager = event_manager

    @classmethod
    def create_components(cls, config, context):
        comps = []

        for data in config.values():
            comp = cls(data)
            comp.setup(context.event_manager)
            comps.append(comp)

        return comps

    # helper methods

    def getOption(self, optName, default=None):
        if optName in self.options:
            return self.options[optName]
        # else
        return default

    def getInputEvent(self, eventName, dummy=True):
        if 'input_events' in self.options and eventName in self.options['input_events'] and self.event_manager:
            return self.event_manager.get(self.options['input_events'][eventName])
        # else
        return Event() if dummy else None

    def getOutputEvent(self, eventName, dummy=True):
        if 'output_events' in self.options and eventName in self.options['output_events'] and self.event_manager:
            return self.event_manager.get(self.options['output_events'][eventName])
        # else
        return Event() if dummy else None
