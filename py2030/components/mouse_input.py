#!/usr/bin/env python
import time, threading, logging
from py2030.base_component import BaseComponent

deps = {}
def loadDeps():
    global deps
    if deps:
        return deps

    deps = {}
    try:
        import pynput.mouse as mouse
        deps['mouse'] = mouse
    except ImportError as err:
        logging.getLogger(__name__).warning("import pynput.mouse failed, MouseInput component will not work.")
        logging.getLogger(__name__).warning(err)
        deps['mouse'] = None

    return deps

class MouseInput(BaseComponent):
    config_name = 'mouse_inputs'

    def __init__(self, options = {}):
        BaseComponent.__init__(self,options)
        self.mouse = loadDeps()['mouse']
        self.listener = None
        self.thread = None

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.thread:
            if self.listener:
                self.logger.debug('killing mouse listener thread')
                self.listener.stop()
                self.listener = None
            self.thread = None

    def setup(self, event_manager):
        BaseComponent.setup(self, event_manager)
        self.clickE = self.getOutputEvent('click')
        self.clickLeftE = self.getOutputEvent('click_left')
        self.clickRightE = self.getOutputEvent('click_right')
        self.moveE = self.getOutputEvent('move')
        self.scrollE = self.getOutputEvent('scroll')
        self.scrollUpE = self.getOutputEvent('scroll_up')
        self.scrollDownE = self.getOutputEvent('scroll_down')
        self.thread = threading.Thread(target=self._threadMethod, args=())
        self.thread.start()

    def _threadMethod(self):
        if self.mouse:
            self.logger.debug('starting mouse listener thread')
            with self.mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll, on_move=self.on_move) as listener:
                self.listener = listener
                self.listener.join()

    def on_click(self, x,y,btn,pressed):
        self.logger.debug('mouse CLICK '+str(x)+','+str(y)+': '+str(btn)+'-'+str(pressed))
        self.clickE.fire()

        if btn == self.mouse.Button.left:
            self.clickLeftE.fire()

        if btn == self.mouse.Button.right:
            self.clickRightE.fire()

    def on_scroll(self, x,y,dx,dy):
        self.logger.debug('mouse SCROLL '+str(dx)+','+str(dy))
        # print("SCROLL: " + str(x)+','+str(y)+' - '+str(dx)+','+str(dy))
        self.scrollE.fire()
        if(dy > 0):
            self.scrollUpE.fire()
        if(dy < 0):
            self.scrollDownE.fire()

    def on_move(self, x,y):
        # self.logger.debug('mouse SCROLL '+str(x)+','+str(y))
        self.moveE.fire()
