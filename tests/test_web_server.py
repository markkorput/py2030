# #!/usr/bin/env python
# import unittest, os, urllib
# from py2030.components.web_server import WebServer
# from py2030.event_manager import EventManager
#
# class TestWebServer(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.event_manager = EventManager()
#         cls.webserver = WebServer({
#             'port': 2033,
#             'serve': 'tests/data',
#             'output_events': {'/api/start': 'startEvent'},
#             'responses': {'/system/stop': 'Shutting down...'}})
#         cls.webserver.setup(cls.event_manager)
#
#     @classmethod
#     def tearDownClass(cls):
#         cls.webserver.destroy()
#
#     def test_init(self):
#         webserver = WebServer()
#         self.assertFalse(webserver.isAlive())
#         self.assertIsNone(webserver.event_manager)
#         self.assertTrue(webserver.daemon)
#
#     def test_setup(self):
#         self.assertTrue(self.webserver.isAlive())
#         self.assertEqual(self.webserver.event_manager, self.event_manager)
#
#     def test_setup_without_event_manager(self):
#         self.webserver = WebServer()
#         self.webserver.setup()
#         self.assertTrue(self.webserver.isAlive())
#         self.assertIsNone(self.webserver.event_manager)
#         self.webserver.destroy()
#
#     def test_destroy(self):
#         webserver = WebServer()
#         em = EventManager()
#         webserver.setup(em)
#         self.assertTrue(webserver.isAlive())
#         self.assertEqual(webserver.event_manager, em)
#         webserver.destroy()
#         self.assertFalse(webserver.isAlive())
#         self.assertIsNone(webserver.event_manager)
#
#     def test_port_default_value(self):
#         self.assertEqual(WebServer().port(), 2031)
#
#     def test_port_config_option(self):
#         self.assertEqual(WebServer({'port': 1234}).port(), 1234)
#
#     def test_serve_options(self):
#         response = urllib.urlopen('http://localhost:'+str(self.webserver.port())+'/config.yml').read()
#         with open(os.path.join(os.path.dirname(__file__), 'data', 'config.yml')) as f:
#             self.assertEqual(response, f.read())
#
#     def test_output_event(self):
#         self.assertEqual(self.event_manager.get('event1')._fireCount, 0)
#         urllib.urlopen('http://localhost:'+str(self.webserver.port())+'/api/start').read()
#         self.assertEqual(self.event_manager.get('startEvent')._fireCount, 1)
#
#     def test_responses(self):
#         response = urllib.urlopen('http://localhost:'+str(self.webserver.port())+'/system/stop')
#         self.assertEqual(response.getcode(), 200)
#         self.assertEqual(response.read(), 'Shutting down...')
