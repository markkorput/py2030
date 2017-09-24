#!/usr/bin/env python
import time
from evento import Event
from py2030.components.dmx_output import DmxOutput

class LightCeremonyDmxOutput(DmxOutput):
    config_name = 'lightCeremonyDmxOutputs'

    def setup(self, event_manager=None):
        DmxOutput.setup(self, event_manager)
