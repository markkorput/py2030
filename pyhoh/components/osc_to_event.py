import logging

class OscToEvent:
    def __init__(self, options = {}):
        self.options = options
        self.osc_input = None
        self.event_manager = None
        self.mapping=None

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)

    def __del__(self):
        self.destroy()

    def setup(self, osc_input, event_manager):
        self.osc_input = osc_input
        self.event_manager = event_manager
        self.osc_input.messageEvent += self._onOscMessage

        self.mapping = {}
        for key, val in self.options.items():
            if type(val).__name__ == 'str':
                self.mapping[key] = val

    def destroy(self):
        self.mapping = None
        if self.osc_input:
            self.osc_input.messageEvent -= self._onOscMessage
        self.osc_input = None
        self.event_manager = None

    def _onOscMessage(self, addr, *args, **kargs):
        if addr in self.mapping:
            event_name = self.mapping[addr]
            self.logger.debug('OSC message `{}` triggers event `{}`'.format(addr, event_name))
            self.event_manager.getEvent(event_name).fire()

        elif 'auto' in self.options and self.options['auto']:
            self.logger.debug('OSC message `{}` triggers event `{}`'.format(addr, addr))
            self.event_manager.getEvent(addr).fire()
