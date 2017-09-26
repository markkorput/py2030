class BaseComponent:
    config_name = None

    @classmethod
    def create_components(cls, config, context):
        comps = []

        for data in config.values():
            comp = cls(data)
            comp.setup(context.event_manager)
            comps.append(comp)

        return comps

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
