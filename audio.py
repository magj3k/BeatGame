

class AudioController(object):
    def __init__(self, level = 0, bpm = 120, elements = []):
        self.level = level
        self.bpm = bpm
        self.elements = elements

    def on_update(self, dt, player, active_keys):
        pass

    def on_key_down(self, key):
        pass

    def on_key_up(self, key):
        pass

    def jump(self):
        pass