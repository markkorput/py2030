import logging

class MidiToOsc:
    def __init__(self, options = {}):
        # config
        self.options = options
        # attributes
        self.midi_input = None
        self.osc_outputs = []
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)

    def __del__(self):
        self.destroy()

    def setup(self, midi_input, osc_outputs):
        self.destroy()
        self.midi_input = midi_input
        self.osc_outputs = osc_outputs
        # register callback
        if self.midi_input:
            self.midi_input.messageEvent += self._onMidiMessage

    def destroy(self):
        if self.midi_input:
            self.midi_input.messageEvent -= self._onMidiMessage
            self.midi_input = None
        self.osc_outputs = []

    def _onMidiMessage(self, msg):
        oscmsg = self._midiToOsc(msg)

        if not oscmsg:
            self.logger.debug('no osc message specified for midi note {0},{1}'.format(msg[0][0], msg[0][1]))
            return

        self.logger.debug('midi note ({0}, {1}) mapping to osc message: {2}'.format(msg[0][0], msg[0][1], oscmsg))

        for oscout in self.osc_outputs:
            oscout.sendMessage(oscmsg)

    def _midiToOsc(self, msg):
        if not msg[0][0] in self.options:
            return None

        cur = self.options[msg[0][0]]

        if not msg[0][1] in cur:
            return None

        return cur[msg[0][1]]
