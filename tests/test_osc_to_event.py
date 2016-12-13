#!/usr/bin/env python
import unittest
from py2030.event_manager import EventManager
from py2030.components.osc_input import OscInput
from py2030.components.osc_to_event import OscToEvent

class TestOscToEvent(unittest.TestCase):
    def test_init(self):
        osc2event = OscToEvent()
        self.assertIsNone(osc2event.osc_input)
        self.assertIsNone(osc2event.event_manager)
        self.assertIsNone(osc2event.mapping)

    def test_setup(self):
        osc2event = OscToEvent()
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        # assert result
        self.assertEqual(osc2event.osc_input, osc_input)
        self.assertEqual(osc2event.event_manager, event_manager)
        self.assertEqual(osc2event.mapping, {})
        self.assertTrue(osc2event._onOscMessage in osc_input.messageEvent)

    def test_destroy(self):
        osc2event = OscToEvent()
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        self.assertEqual(osc2event.mapping, {})
        osc2event.destroy()
        self.assertIsNone(osc2event.mapping)
        self.assertFalse(osc2event._onOscMessage in osc_input.messageEvent)
        self.assertIsNone(osc2event.event_manager)
        self.assertIsNone(osc2event.osc_input)

    def test_ignores_non_string_options(self):
        osc2event = OscToEvent({'verbose': True, 'foo': 3})
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        # before
        self.assertEqual(event_manager.get('True')._fireCount, 0)
        self.assertEqual(event_manager.get('true')._fireCount, 0)
        self.assertEqual(event_manager.get(3)._fireCount, 0)
        self.assertEqual(event_manager.get('3')._fireCount, 0)
        # tigger
        osc_input.messageEvent('verbose')
        osc_input.messageEvent('foo')
        # after
        self.assertEqual(event_manager.get('True')._fireCount, 0)
        self.assertEqual(event_manager.get('true')._fireCount, 0)
        self.assertEqual(event_manager.get(3)._fireCount, 0)
        self.assertEqual(event_manager.get('3')._fireCount, 0)

    def test_osc_messages_trigger_specified_events(self):
        osc2event = OscToEvent({'/start': 'startE', '/stop': 'stopE'})
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        # before
        self.assertEqual(event_manager.get('startE')._fireCount, 0)
        self.assertEqual(event_manager.get('stopE')._fireCount, 0)
        # trigger start
        osc_input.messageEvent('/start')
        self.assertEqual(event_manager.get('startE')._fireCount, 1)
        self.assertEqual(event_manager.get('stopE')._fireCount, 0)
        osc_input.messageEvent('/stop')
        self.assertEqual(event_manager.get('startE')._fireCount, 1)
        self.assertEqual(event_manager.get('stopE')._fireCount, 1)
        osc_input.messageEvent('/start')
        self.assertEqual(event_manager.get('startE')._fireCount, 2)
        self.assertEqual(event_manager.get('stopE')._fireCount, 1)

    def test_auto_false(self):
        # setup
        osc2event = OscToEvent() # default: {'auto': False}
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        # before
        self.assertEqual(event_manager.get('/osc/message')._fireCount, 0)
        # trigger
        osc_input.messageEvent('/osc/message')
        # before
        self.assertEqual(event_manager.get('/osc/message')._fireCount, 0)

    def test_auto_true(self):
        # setup
        osc2event = OscToEvent({'auto': True})
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        # before
        self.assertEqual(event_manager.get('/osc/message')._fireCount, 0)
        # trigger
        osc_input.messageEvent('/osc/message')
        # before
        self.assertEqual(event_manager.get('/osc/message')._fireCount, 1)

    def test_auto_true_with_explicit_overwrite(self):
        # setup
        osc2event = OscToEvent({'auto': True, '/explicit': 'doesthis'})
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        # before
        self.assertEqual(event_manager.get('/explicit')._fireCount, 0)
        self.assertEqual(event_manager.get('doesthis')._fireCount, 0)
        # trigger
        osc_input.messageEvent('/explicit')
        # before
        self.assertEqual(event_manager.get('/explicit')._fireCount, 0)
        self.assertEqual(event_manager.get('doesthis')._fireCount, 1)
