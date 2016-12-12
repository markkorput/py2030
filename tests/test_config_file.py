#!/usr/bin/env python
import unittest
from py2030.utils.config_file import ConfigFile

class TestOscInput(unittest.TestCase):
    def test_init(self):
        cfile = ConfigFile('config/config.example.yml')
        self.assertEqual(cfile.path, 'config/config.example.yml')
        self.assertIsNone(cfile.data)
        self.assertIsNotNone(cfile.dataLoadedEvent)
        self.assertIsNotNone(cfile.dataChangeEvent)
