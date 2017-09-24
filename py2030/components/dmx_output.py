#!/usr/bin/env python
import time
import logging
from evento import Event
from py2030.base_component import BaseComponent

class DmxOutput(BaseComponent):
    config_name = 'dmx_outputs'

    def __init__(self, options = {}):
        # params
        self.options = options
        # attributes
        # self.port = self.options['port'] if 'port' in self.options else None
        # self.midiin = None
        # self.port_name = None
        # self.limit = 10
        # self.connected = False
        self.num_channels = self.options['num_channels'] if 'num_channels' in self.options else 10
        self.channel_event_prefix = self.options['channel_event_prefix'] if 'channel_event_prefix' in self.options else 'ch'
        self.event_manager = None
        self.output_events = None
        self.fps = self.options['fps'] if 'fps' in self.options else 4.0
        self.frameTime = 1.0 / self.fps

        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        # events
        self.messageEvent = Event()
        self.dirty = True;
        self.nextFrameTime = 0.0

    def setup(self, event_manager=None, midi_port=None):
        self.event_manager = event_manager

        for i in range(self.num_channels):
            evt = self.event_manager.get(self.channel_event_prefix+str(i))
            evt += lambda val, idx=i: self._setChannel(idx, val)

        self.logger.debug('registered event listeners for '+str(self.num_channels)+' channels')

    def update(self):
        t = time.time()
        if self.dirty and t >= self.nextFrameTime:
            # dmx update
            self.logger.debug('DMX update')
            self.nextFrameTime = t + self.frameTime

    def destroy(self):
        # if self.midiin:
        #     self._disconnect()

        self.event_manager = None
        self.output_events = None

    def _setChannel(self, idx, val):
        self.logger.debug('_setChannel: '+str(idx)+' with: '+str(val))
        self.dirty = True
