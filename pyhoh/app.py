#!/usr/bin/env python
from optparse import OptionParser
from component_manager import ComponentManager

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-p', '--profile', dest='profile', default="default")
    # parser.add_option('-f', '--file', dest='file', default=None)
    parser.add_option('-v', '--verbose', dest='verbose', action="store_true", default=False)

    opts, args = parser.parse_args()

    options = {'verbose': opts.verbose, 'profile': opts.profile}

    cm = ComponentManager(options)
    cm.setup()

    try:
        while cm.running:
            cm.update()
    except KeyboardInterrupt:
        print 'KeyboardInterrupt. Quitting.'

    cm.destroy()
