import logging
from evento import Event

class CsvFramesFile:
    def __init__(self, path=None, loop=True, delimiter=',', verbose=False):
        self.path = path
        self.loop = loop
        self.delimiter = ','

        self.file = None

        # last read frame info
        self.currentFrame = None
        self.currentFrameTime = None
        self.currentFrameIndex = -1

        # events
        self.loopEvent = Event()

        self.logger = logging.getLogger(__name__)
        if verbose:
            self.logger.setLevel(logging.DEBUG)

    def __del__(self):
        self.close()

    def open(self):
        if self.file:
            self.close()

        try:
            if not self.path:
                self.logger.warn('no file path')
            else:
                self.file = open(self.path, 'rb')
                # self.csvreader = csv.reader(self.file)
                self.logger.debug("csv frames file opened: %s" % self.path)
        except:
            self.logger.warn("could not open csv frames file: %s" % self.path)
            self.file = None

    def rewind(self):
        if self.file:
            self.file.seek(0)

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
            self.logger.debug("csv frames file closed")

    def setLoop(self, loop):
        self.loop = loop

    def getNextFrame(self):
        while(True):
            line = self.file.readline()

            if not line:
                if not self.loop:
                    return None

                self.file.seek(0)
                self.loopEvent(self)
                self.loop = False # to avoid endless loop for empty files
                result = self.readNextFrame()
                self.loop = True
                return result

            line = line.strip()

            # skip comments (ie. don't break and stay inside while(True) loop)
            if not line.startswith('#'):
                break

        return line.split(self.delimiter)
