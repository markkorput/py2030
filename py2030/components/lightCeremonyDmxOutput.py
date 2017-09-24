#!/usr/bin/env python
import time
from evento import Event
from py2030.components.dmx_output import DmxOutput

class LightCeremonyDmxOutput(DmxOutput):
    config_name = 'lightCeremonyDmxOutputs'

    def setup(self, event_manager=None):
        DmxOutput.setup(self, event_manager)

        self.winchStartChannel = int(self.options['winchStartChannel'])-1 if 'winchStartChannel' in self.options else 0

        self.CH_WINCH_POS_ROUGH = self.winchStartChannel + 0
        self.CH_WINCH_POS_FINE = self.winchStartChannel + 1
        self.CH_WINCH_POS_VELOCITY = self.winchStartChannel + 2
        self.CH_WINCH_POS_RESET_UP = self.winchStartChannel + 5

        if 'winchVelocityEvent' in self.options:
            event = event_manager.get(self.options['winchVelocityEvent'])
            event += self._onWinchVelocity
            self.logger.debug('registed listener for winch velocity event: '+self.options['winchVelocityEvent'])

    def _onWinchVelocity(self, vel):
        if vel > 0:
            # self.logger.debug('up, vel: '+str(vel))
            self._winchToPos(1.0, vel) # up
        else:
            # self.logger.debug('down, vel: '+str(-vel))
            self._winchToPos(0.0, -vel) # down

    def _winchToPos(self, pos, velocity):
        self._setChannel(self.CH_WINCH_POS_ROUGH, pos)
        self._setChannel(self.CH_WINCH_POS_VELOCITY, velocity)
