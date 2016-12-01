import logging

class DelayItem:
    def __init__(self, _id, source, delay, effect):
        self.id = _id
        self.sourceEvent = source
        self.delay = delay
        self.effectEvent = effect
        self.timer = 0

    def setup(self):
        self.sourceEvent += self.trigger

    def destroy(self):
        self.sourceEvent -= self.trigger

    def trigger(self):
        self.timer = self.delay

    def update(self, dt):
        if self.timer <= 0:
            return # we're not running

        self.timer -= dt # count down

        if self.timer <= 0:
            # trigger effect event
            self.effectEvent()

class DelayEvents:
    def __init__(self, options = {}):
        self.options = options
        self.dynamic_events = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)
        self._delay_items = []

    def __del__(self):
        self.destroy()

    def setup(self, dynamic_events):
        self.dynamic_events = dynamic_events
        self._delay_items = self._options_to_delay_items()

        for delay_item in self._delay_items:
            delay_item.setup()

    def destroy(self):
        for delay_item in self._delay_items:
            delay_item.destroy()

        self._delay_items = []
        self.dynamic_events = None

    def update(self, dt):
        for delay_item in self._delay_items:
            delay_item.update(dt)

    def _options_to_delay_items(self):
        delay_items = []

        for _id, params in self.options.items():
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
            effectEvent = self.dynamic_events.getEvent(params['target'])
            delay_items.append(DelayItem(_id, sourceEvent, delay, effectEvent))
        return delay_items
