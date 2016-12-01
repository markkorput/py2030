class OscToEvent:
    def __init__(self, options = {}):
        self.options = options
        self.osc_input = None
        self.event_manager = None

    def setup(self, osc_input, event_manager):
        self.osc_input = osc_input
        self.event_manager = event_manager
        self.osc_input.messageEvent += self._onOscMessage

    def _onOscMessage(self, addr, *args, **kargs):
        if addr in self.options:
            self.event_manager.getEvent(self.options[addr]).fire()
