#!/usr/bin/env python
import unittest
import helper
from pyhoh.dynamic_events import DynamicEvents

class TestDynamicEvents(unittest.TestCase):
    def test_init(self):
        dynevents = DynamicEvents()
        self.assertIsNotNone(dynevents.eventAddedEvent)
        self.assertEqual(len(dynevents._events), 0)

    def test_create_event(self):
        dynevents = DynamicEvents()
        self.assertEqual('foo' in dynevents._events, False)
        event = dynevents.getEvent('foo')
        self.assertEqual('foo' in dynevents._events, True)
        self.assertEqual(dynevents._events['foo'], event)
        self.assertEqual(len(dynevents._events), 1)

    def test_get_existing_event(self):
        dynevents = DynamicEvents()
        event1 = dynevents.getEvent('bar')
        event2 = dynevents.getEvent('bar')
        self.assertEqual(event1, event2)
        self.assertEqual(len(dynevents._events), 1)

    def test_non_existing_event(self):
        dynevents = DynamicEvents()
        event1 = dynevents.getEvent('bar')
        event2 = dynevents.getEvent('foo', create=False)
        event3 = dynevents.getEvent('bar', create=False)
        self.assertIsNone(event2)
        self.assertEqual(event1, event3)
