#!/usr/bin/env python
import time
from evento import Event
from py2030.components.dmx_output import DmxOutput

class LightCeremonyDmxOutput(DmxOutput):
    config_name = 'lightCeremonyDmxOutputs'

    def setup(self, event_manager=None):
        DmxOutput.setup(self, event_manager)
        self.bottomPosition = self.getOption('bottomPosition', 0.5)
        self.winchStartChannelIdx = int(self.getOption('winchStartChannel', 1))-1

        self.CH_WINCH_POS_ROUGH = self.winchStartChannelIdx + 0
        self.CH_WINCH_POS_FINE = self.winchStartChannelIdx + 1
        self.CH_WINCH_POS_VELOCITY = self.winchStartChannelIdx + 2
        self.CH_WINCH_POS_RESET_UP = self.winchStartChannelIdx + 5

        event = self.getInputEvent('winchVelocity')
        event += self._onWinchVelocity
        # self.logger.debug('registed listener for winch velocity event: '+self.options['winchVelocity'])
        event = self.getInputEvent('winchResetUpVelocity')
        event += self._onWinchResetUpVelocity
        event = self.getInputEvent('winchResetDownVelocity')
        event += self._onWinchResetDownVelocity

        self.rotatorStartChannel = int(self.options['rotatorStartChannel'])-1 if 'rotatorStartChannel' in self.options else 0

        self.CH_ROT_POS_ROUGH = self.rotatorStartChannel + 0
        self.CH_ROT_POS_FINE = self.rotatorStartChannel + 1
        self.CH_ROT_POS_VELOCITY = self.rotatorStartChannel + 2
        self.CH_ROT_CW_VELOCITY = self.rotatorStartChannel + 3
        self.CH_ROT_CCW_VELOCITY = self.rotatorStartChannel + 4

        self.getInputEvent('rotatorVelocity').subscribe(self._onRotatorVelocity)
        # self.logger.debug('registed listener for rotator velocity event: '+self.options['rotatorVelocity'])
        self.getInputEvent('black').subscribe(self._onBlack)

        self.bResetDownActive = False

    def update(self):
        if self.bResetDownActive:
            t = time.time()
            dt = 0.0
            if self.resetPreviousTime:
                dt = t-self.resetPreviousTime
            self.resetPreviousTime = t

            self.resetDownPos -= dt * self.getOption('resetDownDeltaPos', 0.001)
            self._winchToPos(self.resetDownPos, self.resetDownVelocity)
            self.event_manager.get('resetDownPos').fire(self.resetDownPos)
            self.logger.debug('reset down pos: '+str(self.resetDownPos))

        # super
        DmxOutput.update(self)

    def _onWinchVelocity(self, vel):
        if vel > 0:
            # self.logger.debug('up, vel: '+str(vel))
            self._winchToPos(1.0, vel) # up
        else:
            # self.logger.debug('down, vel: '+str(-vel))
            self._winchToPos(self.bottomPosition, -vel) # down

    def _winchToPos(self, pos, velocity):
        # self.logger.debug('winch to pos: '+str(pos)+' with velocity: '+str(velocity))
        self._setChannel(self.CH_WINCH_POS_ROUGH, pos)
        self._setChannel(self.CH_WINCH_POS_VELOCITY, velocity)

    def _onWinchResetUpVelocity(self, vel):
        self.logger.debug('setting winch reset-up velocity: '+str(vel))
        self._setChannel(self.CH_WINCH_POS_VELOCITY, 0.0) # just to be sure it doesn't interfere
        self._setChannel(self.CH_WINCH_POS_RESET_UP, vel)

    def _onWinchResetDownVelocity(self, vel):
        if vel > 0.0:
            self._startResetDown(vel)
        else:
            self._endResetDown()

    def _onRotatorVelocity(self, vel):
        if vel > 0:
            self._setChannel(self.CH_ROT_CW_VELOCITY, vel)
        else:
            self._setChannel(self.CH_ROT_CCW_VELOCITY, -vel)

    def _startResetDown(self, velocity):
        self.logger.debug('starting winch reset-down at velocity: '+str(velocity))
        self.resetDownPos = 1.0
        self.resetPreviousTime = None
        self.resetDownVelocity = velocity
        self.bResetDownActive = True # update method takes it from here

    def _endResetDown(self):
        self.logger.debug('ending winch reset-down...')
        self.bResetDownActive = False
        self.bottomPosition = self.resetDownPos
        self.event_manager.get('resetDownPos').fire(0.0)
        self._winchToPos(1.0, 0.5) # move back up
        self.logger.warn("winch reset-down finished at position: "+str(self.bottomPosition))

    def _onBlack(self):
        self.black()
