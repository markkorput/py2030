from py2030.base_component import BaseComponent

class EventToEvent(BaseComponent):
    config_name = 'event_to_event'

    def __init__(self, options = {}):
        BaseComponent.__init__(self, options)

    def setup(self, event_manager):
        super().setup(event_manager)

        # loop over each key/value pair in configuration hash
        for triggerName, effectNames in self.options.items():
            # the key is the name of the event that triggers other event(s)
            triggerEvent = self.event_manager.get(triggerName)

            events = self.event_manager.config_to_events(effectNames)
            for event in events:
                triggerEvent += event
                # also register a cleanup logic
                self.onDestroy(lambda: triggerEvent.unsubscribe(event))
