#!/usr/bin/env python
import unittest

from py2030.components.ssh_remote import SshRemote

class TestSshRemote(unittest.TestCase):
    def test___init__(self):
        sr = SshRemote({'hostname': 'host.name', 'password': 'abc123'})
        self.assertEqual(sr.hostname, 'host.name')
        self.assertIsNone(sr.ip)
        self.assertIsNone(sr.username)
        self.assertEqual(sr.password, 'abc123')
        self.assertFalse(sr.connected)
        self.assertIsNone(sr.client)

    # def test_setup(self):
    #     sr = SshRemote({'hostname': 'localhost', 'username': 'pi', 'password': 'raspberry'})
    #     sr.setup()
    #     self.assertEqual(sr.ip, '127.0.0.1')
    #     self.assertIsNotNone(sr.client)
    #     self.assertTrue(sr.connected)
    #
    # def test_destroy(self):
    #     sr = SshRemote({'hostname': 'localhost', 'username': 'pi', 'password': 'raspberry'})
    #     sr.setup()
    #     sr.connect()
    #     sr.destroy()
    #     self.assertIsNone(sr.ip)
    #     self.assertFalse(sr.connected)
    #     self.assertIsNone(sr.client)
