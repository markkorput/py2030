#!/usr/bin/env python
import unittest
from py2030.components.web_server import WebServer
from py2030.event_manager import EventManager

class TestWebServer(unittest.TestCase):
    def test_init(self):
        webserver = WebServer()
        self.assertFalse(webserver.isAlive())
        self.assertIsNone(webserver.event_manager)
        self.assertTrue(webserver.daemon)

    def test_setup(self):
        webserver = WebServer()
        webserver.setup()
        self.assertTrue(webserver.isAlive())
        self.assertIsNone(webserver.event_manager)

    def test_setup_with_event_manager(self):
        webserver = WebServer()
        em = EventManager()
        webserver.setup(em)
        self.assertTrue(webserver.isAlive())
        self.assertEqual(webserver.event_manager, em)

    def test_destroy(self):
        webserver = WebServer()
        em = EventManager()
        webserver.setup(em)
        self.assertTrue(webserver.isAlive())
        self.assertEqual(webserver.event_manager, em)
        webserver.destroy()
        self.assertFalse(webserver.isAlive())
        self.assertIsNone(webserver.event_manager)
