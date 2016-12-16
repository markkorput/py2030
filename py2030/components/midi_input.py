#!/usr/bin/env python
import time
import logging
from evento import Event

try:
    from rtmidi.midiutil import open_midiport
except ImportError as err:
    logging.getLogger(__name__).warning("Importing of rtmidi.midiutil failed, MidiInput component will not work.")
    open_midiport = False

class MidiInput:
    def __init__(self, options = {}):
        # params
        self.options = options
        # attributes
        self.port = self.options['port'] if 'port' in self.options else None
        self.midiin = None
        self.port_name = None
        self.limit = 10
        self.connected = False
        self.event_manager = None
        self.output_events = None

        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        # events
        self.messageEvent = Event()

    def __del__(self):
        self.destroy()

    def setup(self, event_manager=None, midi_port=None):
        self.event_manager = event_manager
        # start listening for midi messages
        # (we'll poll for new message in the update method)
        if midi_port == None:
            self._connect()
        else:
            self.midiin = midi_port
            self.connected = True
        # reset timer
        # self.time = 0

        self.output_events = self.options['output_events'] if self.event_manager != None and 'output_events' in self.options else {}

    def destroy(self):
        if self.midiin:
            self._disconnect()

        self.event_manager = None
        self.output_events = None

    def _connect(self):
        if not open_midiport:
            self.logger.warning('rtmidi library not available MidiInput cannot connect.')
            return

        try:
            self.midiin, self.port_name = open_midiport(self.port)
        except IOError as err:
            print "Failed to initialize MIDI interface:", err
            self.midiin = None
            self.port_name = None
            self.connected = False
            return
        except EOFError as err:
            print("Failed to initialize MIDI interface")
            self.midiin = None
            self.port_name = None
            self.connected = False
            return
        print("Midi input initialized on port: " + self.port_name)
        self.connected = True

    def _disconnect(self):
        self.midiin.close_port()
        self.midiin = None
        self.connected = False

    def update(self):
        if not self.midiin:
            return

        for i in range(self.limit):
            # get next incoming midi message
            msg = self.midiin.get_message()

            # if no more messages; we're done
            if not msg:
                return

            # skip note off (??)
            if len(msg) > 0 and len(msg[0]) > 2 and msg[0][2] == 0 or msg[0][0] == 128:
                continue

            # self.time += msg[1]
            self.logger.debug('midi message: {0}'.format(msg))
            self.messageEvent(msg)

            if msg[0][0] in self.output_events:
                data = self.output_events[msg[0][0]]
                if msg[0][1] in data:
                    for event in self.event_manager.config_to_events(data[msg[0][1]]):
                        event.fire()

# for manual testing this python file can be invoked directly
if __name__ == '__main__':
    mt = MidiInput()

    print("Entering main loop. Press Control-C to exit.")
    try:
        while True:
            mt.update()
            time.sleep(0.01)
    except KeyboardInterrupt:
        print('Keyboard Interrupt')

    del mt
