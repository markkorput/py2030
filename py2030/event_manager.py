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
