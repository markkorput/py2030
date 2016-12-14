#!/usr/bin/env python
import unittest, logging
from glob import glob

from py2030.components.ssh_remote import SshRemote
from py2030.event_manager import EventManager

class TestSshRemote(unittest.TestCase):
    def setUp(self):
        logging.basicConfig()

    def test___init__(self):
        sr = SshRemote({'hostname': 'host.name', 'password': 'abc123'})
        self.assertEqual(sr.hostname, 'host.name')
        self.assertIsNone(sr.ip)
        self.assertIsNone(sr.username)
        self.assertEqual(sr.password, 'abc123')
        self.assertFalse(sr.connected)
        self.assertIsNone(sr.client)
        self.assertEqual(sr._operations, {})
        self.assertIsNone(sr.event_manager)

    def test_setup_takes_event_manager(self):
        sr = SshRemote()
        em = EventManager()
        sr.setup(em)
        self.assertEqual(sr.event_manager, em)

    def test_setup_fails_to_connect_without_password(self):
        sr = SshRemote({'hostname': 'localhost', 'username': 'pi'})
        sr.setup()
        self.assertEqual(sr.ip, '127.0.0.1')
        self.assertIsNotNone(sr.client)
        self.assertFalse(sr.connected)

    def test_setup_creates_file_sync_operations_queue(self):
        files = {
            './LICENSE': 'remote/target/folder/',
            './README.md': 'remote/target/path/README.md'}

        sr = SshRemote({'files': files})
        sr.setup()
        self.assertEqual(sr._operations, files)

    def test_setup_creates_empty_file_sync_operations_queue_by_default(self):
        sr = SshRemote()
        sr.setup()
        self.assertEqual(sr._operations, {})

    def test_setup_expands_glob_patterns_into_multiple_file_operations(self):
        files = {
            './LICENSE': 'remote/target/folder/',
            './README.md': 'remote/target/path/README.md'}

        sr = SshRemote({'files': {'./tests/test_*.py': 'remote/folder/'}})
        sr.setup()
        a = sr._operations.keys()
        a.sort()
        b = glob('./tests/test_*.py')
        b.sort()
        self.assertEqual(a,b)

    def test_destroy(self):
        sr = SshRemote({'hostname': 'localhost', 'username': 'pi', 'password': 'raspberry'})
        sr.setup(EventManager())
        sr.destroy()
        self.assertIsNone(sr.ip)
        self.assertFalse(sr.connected)
        self.assertIsNone(sr.client)
        self.assertIsNone(sr.event_manager)

    # def test_update_process_operations_one_at_a_time(self):
    def test_update_fails_to_process_operations_without_connection(self):
        files = {
            './LICENSE': 'remote/target/folder/',
            './README.md': 'remote/target/path/README.md'}

        sr = SshRemote({'verbose': True, 'files': files})
        sr.setup()
        self.assertEqual(len(sr._operations), 2)
        self.assertFalse(sr.isDone())
        sr.update()
        self.assertEqual(len(sr._operations), 2)

    # requires scp server
    # def test_update_processes_operations_one_by_one(self):
    #     files = {
    #         './LICENSE': '~/',
    #         './README.md': '~/'}
    #
    #     sr = SshRemote({'verbose': True, 'files': files, 'username': 'pi', 'password': 'raspberry', 'hostname': 'localhost'})
    #     sr.setup()
    #     self.assertEqual(len(sr._operations), 2)
    #     self.assertFalse(sr.isDone())
    #     sr.update()
    #     self.assertEqual(len(sr._operations), 1)
    #     self.assertFalse(sr.isDone())
    #     sr.update()
    #     self.assertEqual(len(sr._operations), 0)
    #     self.assertTrue(sr.isDone())

    # requires scp server
    # def test_process(self):
    #     sr = SshRemote({'verbose': True, 'username': 'pi', 'password': 'raspberry', 'hostname': 'localhost', 'files': {'./tests/test_*.py': 'Public'}})
    #     sr.setup()
    #     while not sr.isDone():
    #         sr.update()

    # def test_done_event(self):
    #     pass
