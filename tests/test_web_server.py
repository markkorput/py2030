#!/usr/bin/env python
import unittest, httplib, os
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
        webserver.destroy()

    def test_setup_with_event_manager(self):
        webserver = WebServer()
        em = EventManager()
        webserver.setup(em)
        self.assertTrue(webserver.isAlive())
        self.assertEqual(webserver.event_manager, em)
        webserver.destroy()

    def test_destroy(self):
        webserver = WebServer()
        em = EventManager()
        webserver.setup(em)
        self.assertTrue(webserver.isAlive())
        self.assertEqual(webserver.event_manager, em)
        webserver.destroy()
        self.assertFalse(webserver.isAlive())
        self.assertIsNone(webserver.event_manager)

    def test_port_default_value(self):
        self.assertEqual(WebServer().port(), 2031)

    def test_port_config_option(self):
        self.assertEqual(WebServer({'port': 1234}).port(), 1234)

    def test_request(self):
        webserver = WebServer()
        webserver.setup()
        connection = httplib.HTTPConnection('127.0.0.1', webserver.port())
        connection.request('GET', '/tests/data/config.yml')
        response = connection.getresponse().read()
        with open(os.path.join(os.path.dirname(__file__), 'data', 'config.yml')) as f:
            self.assertEqual(response, f.read())
        webserver.destroy()

    def test_serve_options(self):
        webserver = WebServer({'serve': 'tests/data'})
        webserver.setup()
        connection = httplib.HTTPConnection('127.0.0.1', webserver.port())
        connection.request('GET', 'config.yml')
        response = connection.getresponse().read()
        with open(os.path.join(os.path.dirname(__file__), 'data', 'config.yml')) as f:
            self.assertEqual(response, f.read())
        webserver.destroy()

    def test_output_event(self):
        webserver = WebServer({'output_events': {'/api/start': 'startEvent'}})
        em = EventManager()
        webserver.setup(em)
        connection = httplib.HTTPConnection('127.0.0.1', webserver.port())
        self.assertEqual(em.get('event1')._fireCount, 0)
        connection.request('GET', '/api/start')
        webserver.destroy()
        self.assertEqual(em.get('startEvent')._fireCount, 1)
