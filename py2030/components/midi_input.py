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

        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        # events
        self.messageEvent = Event()

    def __del__(self):
        self.destroy()

    def setup(self):
        # start listening for midi messages
        # (we'll poll for new message in the update method)
        self._connect()
        # reset timer
        # self.time = 0

    def destroy(self):
        if self.midiin:
            self._disconnect()

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
        return

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
