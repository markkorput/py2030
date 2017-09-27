#!/usr/bin/env python
import time
import logging
from evento import Event
from py2030.base_component import BaseComponent

class AudioInput(BaseComponent):
    config_name = 'audio_inputs'

    def setup(self, event_manager):
        BaseComponent.setup(self, event_manager)

    
