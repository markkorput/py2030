#!/usr/bin/env python
import unittest
from time import sleep
from pyhoh.dynamic_events import DynamicEvents
from pyhoh.components.delay_events import DelayEvents

class TestEventToEvent(unittest.TestCase):
    def test_init(self):
        delay_events = DelayEvents()
        self.assertIsNone(delay_events.dynamic_events)

    def test_setup(self):
        delay_events = DelayEvents({'example': {'source': 'loop', 'delay': 60, 'target': 'loop'}})
        dynamic_events = DynamicEvents()
        self.assertEqual(dynamic_events.getEvent('loop').getSubscriberCount(), 0)
        delay_events.setup(dynamic_events)
        self.assertEqual(delay_events.dynamic_events, dynamic_events)
        self.assertEqual(dynamic_events.getEvent('loop').getSubscriberCount(), 1)

    def test_destroy(self):
        delay_events = DelayEvents({'example': {'source': 'loop', 'delay': 60, 'target': 'loop'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        self.assertEqual(delay_events.dynamic_events, dynamic_events)
        self.assertEqual(dynamic_events.getEvent('loop').getSubscriberCount(), 1)
        delay_events.destroy()
        self.assertIsNone(delay_events.dynamic_events)
        self.assertEqual(dynamic_events.getEvent('loop').getSubscriberCount(), 0)

    def test_update_without_trigger(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 60, 'target': 'BB'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        delay_events.update(62) # 'pretend' 62 seconds have passed
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 0)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 0)

    def test_update_with_trigger(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 50, 'target': 'BB'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        # trigger source event, in order to trigger the delayed call to the target event
        dynamic_events.getEvent('AA').fire()
        delay_events.update(50) # let 10 seconds 'pass'
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 1)

    def test_update_progress(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 30, 'target': 'BB'}})
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

    def test_update_progress_without_specified_dt(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 30, 'target': 'BB'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        self.assertEqual(delay_events._delay_items[0].timer, 0)
        # trigger source event, in order to trigger the delayed call to the target event
        dynamic_events.getEvent('AA').fire()
        self.assertEqual(delay_events._delay_items[0].timer, 30)
        delay_events.update()
        self.assertLess(delay_events._delay_items[0].timer, 30)
        self.assertGreater(delay_events._delay_items[0].timer, 29.75)
        sleep(0.25)
        delay_events.update()
        self.assertLess(delay_events._delay_items[0].timer, 29.75)
        self.assertGreater(delay_events._delay_items[0].timer, 29.5)

    def test_expired_delay(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 10, 'target': 'BB'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        # trigger source event, in order to trigger the delayed call to the target event
        dynamic_events.getEvent('AA').fire()
        delay_events.update(10) # let 10 seconds 'pass'
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 1) # B got fired
        delay_events.update(10) # let's move another 10 seconds into the future
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 1) # B didn't get fired again

    def test_delay_runs_multiple_times(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 10, 'target': 'BB'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        # trigger source event, in order to trigger the delayed call to the target event
        dynamic_events.getEvent('AA').fire()
        delay_events.update(10) # let 10 seconds 'pass'
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 1) # B got fired
        delay_events.update(10) # let's move another 10 seconds into the future
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 1)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 1) # B didn't get fired again
        dynamic_events.getEvent('AA').fire()
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 2)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 1) # B didn't get fired again
        delay_events.update(10) # let 10 seconds 'pass'
        self.assertEqual(dynamic_events.getEvent('AA')._fireCount, 2)
        self.assertEqual(dynamic_events.getEvent('BB')._fireCount, 2) # B didn't get fired again

    def test_looping_event(self):
        delay_events = DelayEvents({'looper': {'source': 'loop', 'delay': 10, 'target': 'loop'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        delay_events.update(10) # let 10 seconds 'pass'
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 0)
        # trigger source event, in order to trigger the delayed call to the target event
        dynamic_events.getEvent('loop').fire()
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 1)
        delay_events.update(5) # halfway towards the second trigger
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 1)
        delay_events.update(5) # time for the second trigger
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 2)
        delay_events.update(10) # 3rd
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 3)
        delay_events.update(10) # 4th
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 4)
        # etc

    def test_halt(self):
        delay_events = DelayEvents({'example': {'source': 'loop', 'delay': 10, 'target': 'loop', 'halt': 'halter'}})
        dynamic_events = DynamicEvents()
        halterE = dynamic_events.getEvent('halter')
        self.assertEqual(halterE.getSubscriberCount(), 0)
        delay_events.setup(dynamic_events)
        self.assertEqual(delay_events._delay_items[0].haltEvent, halterE)
        self.assertEqual(halterE.getSubscriberCount(), 1)
        self.assertEqual(delay_events._delay_items[0].active, True)
        # start
        dynamic_events.getEvent('loop').fire()
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 1)
        # progress
        delay_events.update(10)
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 2)
        # progress
        delay_events.update(10)
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 3)
        # halt
        halterE()
        self.assertEqual(delay_events._delay_items[0].active, False)
        # progress, halted
        delay_events.update(10)
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 3)
        # progress, halted
        delay_events.update(10)
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 3)

    def test_pause(self):
        delay_events = DelayEvents({'example': {'source': 'loop', 'delay': 10, 'target': 'loop', 'pause': 'pauser'}})
        dynamic_events = DynamicEvents()
        pauserE = dynamic_events.getEvent('pauser')
        self.assertEqual(pauserE.getSubscriberCount(), 0)
        delay_events.setup(dynamic_events)
        self.assertEqual(delay_events._delay_items[0].pauseEvent, pauserE)
        self.assertEqual(pauserE.getSubscriberCount(), 1)
        self.assertEqual(delay_events._delay_items[0].active, True)
        # start
        dynamic_events.getEvent('loop').fire()
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 1)
        # progress
        delay_events.update(10)
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 2)
        delay_events.update(6)
        # pause
        pauserE()
        self.assertEqual(delay_events._delay_items[0].active, False)
        # progress, halted
        delay_events.update(10)
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 2)
        # resume
        pauserE()
        self.assertEqual(delay_events._delay_items[0].active, True)
        # progress, resumed
        delay_events.update(4)
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 3)

    def test_start_after_halt(self):
        delay_events = DelayEvents({'example': {'source': 'loop', 'delay': 10, 'target': 'loop', 'halt': 'halter'}})
        dynamic_events = DynamicEvents()
        delay_events.setup(dynamic_events)
        # start
        dynamic_events.getEvent('loop').fire()
        # reach first loop (2nd loop fire)
        delay_events.update(10)
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 2)
        # stop
        dynamic_events.getEvent('halter').fire()
        delay_events.update(10)
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 2)
        # start again
        dynamic_events.getEvent('loop').fire()
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 3)
        # finish another cycle since starting again
        delay_events.update(10)
        self.assertEqual(dynamic_events.getEvent('loop')._fireCount, 4)
