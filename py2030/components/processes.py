from evento import Event
from py2030.base_component import BaseComponent

import subprocess, re

class Processes(BaseComponent):
    config_name = 'processes'

    def __init__(self, options = {}):
        super().__init__(options)

    def setup(self, event_manager=None):
        super().setup(event_manager)

        self.idEvent = self.getOutputEvent('id')
        self.match = self.opt('match', None)
        self.getInputEvent('emitIdOn').subscribe(self.onEmitId)

    def findIdByIdentifier(self, id):
        cmd = 'ps ax | grep '+id
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output = p.stdout.readlines()

        for line in output:
            if 'grep' in str(line):
                continue

            m = re.search('\d+', str(line).replace('\'b', ''))
            if m:
                return int(m.group(0))

        return None

    def onEmitId(self):

        if self.match == None:
            self.logger.info('\'match\' property not set, no way to find process ID')
            return

        self.logger.debug('looking for process with identifier: '+self.match)
        id = self.findIdByIdentifier(self.match)

        if not id == None:
            self.logger.debug('Process ID found: {0}'.format(id))
            self.idEvent(id)
