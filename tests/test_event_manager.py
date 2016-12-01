#!/usr/bin/env python
import unittest
from pyhoh.event_manager import EventManager

class TestEventManager(unittest.TestCase):
    def test_init(self):
        event_manager = EventManager()
        self.assertIsNotNone(event_manager.eventAddedEvent)
        self.assertEqual(len(event_manager._events), 0)

    def test_create_event(self):
        event_manager = EventManager()
        self.assertEqual('foo' in event_manager._events, False)
        event = event_manager.getEvent('foo')
        self.assertEqual('foo' in event_manager._events, True)
        self.assertEqual(event_manager._events['foo'], event)
        self.assertEqual(len(event_manager._events), 1)

    def test_get_existing_event(self):
        event_manager = EventManager()
        event1 = event_manager.getEvent('bar')
        event2 = event_manager.getEvent('bar')
        self.assertEqual(event1, event2)
        self.assertEqual(len(event_manager._events), 1)

    def test_non_existing_event(self):
        event_manager = EventManager()
        event1 = event_manager.getEvent('bar')
        event2 = event_manager.getEvent('foo', create=False)
        event3 = event_manager.getEvent('bar', create=False)
        self.assertIsNone(event2)
        self.assertEqual(event1, event3)
