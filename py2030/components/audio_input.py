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
        BaseComponent.setup(self, event_manager)
        self.levelEvent = self.getOutputEvent('level', True)
        self.frame_size = self.getOption('frame_size', 1024)

        deps = loadDependencies()
        self.pyaudio = deps['pyaudio']
        self.audioop = deps['audioop']

        if not self.pyaudio:
            self.stream = None
        else:
            self.stream = self.pyaudio.PyAudio().open(
                format=self.pyaudio.paInt16, # self.pyaudio.paFloat32
                channels=1,
                rate=44100,
                input_device_index=self._getDeviceIndex(),
                input=True,
                frames_per_buffer=self.frame_size)
                #stream_callback=self._streamCallback)

            self.stream.start_stream()

    def destroy(self):
        if hasattr(self, 'stream') and self.stream != None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def update(self):
        if self.stream:
            dat = self.stream.read(self.frame_size, exception_on_overflow=False)
            self._streamCallback(dat, None, None, None);

    def _streamCallback(self, in_data, frame_count, time_info, flag):
        level = self.audioop.rms(in_data, 2)
        self.levelEvent.fire(level)

        if self.verbose:
            s = "level: "
            i = 0
            while i < level:
                i += 50
                s += "#"
            self.logger.debug(s)

        if self.pyaudio:
            return (in_data, self.pyaudio.paContinue)

    def _getDeviceIndex(self):
        device_index = self.getOption('device_index', None)

        if not device_index:
            device_name = self.getOption('device_name', None)

            if device_name:
                for i in range(self.pyaudio.PyAudio().get_device_count()):
                    name = self.pyaudio.PyAudio().get_device_info_by_index(i)['name']
                    log = 'Audio device: ' + name
                    if name == device_name or name.lower().find(device_name.lower()) >= 0:
                        device_index = i
                        log += '\t<-----'

                    self.logger.debug(log)

        return device_index
