#!/usr/bin/env python
import time
import logging
from evento import Event
from py2030.base_component import BaseComponent
from py2030.utils.CsvFramesFile import CsvFramesFile

try:
    import pysimpledmx
except ImportError:
    pysimpledmx = None

class LightCeremonyController(BaseComponent):
    config_name = 'lightCeremonyAnimReaders'

    def __init__(self, options = {}):
        self.options = options
        self.event_manager = None
        self.maxFramesPerCycle = self.getOption('maxFramesPerCycle', 5)
        self.sync = self.getOption('sync', True)

        self.logger = logging.getLogger(__name__)
        if self.getOption('verbose', False):
            self.logger.setLevel(logging.DEBUG)

        self.bPlaying = False
        self.bPaused = False
        self.pendingFrame = None

    def setup(self, event_manager):
        BaseComponent.setup(self, event_manager)

        self.framesReader = CsvFramesFile(path=self.getOption('file'), loop=self.getOption('loop', False), verbose=self.getOption('verbose', False))
        self.framesReader.open()

        self.frameEvent = self.getOutputEvent('frame')
        self.endEvent = self.getOutputEvent('end')

        self.getInputEvent('start').subscribe(self._start)
        self.getInputEvent('stop').subscribe(self._stop)
        self.getInputEvent('pause').subscribe(self._pause)
        self.getInputEvent('resume').subscribe(self._resume)
        self.getInputEvent('togglePaused').subscribe(self._togglePaused)

        if self.getOption('autoStart', False):
            self._start()

    def update(self):
        if not self.bPlaying:
            return

        # update our internal timer
        t = time.time()
        dt = t - self.lastUpdateTime
        self.playTime += dt * 1000.0
        self.lastUpdateTime = t

        # limit number of frame we can do per cycle
        for i in range(self.maxFramesPerCycle):
            if not self.pendingFrame:
                # read next frame from file
                data_strings = self.framesReader.getNextFrame()
                if not data_strings:
                    self.endEvent(self)
                    self._stop()
                    return

                # check length of list?

                # time (ms), winch velocity (-1.0 - 1.0), rotator velocity (-1.0 - 1.0), light brightness (0.0 - 1.0)
                self.pendingFrame = [long(data_strings[0]), float(data_strings[1]), float(data_strings[2]), float(data_strings[3])]

            if self.sync and self.pendingFrame[0] > self.playTime:
                return

            self.frameEvent(self.pendingFrame)
            self.frameCount += 1
            self.logger.debug('frame #'+str(self.frameCount)+', t:'+str(self.pendingFrame[0]))
            self.pendingFrame = None

    def _start(self):
        if self.bPlaying or self.bPaused:
            self._stop() # and rewind

        self.pendingFrame = None
        self.playTime = 0L
        self.frameCount = 0L
        self.lastUpdateTime = time.time()
        self.bPaused = False
        self.bPlaying = True

    def _stop(self):
        self.bPlaying = False
        self.bPaused = False
        self.framesReader.rewind()

    def _pause(self):
        if self.bPlaying:
            self.bPaused = True
            self.pauseTime = time.time()
            self.bPlaying = False

    def _resume(self):
        if self.bPaused:
            self.lastUpdateTime = time.time() - (self.pauseTime - self.lastUpdateTime)
            self.pauseTime = None
            self.bPaused = False
            self.bPlaying = True

    def _togglePaused(self):
        if self.bPaused:
            self._resume()
        elif self.bPlaying:
            self._pause()
