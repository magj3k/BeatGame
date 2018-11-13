from scene_manager import *
from scenes import *
from core import *
from kivy.clock import Clock as kivyClock

class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.scene_manager = SceneManager(scenes)
        self.canvas.add(self.scene_manager)

    def on_update(self):
        dt = kivyClock.frametime
        self.scene_manager.on_update(dt)

run(MainWidget)