

class AudioController(object):
    def __init__(self, level = 0, bpm = 120, elements = []):
        self.level = level
        self.bpm = bpm
        self.elements = elements

    def on_update(self, dt, player, active_keys):
        pass
