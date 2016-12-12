#!/usr/bin/env python
from optparse import OptionParser
from .component_manager import ComponentManager

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-p', '--profile', dest='profile', default=None)
    # parser.add_option('-f', '--file', dest='file', default=None)
    parser.add_option('-v', '--verbose', dest='verbose', action="store_true", default=False)
    parser.add_option('-y', '--yml', '--yaml', '--config-file', dest='config_file', default=None)

    opts, args = parser.parse_args()

    if opts.profile == None:
        import socket
        opts.profile = socket.gethostname().replace('.', '_')
        del socket

    options = {
        'verbose': opts.verbose,
        'profile': opts.profile,
        'config_file': opts.config_file
    }

    cm = ComponentManager(options)
    cm.setup()

    try:
        while cm.running:
            cm.update()
    except KeyboardInterrupt:
        print 'KeyboardInterrupt. Quitting.'

    cm.destroy()
