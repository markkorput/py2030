import logging

class EventOscTrigger:
    def __init__(self, event, osc_output, osc_message):
        self.event = event
        self.osc_output = osc_output
        self.osc_message = osc_message

    def __del__(self):
        self.destroy()

    def setup(self):
        self.event += self._onEvent

    def destroy(self):
        if self._onEvent in self.event:
            self.event -= self._onEvent

    def _onEvent(self):
        self.osc_output.sendMessage(self.osc_message)

class EventToOsc:
    def __init__(self, options = {}):
        self.options = options
        self.event_manager = None
        self.osc_output = None
        self._triggers = []

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)

    def __del__(self):
        self.destroy()

    def setup(self, osc_output, event_manager):
        self.event_manager = event_manager
        self.osc_output = osc_output

        for key, val in self.options.items():
            # skip non-string properties (like the boolean 'verbose' property)
            if type(val).__name__ != 'str':
                continue

            trigger = EventOscTrigger(self.event_manager.getEvent(key), self.osc_output, val)
            trigger.setup()
            self._triggers.append(trigger)

    def destroy(self):
        for trigger in self._triggers:
            trigger.destroy()

        self._triggers = []
        self.event_manager = None
        self.osc_output = None
