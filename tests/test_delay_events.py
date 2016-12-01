#!/usr/bin/env python
import unittest
from pyhoh.dynamic_events import DynamicEvents
from pyhoh.components.delay_events import DelayEvents

class TestEventToEvent(unittest.TestCase):
    def test_init(self):
        delay_events = DelayEvents()
        self.assertIsNone(delay_events.dynamic_events)

    def test_setup(self):
        delay_events = DelayEvents({'looper': {'source': 'loop', 'delay': 60, 'target': 'loop'}})
        dynamic_events = DynamicEvents()
        self.assertEqual(dynamic_events.getEvent('loop').getSubscriberCount(), 0)
        delay_events.setup(dynamic_events)
        self.assertEqual(delay_events.dynamic_events, dynamic_events)
        self.assertEqual(dynamic_events.getEvent('loop').getSubscriberCount(), 1)

    def test_destroy(self):
        delay_events = DelayEvents({'looper': {'source': 'loop', 'delay': 60, 'target': 'loop'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        self.assertEqual(delay_events.dynamic_events, dynamic_events)
        self.assertEqual(dynamic_events.getEvent('loop').getSubscriberCount(), 1)
        delay_events.destroy()
        self.assertIsNone(delay_events.dynamic_events)
        self.assertEqual(dynamic_events.getEvent('loop').getSubscriberCount(), 0)

    def test_update_without_trigger(self):
        delay_events = DelayEvents({'looper': {'source': 'AA', 'delay': 60, 'target': 'BB'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        delay_events.update(62) # 'pretend' 62 seconds have passed
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 0)

    def test_update_with_trigger(self):
        delay_events = DelayEvents({'looper': {'source': 'AA', 'delay': 50, 'target': 'BB'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        # trigger source event, in order to trigger the delayed call to the target event
        dynamic_events.getEvent('AA').fire()
        delay_events.update(50) # let 10 seconds 'pass'
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 1)

    def test_update_progress(self):
        delay_events = DelayEvents({'looper': {'source': 'AA', 'delay': 30, 'target': 'BB'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        self.assertEqual(delay_events._delay_items[0].timer, 0)
        # trigger source event, in order to trigger the delayed call to the target event
        dynamic_events.getEvent('AA').fire()
        self.assertEqual(delay_events._delay_items[0].timer, 30)
        delay_events.update(10) # let 10 seconds 'pass'
        self.assertEqual(delay_events._delay_items[0].timer, 20)
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 0)
        delay_events.update(10) # let another 10 seconds 'pass'
        self.assertEqual(delay_events._delay_items[0].timer, 10)
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 0)
        delay_events.update(10) # let 10 seconds again, reaching 30 second mark
        self.assertEqual(delay_events._delay_items[0].timer, 0)
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 1)
