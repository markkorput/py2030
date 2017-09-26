#!/usr/bin/env python
import time
import logging
from evento import Event
from py2030.base_component import BaseComponent

try:
    import pysimpledmx
except ImportError:
    pysimpledmx = None

class LightCeremonyController(BaseComponent):
    config_name = 'lightCeremonyControllers'

    def __init__(self, options = {}):
        self.options = options
        self.event_manager = None
        self.output_events = None
        self.input_events = self.options['input_events'] if 'input_events' in self.options else {}
        self.resetUpMaxDuration = self.getOption('resetUpMaxDuration', 10.0)

        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        self.bResetUpActive = False
        self.bResetDownActive = False
        self.bPlaying = False

    def setup(self, event_manager=None):
        self.event_manager = event_manager
        self.getInputEvent('resetUp').subscribe(self._onResetUpCmd)
        self.getInputEvent('resetDown').subscribe(self._onResetDownCmd)
        self.getInputEvent('play1').subscribe(self._onPlay1)
        self.event_manager.get('play1-winchVel').subscribe(self._onPlay1WinchVel)
        self.event_manager.get('play1-rotVel').subscribe(self._onPlay1rotVel)

    def update(self):
        t = time.time()

        if self.bResetUpActive and t >= self.resetUpEndTime:
            self._endResetUp()

        if self.bResetDownActive and t >= self.resetDownEndTime:
            self._endResetDown()

    # RESET UP

    def _onResetUpCmd(self):
        if self.bResetDownActive:
            return;

        if self.bResetUpActive:
            self._endResetUp()
        else:
            self._startResetUp()

    def _startResetUp(self):
        self.logger.debug('starting reset-up...')
        t = time.time()
        self.resetUpEndTime = t + self.resetUpMaxDuration
        self.event_manager.get('winchResetUpVel').fire(self.getOption('resetUpVelocity', 0.25))
        self.event_manager.get('resetUpActive').fire(0.5) # midi out;
        self.bResetUpActive = True
        self.bPlaying = False

    def _endResetUp(self):
        self.logger.debug('ending reset-up...')
        self.event_manager.get('winchResetUpVel').fire(0.0)
        self.event_manager.get('resetUpActive').fire(0.0) # midi out;
        self.bResetUpActive = False

    # RESET DOWN

    def _onResetDownCmd(self):
        if self.bResetUpActive:
            return;

        if self.bResetDownActive:
            self._endResetDown()
        else:
            self._startResetDown()

    def _startResetDown(self):
        self.logger.debug('starting reset down...')
        t = time.time()
        self.resetDownEndTime = t + self.getOption('resetDownMaxDuration', 20.0)
        self.event_manager.get('winchResetDownVel').fire(self.getOption('resetDownVelocity', 0.2))
        self.bResetDownActive = True
        self.bPlaying = False

    def _endResetDown(self):
        self.logger.debug('ending reset down...')
        self.event_manager.get('winchResetDownVel').fire(0.0)
        self.bResetDownActive = False

    def _onPlay1(self):
        self.bPlaying = True

    def _onPlay1WinchVel(self, vel):
        if self.bPlaying:
            self.event_manager.get('winchVel').fire(vel)

    def _onPlay1RotVel(self, vel):
        if self.bPlaying:
            self.event_manager.get('rotVel').fire(vel)
