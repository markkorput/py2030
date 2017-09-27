#!/usr/bin/env python
import sys, logging
from evento import Event
from py2030.base_component import BaseComponent

try:
    import numpy
except ImportError:
    numpy = None
    sys.stderr.write("could not load numpy library, audio_input will not function properly\n")

try:
    import pyaudio
except ImportError:
    pyaudio = None
    sys.stderr.write("could not load pyaudio library, audio_input will not function properly\n")

try:
    import analyse
except ImportError:
    analyse = None
    sys.stderr.write("could not load analyse library, audio_input will not function properly\n")

try:
    import audioop
except ImportError:
    audioop = None
    sys.stderr.write("could not load audioop library, audio_input will not function properly\n")

class AudioInput(BaseComponent):
    config_name = 'audio_inputs'

    def setup(self, event_manager):
        BaseComponent.setup(self, event_manager)

        if not pyaudio:
            self.stream = None
        else:
            self.stream = pyaudio.PyAudio().open(
                format=pyaudio.paInt16, # pyaudio.paFloat32
                channels=1,
                rate=44100,
                #input_device_index=2,
                input=True,
                stream_callback=self._streamCallback)
            self.fulldata = numpy.array([])
            self.dry_data = numpy.array([])

            self.stream.start_stream()

    def destroy(self):
        if hasattr(self, 'stream') and self.stream != None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    # def update(self):
    #     if self.stream:
    #         # Read raw microphone data
    #         rawsamps = self.stream.read(1024)
    #         # Convert raw data to NumPy array
    #         samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
    #         # Show the volume and pitch
    #         self.logger.debug('loudness: ', analyse.loudness(samps))
    #         # print analyse.loudness(samps), analyse.musical_detect_pitch(samps)

    def _streamCallback(self, in_data, frame_count, time_info, flag):
        if numpy:
            # audio_data = numpy.fromstring(in_data, dtype=numpy.float32)
            # self.dry_data = numpy.append(self.dry_data,audio_data)
            # #do processing here
            # self.fulldata = numpy.append(self.fulldata,audio_data)
            # self.logger.warn('fulldaata')
            # self.logger.warn(self.fulldata)
            level = audioop.rms(in_data, 2)
            s = "level: "
            i = 0
            while i < level:
                i += 10
                s += "#"
            self.logger.debug(s)
        return (in_data, pyaudio.paContinue)


#
#
#
# # Initialize PyAudio
# pyaud = pyaudio.PyAudio()
#
# # Open input stream, 16-bit mono at 44100 Hz
# # On my system, device 4 is a USB microphone
# stream = pyaud.open(
#     format = pyaudio.paInt16,
#     channels = 1,
#     rate = 44100,
#     input_device_index = 2,
#     input = True)
#
# while True:
#     # Read raw microphone data
#     rawsamps = stream.read(1024)
#     # Convert raw data to NumPy array
#     samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
#     # Show the volume and pitch
#     print analyse.loudness(samps), analyse.musical_detect_pitch(samps)
