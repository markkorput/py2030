#!/usr/bin/env python
import unittest, time

from py2030.components.sine import Sine
from py2030.event_manager import EventManager

class TestSineMethods(unittest.TestCase):
    def test_init(self):
        sine = Sine()
        self.assertEqual(sine.amplitude, 1.0)
        self.assertEqual(sine.frequency, 1.0)

        sine = Sine({'amplitude': 2.0, 'frequency': 3.0})
        self.assertEqual(sine.amplitude, 2.0)
        self.assertEqual(sine.frequency, 3.0)

    def test_setup(self):
        sine = Sine()
        em = EventManager()
        sine.setup(em)
        self.assertEqual(sine.event_manager, em)

    def test_update(self):
        sine = Sine({'output_events': {'value': 'newSineValue'}})
        em = EventManager()
        self.assertIsNone(em.get('newSineValue', create=False))
        sine.setup(em)
        self.assertIsNotNone(em.get('newSineValue', create=False))
        sine.update()
        self.assertEqual(em.get('newSineValue')._fireCount, 1)
        sine.update()
        self.assertEqual(em.get('newSineValue')._fireCount, 2)
        sine.update()
        sine.update()
        self.assertEqual(em.get('newSineValue')._fireCount, 4)

    def test_update_timed(self):
        sine = Sine()
        sine.setup()
        self._test_update_values = []
        sine.valueEvent += self._test_update_timed_callback
        sine.update(0.0) # start of sine wave
        self.assertLess(self._test_update_values[-1], 0.001)
        sine.update(0.0) # still at start of sine wave
        self.assertLess(self._test_update_values[-1], 0.001)
        sine.update(1.0) # move forward one full sine wave (back to start of next phase)
        self.assertLess(self._test_update_values[-1], 0.001)
        sine.update(0.5) # move forward 1/2 sine wave (back down to zero)
        self.assertLess(self._test_update_values[-1], 0.001)
        sine.update(0.25) # move forward 1/4 phase (deepest point)
        self.assertLess(self._test_update_values[-1], -0.99)
        sine.update(0.5) # move forward 1/4 phase (highest point)
        self.assertGreater(self._test_update_values[-1], 0.99)

        sine = Sine({'frequency': 2.0, 'amplitude': 100})
        sine.setup()
        self._test_update_values = []
        sine.valueEvent += self._test_update_timed_callback
        sine.update(0.125) # high point of first phase
        self.assertGreater(self._test_update_values[-1], 99.99)

    def _test_update_timed_callback(self, value):
        self._test_update_values.append(value)

    def test_sleep(self):
        # without sleep
        sine = Sine()
        sine.setup()
        t1 = time.time()
        sine.update()
        t2 = time.time()
        self.assertLess(t2-t1, 0.01)

        # with sleep
        sine = Sine({'sleep': 0.6})
        sine.setup()
        t1 = time.time()
        sine.update()
        t2 = time.time()
        self.assertGreater(t2-t1, 0.6)

    def test_base_option(self):
        # without base
        sine = Sine()
        sine.setup()
        self.assertEqual(sine.base, 0.0)
        sine.update(0.0)
        self.assertLess(sine._lastValue, 0.01)
        sine.update(0.25)
        self.assertGreater(sine._lastValue, 0.99)

        # with base
        sine = Sine({'base': 5.0})
        sine.setup()
        self.assertEqual(sine.base, 5.0)
        sine.update(0.0)
        self.assertGreater(sine._lastValue, 4.99)
        self.assertLess(sine._lastValue, 5.01)
        sine.update(0.25)
        self.assertGreater(sine._lastValue, 5.99)
