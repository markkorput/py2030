#!/usr/bin/env python
import unittest
from pyhoh.dynamic_events import DynamicEvents
from pyhoh.components.event_to_event import EventToEvent

class TestEventToEvent(unittest.TestCase):
    def test_init(self):
        event2event = EventToEvent()
        self.assertIsNone(event2event.dynamic_events)

    def test_setup(self):
        e2e = EventToEvent({'abc': 'def'})
        dynamic_events = DynamicEvents()
        self.assertEqual(dynamic_events.getEvent('abc').getSubscriberCount(), 0)
        e2e.setup(dynamic_events)
        self.assertEqual(e2e.dynamic_events, dynamic_events)
        self.assertEqual(dynamic_events.getEvent('abc').getSubscriberCount(), 1)

    def test_destroy(self):
        e2e = EventToEvent({'abc': 'def'})
        dynamic_events = DynamicEvents()
        e2e.setup(dynamic_events)
        self.assertEqual(dynamic_events.getEvent('abc').getSubscriberCount(), 1)
        e2e.destroy()
        self.assertIsNone(e2e.dynamic_events)
        self.assertEqual(dynamic_events.getEvent('abc').getSubscriberCount(), 0)

    def test_events_triggers_other_events(self):
        e2e = EventToEvent({'event1': ['aa', 'bb', 'cc'], 'event2': ['bb', 'dd'], 'event3': 'bb'})
        dynamic_events = DynamicEvents()
        e2e.setup(dynamic_events)
        self.assertEqual(dynamic_events.getEvent('event1')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('event2')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('event3')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('aa')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('bb')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('cc')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('dd')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('event1').getSubscriberCount(), 3)
        dynamic_events.getEvent('event1').fire()
        self.assertEqual(dynamic_events.getEvent('event1')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('event2')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('event3')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('aa')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('bb')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('cc')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('dd')._fireCount, 0)
        dynamic_events.getEvent('event2').fire()
        self.assertEqual(dynamic_events.getEvent('event1')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('event2')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('event3')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('aa')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('bb')._fireCount, 2)
        self.assertEqual(dynamic_events.getEvent('cc')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('dd')._fireCount, 1)
        dynamic_events.getEvent('event3').fire()
        self.assertEqual(dynamic_events.getEvent('event1')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('event2')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('event3')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('aa')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('bb')._fireCount, 3)
        self.assertEqual(dynamic_events.getEvent('cc')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('dd')._fireCount, 1)
