import logging, math, time
from evento import Event
from py2030.base_component import BaseComponent

class Sine(BaseComponent):
    config_name = 'sines'

    def __init__(self, options = {}):
        self.options = options
        self.amplitude = options['amplitude'] if 'amplitude' in options else 1.0
        self.frequency = options['frequency'] if 'frequency' in options else 1.0

        # attributes
        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

    def setup(self, event_manager=None):
        self.event_manager = event_manager

        self.cursor = 0.0
        self.cursorSpeed = self.frequency * math.pi * 2.0

        if self.event_manager and 'output_events' in self.options and 'value' in self.options['output_events']:
            # get the event to use for distributing the sine-value during update
            self.valueEvent = self.event_manager.get(self.options['output_events']['value'])
        else:
            # dummy event
            self.valueEvent = Event()

        self.sleep = None
        if 'sleep' in self.options:
            self.sleep = self.options['sleep']

        self.lastUpdateTime = time.time()

    def update(self, dt=None):
        if not dt:
            t = time.time()
            dt = t - self.lastUpdateTime
            self.lastUpdateTime = t

        self.cursor += self.cursorSpeed * dt
        self.valueEvent(math.sin(self.cursor) * self.amplitude)

        if self.sleep:
            time.sleep(self.sleep)
