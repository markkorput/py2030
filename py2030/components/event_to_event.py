class EventToEvent:
    def __init__(self, options = {}):
        self.options = options
        self.event_manager = None

    def __del__(self):
        self.destroy()

    def setup(self, event_manager):
        self.event_manager = event_manager
        self._connect_events()

    def destroy(self):
        if self.event_manager:
            self._connect_events(False)
            self.event_manager = None

    def _connect_events(self, connect=True):
        # loop over each key/value pair in configuration hash
        for triggerName, effectNames in self.options.items():
            # the key is the name of the event that triggers other event(s)
            triggerEvent = self.event_manager.get(triggerName)

            # if the target events is not a list, turn it into a single-item list first
            if not hasattr(effectNames, '__iter__'):
                effectNames = [effectNames]

            # loop over all the target events name and connect them as listeners to the trigger event
            for effectName in effectNames:
                effectEvent = self.event_manager.get(effectName)
                if connect:
                    triggerEvent += effectEvent
                else:
                    triggerEvent -= effectEvent
