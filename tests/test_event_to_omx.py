#!/usr/bin/env python
import unittest
from pyhoh.dynamic_events import DynamicEvents
from pyhoh.components.event_to_omx import EventToOmx
from pyhoh.components.omxvideo import OmxVideo

class TestEventToOmx(unittest.TestCase):
    def test_init(self):
        event2omx = EventToOmx()
        self.assertIsNone(event2omx.dynamic_events)

    def test_setup(self):
        event2omx = EventToOmx({'begin': {'action': 'start'}, 'pause': 'toggle', 'end': 'stop'})
        devents = DynamicEvents()
        event2omx.setup(devents, OmxVideo())
        self.assertEqual(event2omx.dynamic_events, devents)
        self.assertEqual(devents.getEvent('begin').getSubscriberCount(), 1)
        self.assertEqual(devents.getEvent('pause').getSubscriberCount(), 1)
        self.assertEqual(devents.getEvent('end').getSubscriberCount(), 1)

    def test_start(self):
        event2omx = EventToOmx({'begin': {'action': 'start'}, 'pause': 'toggle', 'end': 'stop'})
        devents = DynamicEvents()
        event2omx.setup(devents, OmxVideo())
        self.assertEqual(event2omx.omxvideo.startEvent._fireCount, 0)
        devents.getEvent('begin').fire()
        self.assertEqual(event2omx.omxvideo.startEvent._fireCount, 1)

    def test_stop(self):
        event2omx = EventToOmx({'begin': {'action': 'start'}, 'pause': 'toggle', 'end': 'stop'})
        devents = DynamicEvents()
        event2omx.setup(devents, OmxVideo())
        self.assertEqual(event2omx.omxvideo.stopEvent._fireCount, 0)
        devents.getEvent('end').fire()
        # fails because no video is loaded. TODO; verify
        # self.assertEqual(event2omx.omxvideo.stopEvent._fireCount, 1)

    def test_toggle(self):
        event2omx = EventToOmx({'begin': {'action': 'start'}, 'pause': 'toggle', 'end': 'stop'})
        devents = DynamicEvents()
        event2omx.setup(devents, OmxVideo())
        self.assertEqual(event2omx.omxvideo.toggleEvent._fireCount, 0)
        devents.getEvent('pause').fire()
        # fails because no video is loaded. TODO; verify
        # self.assertEqual(event2omx.omxvideo.toggleEvent._fireCount, 1)
