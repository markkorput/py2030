#!/usr/bin/env python
import time
import logging
from evento import Event
from py2030.base_component import BaseComponent

try:
    import rtmidi
except ImportError as err:
    logging.getLogger(__name__).warning("Importing of rtmidi failed, MidiOutput component will not work.")
    rtmidi = None
del rtmidi
rtmidi = None

class ValueListener:
    def __init__(self, midi, cmd, ch, event, logger):
        self.midi = midi
        self.cmd = cmd
        self.ch = ch
        self.event = event
        self.event += self._output
        self.logger = logger

    def _output(self, val):
        if not self.midi:
            return

        val = int(max(0,val))
        msg = [int(self.cmd), int(self.ch), val]
        if self.midi:
            self.midi.send_message(msg)
        self.logger.debug('midi output value: '+str(val))

class PercentageListener:
    def __init__(self, midi, cmd, ch, event, logger):
        self.midi = midi
        self.cmd = cmd
        self.ch = ch
        self.event = event

        self.minValue = 0.0 # make configurable?
        self.maxValue = 127.0 # make configurable?
        self.valueRangeSize = self.maxValue - self.minValue
        self.logger = logger

        self.event += self._output

    def _output(self, percentage):
        # percentage to value
        val = int(self.minValue + self.valueRangeSize * min(1.0, max(0.0, percentage)));
        msg = [int(self.cmd), int(self.ch), val]
        if self.midi:
            self.midi.send_message(msg)
        self.logger.debug('midi output percentage value: '+str(val))

class MidiOutput(BaseComponent):
    config_name = 'midi_outputs'

    def __init__(self, options = {}):
        # params
        self.options = options
        # attributes
        self.port = self.options['port'] if 'port' in self.options else None
        self.midi = None
        # self.port_name = None
        self.limit = 10
        self.connected = False
        self.event_manager = None
        self.listeners = []

        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        # events
        self.messageEvent = Event()

    def __del__(self):
        self.destroy()

    def setup(self, event_manager=None, midi_port=None):
        self.event_manager = event_manager

        if rtmidi:
            self.logger.debug('available midi outputs: '+str(rtmidi.MidiOut().get_ports()))

        if midi_port == None:
            self._connect()
        else:
            self.midi = midi_port
            self.connected = True

        if 'input_events' in self.options:
            if 'channel_values' in self.options['input_events']:
                self._setup_input_channel_values(self.options['input_events']['channel_values'])

            if 'channel_percentages' in self.options['input_events']:
                self._setup_input_channel_percentages(self.options['input_events']['channel_percentages'])

    def _setup_input_channel_values(self, data):
        for cmd in data:
            for channel in data[cmd]:
                event_name = data[cmd][channel]
                self.logger.debug('input event for cmd: '+str(cmd)+' and ch: '+str(channel)+' event: '+event_name)
                event = self.event_manager.get(event_name)
                rec = ValueListener(self.midi, cmd, channel, event, self.logger)
                self.listeners.append(rec)

    def _setup_input_channel_percentages(self, data):
        for cmd in data:
            for channel in data[cmd]:
                event_name = data[cmd][channel]
                self.logger.debug('percentage input event for cmd: '+str(cmd)+' and ch: '+str(channel)+' event: '+event_name)
                event = self.event_manager.get(event_name)
                rec = PercentageListener(self.midi, cmd, channel, event, self.logger)
                self.listeners.append(rec)

    def destroy(self):
        if self.midi:
            self._disconnect()

        self.event_manager = None

    def _connect(self):
        if not rtmidi:
            self.logger.warning('rtmidi library not available MidiOutput cannot connect.')
            return

        try:
            self.midi = rtmidi.MidiOut().open_port(self.port)
        except IOError as err:
            print("Failed to initialize MIDI interface:", err)
            self.midi = None
            # self.port_name = None
            self.connected = False
            return
        except EOFError as err:
            print("Failed to initialize MIDI interface")
            self.midi = None
            # self.port_name = None
            self.connected = False
            return
        print("Midi output initialized on port: " + str(self.port))
        self.connected = True

    def _disconnect(self):
        self.midi.close_port()
        self.midi = None
        self.connected = False
