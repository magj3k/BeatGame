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

        # handling multiple keypresses
        self.time = 0
        self.timing_window = 0.015
        self.current_keypresses = []

    def on_update(self):
        dt = kivyClock.frametime
        self.time += dt
        self.scene_manager.on_update(dt, self.active_keys)

        if self.current_keypresses:
            if self.time > self.current_keypresses[-1][1] + self.timing_window or len(self.current_keypresses) == 3:
                self.scene_manager.on_multi_key_down([key[0] for key in self.current_keypresses])
                self.current_keypresses = []


    def on_key_down(self, keycode, modifiers):
        key = keycode[1]
        self.scene_manager.on_key_down(key)
        if key in self.active_keys:
            self.active_keys[key] = True
            self.current_keypresses.append((keycode[1], self.time))
            

    def on_key_up(self, keycode):
        key = keycode[1]
        self.scene_manager.on_key_up(key)
        if key in self.active_keys:
            self.active_keys[key] = False

run(MainWidget)
