#!/usr/bin/env python
import unittest
from py2030.event_manager import EventManager
from py2030.components.osc_output import OscOutput
from py2030.components.event_to_osc import EventToOsc

class TestEventToOsc(unittest.TestCase):
    def test_init(self):
        event2osc = EventToOsc()
        self.assertIsNone(event2osc.osc_output)
        self.assertIsNone(event2osc.event_manager)

    def test_setup(self):
        event2osc = EventToOsc({'verbose': True, 'start': '/start', 'stop': '/stop'})
        osc_output = OscOutput()
        event_manager = EventManager()
        # before
        self.assertEqual(event_manager.get('start').getSubscriberCount(), 0)
        self.assertEqual(event_manager.get('stop').getSubscriberCount(), 0)
        self.assertEqual(event_manager.get('verbose').getSubscriberCount(), 0)
        # run setup
        event2osc.setup(osc_output, event_manager)
        # assert result
        self.assertEqual(event2osc.osc_output, osc_output)
        self.assertEqual(event2osc.event_manager, event_manager)
        self.assertEqual(event_manager.get('start').getSubscriberCount(), 1)
        self.assertEqual(event_manager.get('stop').getSubscriberCount(), 1)
        self.assertEqual(event_manager.get('verbose').getSubscriberCount(), 0)

    def test_destroy(self):
        event2osc = EventToOsc({'start': '/start', 'stop': '/stop'})
        osc_output = OscOutput()
        event_manager = EventManager()
        event2osc.setup(osc_output, event_manager)
        # before
        self.assertEqual(event2osc.osc_output, osc_output)
        self.assertEqual(event2osc.event_manager, event_manager)
        self.assertEqual(event_manager.get('start').getSubscriberCount(), 1)
        self.assertEqual(event_manager.get('stop').getSubscriberCount(), 1)
        # destroy
        event2osc.destroy()
        # after
        self.assertIsNone(event2osc.osc_output)
        self.assertIsNone(event2osc.event_manager)
        self.assertEqual(event_manager.get('start').getSubscriberCount(), 0)
        self.assertEqual(event_manager.get('stop').getSubscriberCount(), 0)

    def test_osc_messages(self):
        event2osc = EventToOsc({'verbose': True, 'start': '/begin', 'stop': '/halt'})
        osc_output = OscOutput()
        event_manager = EventManager()
        event2osc.setup(osc_output, event_manager)
        osc_output.messageEvent += self._test_osc_messages_listener
        self._test_osc_messages_log = []
        event_manager.get('start').fire()
        self.assertEqual(self._test_osc_messages_log, ['/begin'])
        event_manager.get('start').fire()
        self.assertEqual(self._test_osc_messages_log, ['/begin', '/begin'])
        event_manager.get('stop').fire()
        self.assertEqual(self._test_osc_messages_log, ['/begin', '/begin', '/halt'])
        event_manager.get('verbose').fire()
        self.assertEqual(self._test_osc_messages_log, ['/begin', '/begin', '/halt'])

    def _test_osc_messages_listener(self, msg, osc_output):
        self._test_osc_messages_log.append(msg.address)
