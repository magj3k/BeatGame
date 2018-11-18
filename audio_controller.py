from core import *
from audio.audio import *
from audio.clock import *
from audio.mixer import *
from audio.wavegen import *
from audio.wavesrc import *

level_map = [
                {'bg_music': 'audio/electro_bg.wav',
                 'fg_music': 'audio/electro_fg.wav',
                 'jump_sfx': 'audio/jump_sound.wav',
                 'walk_sfx': 'audio/walk_sound_soft.wav',
                 'key_sfx': 'audio/key_sfx.wav',
                 'bpm': 110},
]

class AudioController(object):
    def __init__(self, level = 0, bpm = 120, elements = [], beat_callback = None):
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

        # beat tracking
        self.beat = 0

        # callbacks
        self.beat_callback = beat_callback

        # past 5 player moves
        self.move_times = []
        self.fg_gain = 0.5

        # environment
        self.object_ticks = {}

    def get_key(self):
        pass

    def change_game_modes(self):
        pass

    def get_key(self):
        key_gen = WaveGenerator(WaveFile(self.level_music['key_sfx']))
        key_gen.set_gain(0.5)
        self.mixer.add(key_gen)

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

    def object_sound(self, tick, object_props):
        gain, sound, index = object_props
        if tick in self.object_ticks[index]:
            obj_gen = WaveGenerator(WaveFile(sound))
            obj_gen.set_gain(gain)
            self.mixer.add(obj_gen)
            self.object_ticks[index].remove(tick)

    def on_key_down(self, keycode):
        if keycode in ['left', 'right', 'spacebar']:
            self.move_times.append(self.sched.get_tick())

    def on_key_up(self, keycode):
        pass

    def on_update(self, dt, player, active_keys):
        self.audio.on_update()
        now = self.sched.get_tick()

        # callbacks/beat tracking
        if now // self.note_grid != self.beat:
            self.beat = now // self.note_grid

            if self.beat_callback != None:
                self.beat_callback(self.beat)

        # play sound for continuous player movement
        if player.on_ground and (active_keys['left'] == True or active_keys['right'] == True):
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
            # print("begin hi")
            for move in self.move_times[-3:]:
                quantized_move = quantize_tick_up(move, self.note_grid/4)
                # print("hi")
                # print(quantized_move - move)
                # print(move - (quantized_move - self.note_grid/4))
                if not (quantized_move - move < 10 or move - (quantized_move - self.note_grid/4) < 50):
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
        player_pos = player.world_pos

        for index, element in enumerate(self.musical_elements):
            cell_bounds = element.cell_bounds
            x_dist = min(abs(player_pos[0] - cell_bounds[0][0]), abs(player_pos[0] - cell_bounds[1][0]))
            y_dist = min(abs(player_pos[1] - cell_bounds[0][1]), abs(player_pos[1] - cell_bounds[1][1]))
            dist = (x_dist**2 + y_dist**2)**0.5
            dist = max(0, dist - 2)
            # max gain 0.6
            # you start hearing things when you're less than 16 dist away
            gain = 0.6 * max(0, (16 - dist)) / 16
            obj_sound = element.sound_path

            # find closest beat to now
            beats = element.beats
            prev_beat = quantize_tick_up(now, self.note_grid*4) - self.note_grid*4
            next_tick = prev_beat + 8*self.note_grid
            for beat_num in beats:
                tick = prev_beat + self.note_grid * (beat_num-1)
                if tick > now:
                    if tick < next_tick:
                        next_tick = tick
                else:
                    tick += 4*self.note_grid
                    if tick < next_tick:
                        next_tick = tick

            if next_tick < prev_beat + 8*self.note_grid:
                if index in self.object_ticks and next_tick in self.object_ticks[index]:
                    pass
                else:
                    if index not in self.object_ticks:
                        self.object_ticks[index] = set()

                    self.sched.post_at_tick(self.object_sound, next_tick, (gain, obj_sound, index))
                    self.object_ticks[index].add(next_tick)
