from core import *
from audio.audio import *
from audio.clock import *
from audio.mixer import *
from audio.wavegen import *
from audio.wavesrc import *

level_map = [
				{'bg_music': 'audio/KillerQueen_bg.wav',
				 'fg_music': 'audio/KillerQueen_solo.wav'}
]

class AudioController(object):
    def __init__(self, level = 0, bpm = 120, elements = []):
        self.level = level
        self.bpm = bpm
        self.elements = elements

        self.level_elements = level_map[self.level]

        # create Audio, Mixer
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.mixer.set_gain(0.5)
        self.audio.set_generator(self.mixer)

        # create TempoMap, AudioScheduler
        self.tempo_map  = SimpleTempoMap(120)
        self.sched = AudioScheduler(self.tempo_map)

        # add generators to mixer
        self.mixer.add(self.sched)
        self.bg_gen = WaveGenerator(WaveFile(self.level_elements['bg_music']))
        self.fg_gen = WaveGenerator(WaveFile(self.level_elements['fg_music']))
        self.mixer.add(self.bg_gen)
        self.mixer.add(self.fg_gen)

    def on_key_down(self, keycode):
    	pass

   	def on_key_up(self, keycode):
   		pass

    def on_update(self, dt, player, active_keys):
        # play sound for continuous player movement

        # play foreground music when past few player moves have been on beat

        # play game element music based on proximity of player
		