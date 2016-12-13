#!/usr/bin/env python
import unittest
from py2030.event_manager import EventManager

class TestEventManager(unittest.TestCase):
    def test_init(self):
        event_manager = EventManager()
        self.assertIsNotNone(event_manager.eventAddedEvent)
        self.assertEqual(len(event_manager._events), 0)

    def test_get_creates_event(self):
        em = EventManager()
        self.assertFalse('newbie' in em._events)
        event = em.get('newbie') # creates new event with this ID
        self.assertTrue('newbie' in em._events)
        self.assertEqual(len(em._events), 1)
        self.assertEqual(em._events['newbie'], event)
        self.assertTrue('fire' in dir(event))
        self.assertTrue('subscribe' in dir(event))
        self.assertTrue('unsubscribe' in dir(event))

    def test_get_returns_existing_event(self):
        em = EventManager()
        event1 = em.get('bar')
        event2 = em.get('bar')
        self.assertEqual(event1, event2)
        self.assertEqual(len(em._events), 1)

    def test_get_returns_none_for_non_existing_events(self):
        em = EventManager()
        event1 = em.get('bar')
        event2 = em.get('foo', create=False)
        event3 = em.get('bar', create=False)
        self.assertIsNone(event2)
        self.assertEqual(event1, event3)

    def test_get_maps_non_string_params_to_strings(self):
        em = EventManager()
        self.assertEqual(em.get(3), em.get('3'))
        self.assertEqual(em.get(True), em.get('True'))

    def test_fire_existing(self):
        em = EventManager()
        event = em.get('some_event')
        self.assertEqual(event._fireCount, 0)
        em.fire('some_event')
        self.assertEqual(event._fireCount, 1)
        event.fire()
        self.assertEqual(event._fireCount, 2)
        event()
        self.assertEqual(event._fireCount, 3)
        em.fire('some_event')
        self.assertEqual(event._fireCount, 4)

    def test_fire_new(self):
        em = EventManager()
        em.fire('another')
        event = em.get('another')
        self.assertEqual(event._fireCount, 1)

    def test_fire_doesnt_create_event(self):
        em = EventManager()
        em.fire('another', create=False)
        event = em.get('another')
        self.assertEqual(event._fireCount, 0)
