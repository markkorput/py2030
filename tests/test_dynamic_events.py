#!/usr/bin/env python
import unittest
import helper
from pyhoh.dynamic_events import DynamicEvents

class TestDynamicEvents(unittest.TestCase):
    def test_init(self):
        dynevents = DynamicEvents()
        self.assertIsNotNone(dynevents.eventAddedEvent)
