#!/usr/bin/env python
from component_manager import ComponentManager

if __name__ == '__main__':
    cm = ComponentManager()
    cm.setup()

    try:
        while cm.running:
            cm.update()
    except KeyboardInterrupt:
        print 'KeyboardInterrupt. Quitting.'

    cm.destroy()
