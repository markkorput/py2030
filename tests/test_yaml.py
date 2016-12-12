#!/usr/bin/env python
import unittest
import socket, yaml
from py2030.yaml import Yaml

class TestYaml(unittest.TestCase):
    def setUp(self):
        self.default_data = {
            'py2030': {
                'profiles': {
                    socket.gethostname().replace('.', '_'): {
                        'start_event': 'start'
                    }
                }
            }
        }

    def test_init(self):
        self.assertEqual(Yaml().data, self.default_data)

    def test_text(self):
        self.assertEqual(Yaml().text(), yaml.dump(self.default_data, default_flow_style=False))
