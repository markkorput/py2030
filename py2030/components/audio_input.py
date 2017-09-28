#!/usr/bin/env python
from py2030.base_component import BaseComponent

# dependencies are lazy-loaded because not every component will be loaded,
# so not every component's dependencies should have to be imported
deps = {}
def loadDependencies():
    global deps

    if deps:
        return deps

    import sys

    try:
        import pyaudio as pya
        pyaudio = pya
    except ImportError:
        pyaudio = None
        sys.stderr.write("could not load pyaudio library, audio_input will not function properly\n")

    try:
        import audioop
    except ImportError:
        audioop = None
        sys.stderr.write("could not load audioop library, audio_input will not function properly\n")

    del sys

    deps = {}
    deps['pyaudio'] = pyaudio
    deps['audioop'] = audioop
    return deps

class AudioInput(BaseComponent):
    config_name = 'audio_inputs'

    def setup(self, event_manager):
        deps = loadDependencies()
        self.pyaudio = deps['pyaudio']
        self.audioop = deps['audioop']

        BaseComponent.setup(self, event_manager)
        self.levelEvent = self.getOutputEvent('level', True)

        if not self.pyaudio:
            self.stream = None
        else:
            self.stream = self.pyaudio.PyAudio().open(
                format=self.pyaudio.paInt16, # self.pyaudio.paFloat32
                channels=1,
                rate=44100,
                #input_device_index=2,
                input=True,
                stream_callback=self._streamCallback)

            self.stream.start_stream()

    def destroy(self):
        if hasattr(self, 'stream') and self.stream != None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def _streamCallback(self, in_data, frame_count, time_info, flag):
        level = self.audioop.rms(in_data, 2)
        self.levelEvent.fire(level)

        s = "level: "
        i = 0
        while i < level:
            i += 10
            s += "#"
        self.logger.debug(s)

        if self.pyaudio:
            return (in_data, self.pyaudio.paContinue)
