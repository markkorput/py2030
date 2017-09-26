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

        event = self.getInputEvent('winchVelocity')
        event += self._onWinchVelocity
        # self.logger.debug('registed listener for winch velocity event: '+self.options['winchVelocity'])
        event = self.getInputEvent('winchResetUpVelocity')
        event += self._onWinchResetUpVelocity
        event = self.getInputEvent('winchResetDownVelocity')
        event += self._onWinchResetUpVelocity

        self.rotatorStartChannel = int(self.options['rotatorStartChannel'])-1 if 'rotatorStartChannel' in self.options else 0

        self.CH_ROT_POS_ROUGH = self.rotatorStartChannel + 0
        self.CH_ROT_POS_FINE = self.rotatorStartChannel + 1
        self.CH_ROT_POS_VELOCITY = self.rotatorStartChannel + 2
        self.CH_ROT_CW_VELOCITY = self.rotatorStartChannel + 3
        self.CH_ROT_CCW_VELOCITY = self.rotatorStartChannel + 4

        event = self.getInputEvent('rotatorVelocity')
        event += self._onRotatorVelocity
        # self.logger.debug('registed listener for rotator velocity event: '+self.options['rotatorVelocity'])

    def _onWinchVelocity(self, vel):
        if vel > 0:
            # self.logger.debug('up, vel: '+str(vel))
            self._winchToPos(1.0, vel) # up
        else:
            # self.logger.debug('down, vel: '+str(-vel))
            self._winchToPos(0.0, -vel) # down

    def _winchToPos(self, pos, velocity):
        # self.logger.debug('winch to pos: '+str(pos)+' with velocity: '+str(velocity))
        self._setChannel(self.CH_WINCH_POS_ROUGH, pos)
        self._setChannel(self.CH_WINCH_POS_VELOCITY, velocity)

    def _onWinchResetUpVelocity(self, vel):
        self.logger.debug('setting winch reset-up velocity: '+str(vel))
        pass

    def _onWinchResetDownVelocity(self, vel):
        self.logger.debug('setting winch reset-down velocity: '+str(vel))

    def _onRotatorVelocity(self, vel):
        if vel > 0:
            self._setChannel(self.CH_ROT_CW_VELOCITY, vel)
        else:
            self._setChannel(self.CH_ROT_CCW_VELOCITY, -vel)
