import logging
from time import time

class DelayItem:
    def __init__(self, _id, source, delay, target, logger=None):
        self.id = _id
        self.sourceEvent = source
        self.delay = delay
        self.targetEvent = target
        self.timer = 0
        self.logger = logger
        if not self.logger:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)

    def setup(self):
        self.sourceEvent += self.trigger

    def destroy(self):
        self.sourceEvent -= self.trigger

    def trigger(self):
        self.timer = self.delay
        self.logger.debug('DelayItem with ID `{0}` triggered by source event'.format(self.id))

    def update(self, dt=None):
        if self.timer <= 0:
            return # we're not running

        self.timer -= dt # count down

        if self.timer <= 0:
            # trigger target event
            self.targetEvent()
            self.logger.debug('DelayItem with ID `{0}` triggered target event'.format(self.id))

class DelayEvents:
    def __init__(self, options = {}):
        self.options = options
        self.dynamic_events = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)
        self._delay_items = []
        self._last_update = None

    def __del__(self):
        self.destroy()

    def setup(self, dynamic_events):
        self.dynamic_events = dynamic_events
        self._delay_items = self._options_to_delay_items()

        for delay_item in self._delay_items:
            delay_item.setup()

        self._last_update = time()

    def destroy(self):
        for delay_item in self._delay_items:
            delay_item.destroy()

        self._delay_items = []
        self.dynamic_events = None

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
            sourceEvent = self.dynamic_events.getEvent(params['source'])
            targetEvent = self.dynamic_events.getEvent(params['target'])
            delay_items.append(DelayItem(_id, sourceEvent, delay, targetEvent, logger=self.logger))
        return delay_items
