import logging

class MidiToOmx:
    def __init__(self, options = {}):
        # config
        self.options = options
        # attributes
        self.midi_input = None
        self.omxvideo = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)

    def __del__(self):
        self.destroy()

    def setup(self, midi_input, omxvideo):
        self.destroy()
        self.midi_input = midi_input
        self.omxvideo = omxvideo
        # register callback
        if self.midi_input:
            self.midi_input.messageEvent += self._onMidiMessage

    def destroy(self):
        if self.midi_input:
            self.midi_input.messageEvent -= self._onMidiMessage
            self.midi_input = None
        # self.omxvideo = None

    def _onMidiMessage(self, msg):
        action, params = self._midiToOmx(msg)

        if not action:
            self.logger.debug('no omx action specified for midi note {0},{1}'.format(msg[0][0], msg[0][1]))
            return

        if not self.omxvideo:
            self.logger.warning('no mxvideo component specified to perform action on')
            return

        if action == 'play':
            self.omxvideo.play()
            return

        if action == 'start' and len(params) > 0:
            self.omxvideo.start(params[0])
            return

        if action == 'load' and len(params) > 0:
            self.omxvideo.load(params[0])
            return

        if action == 'stop':
            self.omxvideo.stop()
            return

        if action == 'pause':
            self.omxvideo.pause()
            return

        if action == 'toggle':
            self.omxvideo.toggle()
            return

        if action == 'seek' and len(params) > 0:
            self.omxvideo.seek(params[0])
            return

        if action == 'speed' and len(params) > 0:
            self.omxvideo.speed(params[0])
            return

        self.logger.debug('midi note ({0}, {1}) did not map to any omx action'.format(msg[0][0], msg[0][1]))

    def _midiToOmx(self, msg):
        if not msg[0][0] in self.options:
            return (None, [])

        cur = self.options[msg[0][0]]

        if not msg[0][1] in cur:
            return (None, [])

        cur = cur[msg[0][1]]

        return (cur['action'] if 'action' in cur else None, cur['params'] if 'params' in cur else [])
