#!/usr/bin/env python
import time
import logging
from evento import Event
from py2030.base_component import BaseComponent

try:
    import pysimpledmx
except ImportError:
    pysimpledmx = None

class LightCeremonyController(BaseComponent):
    config_name = 'lightCeremonyAnimReaders'
