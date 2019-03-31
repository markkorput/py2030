from evento import Event
from py2030.base_component import BaseComponent

import os

class Kills(BaseComponent):
    config_name = 'kills'

    def __init__(self, options = {}):
        super().__init__(options)
        self.signum = self.opt('signum', None)


    def setup(self, event_manager=None):
        super().setup(event_manager)
        self.killEvent = self.getOutputEvent('kill')
        self.successEvent = self.getOutputEvent('success')
        self.failureEvent = self.getOutputEvent('failure')
        self.getInputEvent('id').subscribe(self.onId)

    def onId(self, id):
        cmd = 'kill '+str(id) if self.signum == None else 'kill -n '+str(self.signum)+' '+str(id)

        self.logger.debug('killing process ID: '+str(id)+' with command: '+cmd)
        res = os.system('kill '+str(id))
        self.killEvent()
        if res == 0:
            self.successEvent()
        else:
            self.failureEvent()
