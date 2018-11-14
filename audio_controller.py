from core import *
from audio.audio import *
from audio.clock import *
from audio.mixer import *
from audio.wavegen import *
from audio.wavesrc import *

level_map = [
                {'bg_music': 'audio/KillerQueen_bg.wav',
                 'fg_music': 'audio/KillerQueen_solo.wav',
                 'jump_sfx': 'audio/snare.wav',
                 'walk_sfx': 'audio/closedhihat.wav'}
]

class AudioController(object):
    def __init__(self, level = 0, bpm = 120, elements = []):
        self.level = level
        self.bpm = bpm

        self.musical_elements = []
        for el in elements:
            if el.musical:
                self.musical_elements.append(el)

        self.level_music = level_map[self.level]

        # create Audio, Mixer
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.mixer.set_gain(0.5)
        self.audio.set_generator(self.mixer)

        # create TempoMap, AudioScheduler
        self.tempo_map  = SimpleTempoMap(120)
        self.sched = AudioScheduler(self.tempo_map)

        # create generators
        self.bg_gen = WaveGenerator(WaveFile(self.level_music['bg_music']), True)
        self.bg_gen.set_gain(0.7)
        self.fg_gen = WaveGenerator(WaveFile(self.level_music['fg_music']), True)
        self.fg_gen.set_gain(0)
        self.jump_gen = WaveGenerator(WaveFile(self.level_music['jump_sfx']))
        self.jump_gen.set_gain(0.5)
        self.walk_gen = WaveGenerator(WaveFile(self.level_music['walk_sfx'], True))
        self.walk_gen.set_gain(0.5)
        self.walk_gen.pause()

        # add generators to mixer
        self.mixer.add(self.sched)
        self.mixer.add(self.bg_gen)
        self.mixer.add(self.fg_gen)
        self.mixer.add(self.walk_gen)

    def jump(self):
        self.jump_gen.reset()
        self.mixer.add(jump)
        self.jump_gen.play()

    def on_key_down(self, keycode):
        pass

    def on_key_up(self, keycode):
        pass

    def on_update(self, dt, player, active_keys):
        self.audio.on_update()

        # play sound for continuous player movement
        if player.on_ground and (active_keys['left'] == True or active_keys['right'] == True):
            self.walk_gen.play()

        # play foreground music when past few player moves have been on beat

        # play game element music based on proximity of player
        