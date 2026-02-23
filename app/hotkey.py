import time
from pynput import keyboard

def global_listener(app_instance):
    def on_activate():
        app_instance.on_stop_hotkey()
    
    # hotkey combination
    with keyboard.GlobalHotKeys({
        '<alt>+s': on_activate
    }) as h:
        h.join()