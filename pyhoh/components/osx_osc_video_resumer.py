import os
import logging

class OsxOscVideoResumer:
    def __init__(self, options = {}):
        self.options = options
        self.resume_on = options['resume_on'] if 'resume_on' in self.options else []
        self.osc_input = None

        self.logger = logging.getLogger(__name__)
        if 'verbose' in self.options and self.options['verbose']:
            self.logger.setLevel(logging.DEBUG)

    def setup(self, osc_input):
        self.osc_input = osc_input
        self.osc_input.messageEvent += self._onOscMessage
        self.logger.debug('OsxOscVideoResumer setup, resuming on following incoming osc messages: \n - {}'.format("\n - ".join(self.resume_on)))

    def destroy(self):
        if self.osc_input:
            self.osc_input.messageEvent -= self._onOscMessage
            self.osc_input = None

    def _onOscMessage(self, addr, tags, data, client_address):
        if addr in self.resume_on:
            self.resume()

    def resume(self):
        cmd = """/usr/bin/osascript -e 'tell application "QuickTime Player"' \
        -e "activate" \
        -e 'tell application "System Events"' -e 'keystroke "f" using {command down}' \
        -e "end tell" -e "play the front document" -e "end tell"
        """
        self.logger.debug('running command: {0}'.format(cmd))
        os.system(cmd)
