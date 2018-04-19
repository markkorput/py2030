import pynput.mouse # import Button, Controller
import time


def on_click(x,y,btn,pressed):
    print("CLICK: " + str(x)+','+str(y)+' - btn: '+str(btn)+', pressed: '+str(pressed))

def on_scroll(x,y,dx,dy):
    print("SCROLL: " + str(x)+','+str(y)+' - '+str(dx)+','+str(dy))

if __name__ == '__main__':
    mouse = pynput.mouse.Controller()

    with pynput.mouse.Listener(on_click=on_click, on_scroll=on_scroll) as listener:
        try:
            while True:
                # Read pointer position
                print('The current pointer position is {0}'.format(mouse.position))
                time.sleep(0.5)
        except KeyboardInterrupt:
            print('KeyboardInterrupt. Quitting.')

        listener.stop()
        listener.join()


# # Set pointer position
# mouse.position = (10, 20)
# print('Now we have moved it to {0}'.format(
#     mouse.position))
#
# # Move pointer relative to current position
# mouse.move(5, -5)
#
# # Press and release
# mouse.press(Button.left)
# mouse.release(Button.left)
#
# # Double click; this is different from pressing and releasing
# # twice on Mac OSX
# mouse.click(Button.left, 2)
#
# # Scroll two steps down
# mouse.scroll(0, 2)
