import logging

class EventToOmx:
    def __init__(self, options = {}):
        self.options = options
        self.event_manager = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)

    def setup(self, event_manager, omxvideo):
        self.event_manager = event_manager
        self.omxvideo = omxvideo

        for eventName, config in self.options.items():
            if eventName == 'verbose':
                continue

            if not hasattr(config, '__iter__'):
                action = config
            elif not 'action' in config:
                self.logger.debug('`{0}` config has no action attribute'.format(eventName))
                continue
            else:
                action = config['action']

            event = self.event_manager.getEvent(eventName)

            if action == 'start':
                event += lambda: self._onStart(0)
                continue

            if action == 'stop':
                event += self._onStop
                continue

            if action == 'toggle':
                event += self._onToggle
                continue

            self.logger.debug("unkown action: {0}".format(action))

    def _onStart(self, idx):
        self.logger.debug('OMX START')
        self.omxvideo.start(idx)

    def _onStop(self):
        self.logger.debug('OMX STOP')
        self.omxvideo.stop()

    def _onToggle(self):
        self.logger.debug('OMX TOGGLE')
        self.omxvideo.toggle()
