from scene_manager import *
from scenes import *
from core import *
from kivy.clock import Clock as kivyClock

class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.active_keys = {'w': False,
                                        's': False,
                                        'a': False,
                                        'd': False,
                                        'left': False,
                                        'right': False,
                                        'up': False,
                                        'down': False,
                                        'spacebar': False,
                                        'enter': False,
                                        '1': False,
                                        '2': False,
                                        '3': False,
                                        '4': False,
                                        '5': False,
                                        '6': False,
                                        '7': False}  # only contains supported keys

        self.scene_manager = SceneManager(scenes)
        self.canvas.add(self.scene_manager)

    def on_update(self):
        dt = kivyClock.frametime
        self.scene_manager.on_update(dt, self.active_keys)

    def on_key_down(self, keycode, modifiers):
        key = keycode[1]
        self.scene_manager.on_key_down(key)
        if key in self.active_keys:
            self.active_keys[key] = True

    def on_key_up(self, keycode):
        key = keycode[1]
        self.scene_manager.on_key_up(key)
        if key in self.active_keys:
            self.active_keys[key] = False

run(MainWidget)
