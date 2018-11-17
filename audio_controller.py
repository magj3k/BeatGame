from core import *
from audio.audio import *
from audio.clock import *
from audio.mixer import *
from audio.wavegen import *
from audio.wavesrc import *

level_map = [
                {'bg_music': 'audio/electro_bg.wav',
                 'fg_music': 'audio/electro_fg.wav',
                 'jump_sfx': 'audio/snare.wav',
                 'walk_sfx': 'audio/closedhihat.wav',
                 'bpm': 110},
]

class AudioController(object):
    def __init__(self, level = 0, bpm = 120, elements = []):
        self.level = level
        self.level_music = level_map[self.level]
        self.bpm = self.level_music['bpm']
        self.note_grid = 480

        self.musical_elements = []
        for el in elements:
            if el.musical:
                self.musical_elements.append(el)

        # create Audio, Mixer
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.mixer.set_gain(0.5)
        self.audio.set_generator(self.mixer)

        # create TempoMap, AudioScheduler
        self.tempo_map  = SimpleTempoMap(self.bpm)
        self.sched = AudioScheduler(self.tempo_map)

        # create generators
        self.bg_gen = WaveGenerator(WaveFile(self.level_music['bg_music']), True)
        self.bg_gen.set_gain(0.3)
        self.fg_gen = WaveGenerator(WaveFile(self.level_music['fg_music']), True)
        self.fg_gen.set_gain(0)

        # add generators to mixer
        self.mixer.add(self.sched)
        self.mixer.add(self.bg_gen)
        self.mixer.add(self.fg_gen)

        # walking
        self.walk_ticks = set()

        # past 5 player moves
        self.move_times = []
        self.fg_gain = 0.5

    def jump(self):
        jump_gen = WaveGenerator(WaveFile(self.level_music['jump_sfx']))
        jump_gen.set_gain(0.5)
        self.mixer.add(jump_gen)

    def walk_once(self, tick, ignore):
        if tick in self.walk_ticks:
            walk_gen = WaveGenerator(WaveFile(self.level_music['walk_sfx']))
            walk_gen.set_gain(0.5)
            self.mixer.add(walk_gen)
            self.walk_ticks.remove(tick)

    def on_key_down(self, keycode):
        if keycode in ['left', 'right', 'spacebar']:
            self.move_times.append(self.sched.get_tick())

    def on_key_up(self, keycode):
        pass

    def on_update(self, dt, player, active_keys):
        self.audio.on_update()

        # play sound for continuous player movement
        if player.on_ground and (active_keys['left'] == True or active_keys['right'] == True):
            now = self.sched.get_tick()
            next_beat = quantize_tick_up(now, self.note_grid/2)
            if next_beat not in self.walk_ticks:
                self.sched.post_at_tick(self.walk_once, next_beat)
                self.walk_ticks.add(next_beat)
        else:
            now = self.sched.get_tick()
            next_beat = quantize_tick_up(now, self.note_grid)
            if next_beat in self.walk_ticks:
                self.walk_ticks.remove(next_beat)

        # play foreground music when past few player moves have been on beat
        if len(self.move_times) > 2:
            on_beat = True
            for move in self.move_times[-3:]:
                quantized_move = quantize_tick_up(move, self.note_grid/2)
                if not (quantized_move - move < 30 or move - (quantized_move - self.note_grid/2) < 30):
                    on_beat = False
            self.on_beat = on_beat

            gain = self.fg_gen.get_gain()
            last_move =  self.sched.get_tick() - self.move_times[-1]
            if on_beat and gain < self.fg_gain and last_move < self.note_grid*4:
                new_gain = gain + self.fg_gain * (self.bpm * dt/(60*4))
                self.fg_gen.set_gain(min(new_gain, self.fg_gain))

            if gain > 0 and (not on_beat or last_move >= self.note_grid*4):
                new_gain = gain - self.fg_gain * (self.bpm * dt/(60*4))
                self.fg_gen.set_gain(max(0, new_gain))

        # play game element music based on proximity of player