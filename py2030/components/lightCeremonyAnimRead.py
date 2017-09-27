# #!/usr/bin/env python
# import time
# import logging
# from evento import Event
# from py2030.base_component import BaseComponent
#
# try:
#     import pysimpledmx
# except ImportError:
#     pysimpledmx = None
#
# class LightCeremonyController(BaseComponent):
#     config_name = 'lightCeremonyAnimReaders'
#
#     def __init__(self, options = {}):
#         self.options = options
#         self.event_manager = None
#
#         self.logger = logging.getLogger(__name__)
#         if 'verbose' in options and options['verbose']:
#             self.logger.setLevel(logging.DEBUG)
#
#         self.bPlaying = False
#
#     def setup(self, event_manager):
#         self.event_manager = event_manager
#
#     def update(self):
#         if self.nextFrame = None:
#             self.nextFrame = self._getNextFrame()
#
#
#     def _start(self):
#         self.bPlaying = True
#         self.fh = open(self.getOption('file', '/home/pi/anim.csv'), 'rt')
#         self.nextFrame = None
#
#     def _stop(self):
#         self.bPlaying = False
#         if self.fh:
#             self.fh.close()
#
#     def _getNextFrame(self):
#         line = fh.readline()
#         # todo convert line into frame data
#         frame = line
#         return frame
