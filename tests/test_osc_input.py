#!/usr/bin/env python
import unittest

from py2030.components.osc_input import OscInput
from py2030.event_manager import EventManager

class TestOscInput(unittest.TestCase):
    def test_init(self):
        oscinput = OscInput()
        self.assertFalse(oscinput.connected)
        self.assertFalse(oscinput.running)

    def test_setup_with_event_manager(self):
        oscinput = OscInput()
        em = EventManager()
        oscinput.setup(em)
        self.assertEqual(oscinput.event_manager, em)

    def test_setup_without_event_manager(self):
        oscinput = OscInput()
        oscinput.setup()
        self.assertIsNone(oscinput.event_manager)

    def test_output_events_option(self):
        oscinput = OscInput({'output_events': {'/test': 'event1'}})
        oscinput.setup(EventManager())
        self.assertEqual(oscinput.event_manager.get('event1')._fireCount, 0)
        oscinput._onOscMsg('/test')
        self.assertEqual(oscinput.event_manager.get('event1')._fireCount, 1)

    def test_output_events_option_auto(self):
        oscinput = OscInput({'output_events': {'auto': True}})
        oscinput.setup(EventManager())
        self.assertEqual(oscinput.event_manager.get('/random')._fireCount, 0)
        oscinput._onOscMsg('/random')
        self.assertEqual(oscinput.event_manager.get('/random')._fireCount, 1)

    def test_output_events_explicit_value_with_auto_enabled(self):
        oscinput = OscInput({'output_events': {'auto': True, '/explicit': 'some_event'}})
        oscinput.setup(EventManager())
        self.assertEqual(oscinput.event_manager.get('some_event')._fireCount, 0)
        oscinput._onOscMsg('/explicit')
        self.assertEqual(oscinput.event_manager.get('some_event')._fireCount, 1)
