import logging
from time import time

class DelayItem:
    def __init__(self, _id, source, delay, target, halt=None, pause=None, logger=None):
        self.id = _id
        self.sourceEvent = source
        self.delay = delay
        self.targetEvent = target
        self.haltEvent = halt
        self.pauseEvent = pause
        self.timer = 0
        self.logger = logger
        if not self.logger:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
        self.active = True

    def setup(self):
        self.sourceEvent += self._onSource

        if self.haltEvent != None:
            self.haltEvent += self._onHalt

        if self.pauseEvent != None:
            self.pauseEvent += self._onPause

    def destroy(self):
        self.sourceEvent -= self._onSource

        if self.haltEvent != None:
            self.haltEvent -= self._onHalt

        if self.pauseEvent != None:
            self.pauseEvent -= self._onPause

    def update(self, dt=None):
        if self.timer <= 0 or not self.active:
            return # we're not running

        self.timer -= dt # count down

        if self.timer <= 0:
            # trigger target event
            self.logger.debug('DelayItem with ID `{0}` triggering target event'.format(self.id))
            self.targetEvent()

    def _onSource(self):
        self.logger.debug('DelayItem with ID `{0}` triggered by source event'.format(self.id))
        self.timer = self.delay
        self.active = True

    def _onHalt(self):
        self.logger.debug('DelayItem with ID `{0}` halted'.format(self.id))
        self.active = False

    def _onPause(self):
        self.logger.debug('DelayItem with ID `{0}` toggled'.format(self.id))
        self.active = not self.active

class DelayEvents:
    def __init__(self, options = {}):
        self.options = options
        self.event_manager = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)
        self._delay_items = []
        self._last_update = None

    def __del__(self):
        self.destroy()

    def setup(self, event_manager):
        self.event_manager = event_manager
        self._delay_items = self._options_to_delay_items()

        for delay_item in self._delay_items:
            delay_item.setup()

        self._last_update = time()

    def destroy(self):
        for delay_item in self._delay_items:
            delay_item.destroy()

        self._delay_items = []
        self.event_manager = None

    def update(self, dt=None):
        if not dt:
            t = time()
            dt = t - self._last_update
            self._last_update = t

        for delay_item in self._delay_items:
            delay_item.update(dt)

    def _options_to_delay_items(self):
        delay_items = []

        for _id, params in self.options.items():
            if not hasattr(params, '__iter__'):
                continue

            if not 'source' in params:
                self.logger.warning('delay_event configuration with id {0} misses the `source` param'.format(id))
                continue
            if not 'delay' in params:
                self.logger.warning('delay_event configuration with id {0} misses the `delay` param'.format(id))
                continue
            if not 'target' in params:
                self.logger.warning('delay_event configuration with id {0} misses the `target` param'.format(id))
                continue

            delay = params['delay']
            sourceEvent = self.event_manager.get(params['source'])
            targetEvent = self.event_manager.get(params['target'])
            haltEvent = self.event_manager.get(params['halt']) if 'halt' in params else None
            pauseEvent = self.event_manager.get(params['pause']) if 'pause' in params else None
            delay_items.append(DelayItem(_id, sourceEvent, delay, targetEvent, halt=haltEvent, pause=pauseEvent, logger=self.logger))
        return delay_items
