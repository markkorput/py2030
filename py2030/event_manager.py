from evento import Event

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
        if hasattr(config_data, '__iter__'):
            return  config_data
        return [config_data]
