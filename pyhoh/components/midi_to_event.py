import logging

class MidiToEvent:
    def __init__(self, options={}):
        self.options = options
        self.midi_input = None
        self.event_manager = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)

    def setup(self, midi_input, event_manager):
        self.midi_input = midi_input
        self.event_manager = event_manager
        self.midi_input.messageEvent += self._onMidiMessageEvent

    def destroy(self):
        if self.midi_input:
            self.midi_input.messageEvent -= self._onMidiMessageEvent

        self.midi_input = None
        self.event_manager = None

    def _onMidiMessageEvent(self, msg):
        eventId = self._midiMessageToEventId(msg)

        if eventId:
            # get event instance
            event = self.event_manager.getEvent(eventId)
            # trigger event (calls listeners)
            self.logger.debug('Midi message {0}/{1} triggered event {2}'.format(msg[0][0], msg[0][1], eventId))
            event()

    def _midiMessageToEventId(self, msg):
        if not msg[0][0] in self.options:
            return None

        cur = self.options[msg[0][0]]

        if msg[0][1] in cur:
            return cur[msg[0][1]]

        return None
