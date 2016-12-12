#!/usr/bin/env python
import unittest
from time import sleep
from py2030.event_manager import EventManager
from py2030.components.delay_events import DelayEvents

class TestEventToEvent(unittest.TestCase):
    def test_init(self):
        delay_events = DelayEvents()
        self.assertIsNone(delay_events.event_manager)

    def test_setup(self):
        delay_events = DelayEvents({'example': {'source': 'loop', 'delay': 60, 'target': 'loop'}})
        event_manager = EventManager()
        self.assertEqual(event_manager.getEvent('loop').getSubscriberCount(), 0)
        delay_events.setup(event_manager)
        self.assertEqual(delay_events.event_manager, event_manager)
        self.assertEqual(event_manager.getEvent('loop').getSubscriberCount(), 1)

    def test_destroy(self):
        delay_events = DelayEvents({'example': {'source': 'loop', 'delay': 60, 'target': 'loop'}})
        event_manager = EventManager()
        delay_events.setup(event_manager)
        self.assertEqual(delay_events.event_manager, event_manager)
        self.assertEqual(event_manager.getEvent('loop').getSubscriberCount(), 1)
        delay_events.destroy()
        self.assertIsNone(delay_events.event_manager)
        self.assertEqual(event_manager.getEvent('loop').getSubscriberCount(), 0)

    def test_update_without_trigger(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 60, 'target': 'BB'}})
        event_manager = EventManager()
        delay_events.setup(event_manager)
        delay_events.update(62) # 'pretend' 62 seconds have passed
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 0)

    def test_update_with_trigger(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 50, 'target': 'BB'}})
        event_manager = EventManager()
        delay_events.setup(event_manager)
        # trigger source event, in order to trigger the delayed call to the target event
        event_manager.getEvent('AA').fire()
        delay_events.update(50) # let 10 seconds 'pass'
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 1)

    def test_update_progress(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 30, 'target': 'BB'}})
        event_manager = EventManager()
        delay_events.setup(event_manager)
        self.assertEqual(delay_events._delay_items[0].timer, 0)
        # trigger source event, in order to trigger the delayed call to the target event
        event_manager.getEvent('AA').fire()
        self.assertEqual(delay_events._delay_items[0].timer, 30)
        delay_events.update(10) # let 10 seconds 'pass'
        self.assertEqual(delay_events._delay_items[0].timer, 20)
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 0)
        delay_events.update(10) # let another 10 seconds 'pass'
        self.assertEqual(delay_events._delay_items[0].timer, 10)
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 0)
        delay_events.update(10) # let 10 seconds again, reaching 30 second mark
        self.assertEqual(delay_events._delay_items[0].timer, 0)
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 1)

    def test_update_progress_without_specified_dt(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 30, 'target': 'BB'}})
        event_manager = EventManager()
        delay_events.setup(event_manager)
        self.assertEqual(delay_events._delay_items[0].timer, 0)
        # trigger source event, in order to trigger the delayed call to the target event
        event_manager.getEvent('AA').fire()
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
        event_manager = EventManager()
        delay_events.setup(event_manager)
        # trigger source event, in order to trigger the delayed call to the target event
        event_manager.getEvent('AA').fire()
        delay_events.update(10) # let 10 seconds 'pass'
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 1) # B got fired
        delay_events.update(10) # let's move another 10 seconds into the future
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 1) # B didn't get fired again

    def test_delay_runs_multiple_times(self):
        delay_events = DelayEvents({'example': {'source': 'AA', 'delay': 10, 'target': 'BB'}})
        event_manager = EventManager()
        delay_events.setup(event_manager)
        # trigger source event, in order to trigger the delayed call to the target event
        event_manager.getEvent('AA').fire()
        delay_events.update(10) # let 10 seconds 'pass'
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 1) # B got fired
        delay_events.update(10) # let's move another 10 seconds into the future
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 1) # B didn't get fired again
        event_manager.getEvent('AA').fire()
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 2)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 1) # B didn't get fired again
        delay_events.update(10) # let 10 seconds 'pass'
        self.assertEqual(event_manager.getEvent('AA')._fireCount, 2)
        self.assertEqual(event_manager.getEvent('BB')._fireCount, 2) # B didn't get fired again

    def test_looping_event(self):
        delay_events = DelayEvents({'looper': {'source': 'loop', 'delay': 10, 'target': 'loop'}})
        event_manager = EventManager()
        delay_events.setup(event_manager)
        delay_events.update(10) # let 10 seconds 'pass'
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 0)
        # trigger source event, in order to trigger the delayed call to the target event
        event_manager.getEvent('loop').fire()
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 1)
        delay_events.update(5) # halfway towards the second trigger
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 1)
        delay_events.update(5) # time for the second trigger
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 2)
        delay_events.update(10) # 3rd
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 3)
        delay_events.update(10) # 4th
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 4)
        # etc

    def test_halt(self):
        delay_events = DelayEvents({'example': {'source': 'loop', 'delay': 10, 'target': 'loop', 'halt': 'halter'}})
        event_manager = EventManager()
        halterE = event_manager.getEvent('halter')
        self.assertEqual(halterE.getSubscriberCount(), 0)
        delay_events.setup(event_manager)
        self.assertEqual(delay_events._delay_items[0].haltEvent, halterE)
        self.assertEqual(halterE.getSubscriberCount(), 1)
        self.assertEqual(delay_events._delay_items[0].active, True)
        # start
        event_manager.getEvent('loop').fire()
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 1)
        # progress
        delay_events.update(10)
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 2)
        # progress
        delay_events.update(10)
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 3)
        # halt
        halterE()
        self.assertEqual(delay_events._delay_items[0].active, False)
        # progress, halted
        delay_events.update(10)
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 3)
        # progress, halted
        delay_events.update(10)
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 3)

    def test_pause(self):
        delay_events = DelayEvents({'example': {'source': 'loop', 'delay': 10, 'target': 'loop', 'pause': 'pauser'}})
        event_manager = EventManager()
        pauserE = event_manager.getEvent('pauser')
        self.assertEqual(pauserE.getSubscriberCount(), 0)
        delay_events.setup(event_manager)
        self.assertEqual(delay_events._delay_items[0].pauseEvent, pauserE)
        self.assertEqual(pauserE.getSubscriberCount(), 1)
        self.assertEqual(delay_events._delay_items[0].active, True)
        # start
        event_manager.getEvent('loop').fire()
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 1)
        # progress
        delay_events.update(10)
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 2)
        delay_events.update(6)
        # pause
        pauserE()
        self.assertEqual(delay_events._delay_items[0].active, False)
        # progress, halted
        delay_events.update(10)
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 2)
        # resume
        pauserE()
        self.assertEqual(delay_events._delay_items[0].active, True)
        # progress, resumed
        delay_events.update(4)
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 3)

    def test_start_after_halt(self):
        delay_events = DelayEvents({'example': {'source': 'loop', 'delay': 10, 'target': 'loop', 'halt': 'halter'}})
        event_manager = EventManager()
        delay_events.setup(event_manager)
        # start
        event_manager.getEvent('loop').fire()
        # reach first loop (2nd loop fire)
        delay_events.update(10)
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 2)
        # stop
        event_manager.getEvent('halter').fire()
        delay_events.update(10)
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 2)
        # start again
        event_manager.getEvent('loop').fire()
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 3)
        # finish another cycle since starting again
        delay_events.update(10)
        self.assertEqual(event_manager.getEvent('loop')._fireCount, 4)
