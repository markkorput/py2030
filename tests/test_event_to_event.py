#!/usr/bin/env python
import unittest
from py2030.event_manager import EventManager
from py2030.components.event_to_event import EventToEvent

class TestEventToEvent(unittest.TestCase):
    def test_init(self):
        event2event = EventToEvent()
        self.assertIsNone(event2event.event_manager)

    def test_setup(self):
        e2e = EventToEvent({'abc': 'def'})
        event_manager = EventManager()
        self.assertEqual(event_manager.getEvent('abc').getSubscriberCount(), 0)
        e2e.setup(event_manager)
        self.assertEqual(e2e.event_manager, event_manager)
        self.assertEqual(event_manager.getEvent('abc').getSubscriberCount(), 1)

    def test_destroy(self):
        e2e = EventToEvent({'abc': 'def'})
        event_manager = EventManager()
        e2e.setup(event_manager)
        self.assertEqual(event_manager.getEvent('abc').getSubscriberCount(), 1)
        e2e.destroy()
        self.assertIsNone(e2e.event_manager)
        self.assertEqual(event_manager.getEvent('abc').getSubscriberCount(), 0)

    def test_events_triggers_other_events(self):
        e2e = EventToEvent({'event1': ['aa', 'bb', 'cc'], 'event2': ['bb', 'dd'], 'event3': 'bb'})
        event_manager = EventManager()
        e2e.setup(event_manager)
        self.assertEqual(event_manager.getEvent('event1')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('event2')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('event3')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('aa')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('bb')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('cc')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('dd')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('event1').getSubscriberCount(), 3)
        event_manager.getEvent('event1').fire()
        self.assertEqual(event_manager.getEvent('event1')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('event2')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('event3')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('aa')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('bb')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('cc')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('dd')._fireCount, 0)
        event_manager.getEvent('event2').fire()
        self.assertEqual(event_manager.getEvent('event1')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('event2')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('event3')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('aa')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('bb')._fireCount, 2)
        self.assertEqual(event_manager.getEvent('cc')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('dd')._fireCount, 1)
        event_manager.getEvent('event3').fire()
        self.assertEqual(event_manager.getEvent('event1')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('event2')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('event3')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('aa')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('bb')._fireCount, 3)
        self.assertEqual(event_manager.getEvent('cc')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('dd')._fireCount, 1)
