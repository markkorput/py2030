from evento import Event

class ParamsEvent(Event):
    def setup(self, event, params=[]):
        self.event=event
        self.params=tuple(params)
        # subscribe custom listener to self
        self.subscribe(self._onFire)

    # our custom listener will trigger the specified event with the given (additional) args
    def _onFire(self, *args, **kwargs):
        new_args = args + self.params
        # trigger given event
        self.event(*new_args, **kwargs)


class EventManager:
    def __init__(self):
        self._events = {}
        self.eventAddedEvent = Event()

    def get(self, _id, create=True):
        _id = str(_id)

        # find existing
        if _id in self._events:
            return self._events[_id]

        # create new
        if create:
            new_event = Event()
            self._events[_id] = new_event
            self.eventAddedEvent(new_event)
            return new_event

        # don't create, return None
        return None

    def fire(self, _id, create=True):
        event = self.get(_id, create)
        if event != None:
            event.fire()

    # takes raw event config value -which can be in various forms
    # and returns a list of events it specifies.
    # Currently supported input formats;
    # - single string value, interpreted as event ID
    # - list of string values, interpreted as multiple event IDs
    def config_to_events(self, config_data):
        events = []

        if config_data.__class__ == {}.__class__ and 'event' in config_data: # we got a dict?
            if 'params' in config_data:
                params_event = ParamsEvent()
                params_event.setup(self.get(config_data['event'], config_data['params']))
                return [params_event]

            config_data = config_data['event']

        for event_id in self._config_to_event_ids(config_data):
            events.append(self.get(event_id))
        return events

    def _config_to_event_ids(self, config_data):
        if hasattr(config_data, '__iter__'):
            return  config_data
        return [config_data]
