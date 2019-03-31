import signal
from evento import Event
from py2030.base_component import BaseComponent

class Signals(BaseComponent):
    config_name = 'signals'

    def __init__(self, options = {}):
        super().__init__(options)

    def setup(self, event_manager=None):
        super().setup(event_manager)

        self.alarmEvent = self.getOutputEvent('alarm', dummy=False)
        if not self.alarmEvent == None:
            signal.signal(signal.SIGALRM, self.alarmHandler)

        # CTLR-C
        self.interruptEvent = self.getOutputEvent('interrupt', dummy=False)
        if not self.interruptEvent == None:
            signal.signal(signal.SIGINT, self.interruptHandler)

        # kill
        self.terminateEvent = self.getOutputEvent('terminate', dummy=False)
        if not self.terminateEvent == None:
            signal.signal(signal.SIGTERM, self.terminateHandler)

        # signal.signal(signal.SIGSTOP, self.generalHandler)
        # signal.signal(signal.SIGKILL, self.generalHandler)
        # signal.signal(signal.SIGCONT, self.generalHandler)
        # signal.signal(signal.SIGINFO, self.generalHandler)

    def destroy(self):
        pass

    def alarmHandler(self, signum, frame):
        # signum == 15 for kill
        # signum == 2 for CTLR-C
        self.logger.debug('Signals.alarmHandler: {0}, {1}'.format(signum, frame))
        self.alarmEvent()

    def interruptHandler(self, signum, frame):

        self.logger.debug('Signals.interruptHandler: {0}, {1}'.format(signum, frame))
        self.interruptEvent()

    def terminateHandler(self, signum, frame):
        # the kill signal
        self.logger.debug('Signals.terminateHandler: {0}, {1}'.format(signum, frame))
        self.terminateEvent()

    # def generalHandler(self, signum, frame):
    #     self.logger.debug('Signals.generalHandler: {0}, {1}'.format(signum, frame))
