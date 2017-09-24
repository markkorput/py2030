#!/usr/bin/env python
import time
import logging
from evento import Event
from py2030.base_component import BaseComponent

try:
    import pysimpledmx
except ImportError:
    pysimpledmx = None

class DmxOutput(BaseComponent):
    config_name = 'dmx_outputs'

    def __init__(self, options = {}):
        self.options = options
        self.event_manager = None
        self.output_events = None

        self.num_channels = self.options['num_channels'] if 'num_channels' in self.options else 10
        self.channel_event_prefix = self.options['channel_event_prefix'] if 'channel_event_prefix' in self.options else 'ch'
        self.deviceName = self.options['deviceName'] if 'deviceName' in self.options else None
        self.deviceNumber = int(self.options['deviceNumber']) if 'deviceNumber' in self.options else None

        self.fps = self.options['fps'] if 'fps' in self.options else 4.0
        self.frameTime = 1.0 / self.fps

        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        # events
        self.messageEvent = Event()
        self.dirty = True;
        self.nextFrameTime = 0.0

    def setup(self, event_manager=None):
        self.event_manager = event_manager

        if not pysimpledmx:
            self.logger.warn("pysimpledmx lib not loaded")
            self.dmx = None
        else:
            if self.deviceName != None:
                self.dmx = pysimpledmx.DMXConnection(self.deviceName)
            elif self.deviceNumber != None:
                self.dmx = pysimpledmx.DMXConnection(self.deviceNumber)

        if self.dmx:
            self.dmx.clear()

        for i in range(self.num_channels):
            evt = self.event_manager.get(self.channel_event_prefix+str(i+1))
            evt += lambda val, idx=i: self._setChannel(idx, val)

        self.logger.debug('registered event listeners for '+str(self.num_channels)+' channels')

    def update(self):
        t = time.time()
        if self.dirty and t >= self.nextFrameTime:
            # dmx update
            if self.dmx != None:
                self.dmx.render()

            self.logger.debug('DMX update')
            self.nextFrameTime = t + self.frameTime
            self.dirty = False

    def destroy(self):
        if self.dmx:
            self.dmx.clear()
            self.dmx.render()
            self.dmx.close()
            self.dmx = None

        # remove events from event manager, good idea?
        for i in range(self.num_channels):
            self.event_manager.remove(self.channel_event_prefix+str(i))

        self.event_manager = None
        self.output_events = None

    def _setChannel(self, idx, val):
        # self.logger.debug('_setChannel: '+str(idx+1)+' with: '+str(val)+' ('+str(int(val * 255.0))+')')
        if self.dmx != None:
            self.dmx.setChannel(idx+1, int(val * 255.0))
        self.dirty = True
