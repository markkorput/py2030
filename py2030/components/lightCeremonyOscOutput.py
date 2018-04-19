from .osc_output import OscOutput

class LightCeremonyOscOutput(OscOutput):
    config_name = 'lightCeremonyOscOutputs'

    def setup(self, event_manager=None):
        OscOutput.setup(self, event_manager)

        self.winchVelEvent = self.event_manager.get('osc-winchVel')
        self.rotVelEvent = self.event_manager.get('osc-rotVel')
        self.lightBrightEvent = self.event_manager.get('osc-lightBright')
        self.frameEvent = self.event_manager.get('osc-frame')

        e = self.getEventFrom('events', 'frame')
        e.subscribe(self._onFrame)

    def _onFrame(self, frame_data):
        self.winchVelEvent.fire(frame_data[1])
        self.rotVelEvent.fire(frame_data[2])
        self.lightBrightEvent.fire(frame_data[3])
        self.frameEvent.fire(frame_data[1], frame_data[2], frame_data[3])
