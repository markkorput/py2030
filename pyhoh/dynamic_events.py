from evento import Event

class DynamicEvents:
    def __init__(self):
        self._events = {}
        self.eventAddedEvent = Event()

    def getEvent(self, id, create=True):
        if id in self._events:
            return self._events[id]

        if create:
            new_event = Event()
            self._events[id] = new_event
            return new_event

        # don't create
        return None
