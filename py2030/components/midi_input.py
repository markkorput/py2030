#!/usr/bin/env python
import time
import logging

from rtmidi.midiutil import open_midiport
from evento import Event

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
                    event_id = data[msg[0][1]]
                    self.logger.debug('firing output event: {0}'.format(event_id))
                    self.event_manager.fire(event_id)

    def _midiMessageToEventId(self, msg):
        if not msg[0][0] in self.options:
            return None

        cur = self.options[msg[0][0]]

        if msg[0][1] in cur:
            return cur[msg[0][1]]



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
