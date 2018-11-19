from core import *
from audio.audio import *
from audio.clock import *
from audio.mixer import *
from audio.wavegen import *
from audio.wavesrc import *
import random

level_map = [
                {'bg_music': 'audio/electro_bg.wav',
                 'fg_music': 'audio/electro_fg.wav',
                 'fg_track_1': 'audio/electro_main.wav',
                 'fg_track_2': 'audio/electro_support.wav',
                 'jump_sfx': 'audio/jump_sound.wav',
                 'walk_sfx': 'audio/walk_sound_soft.wav',
                 'key_sfx': 'audio/key_sfx.wav',
                 'bpm': 110},
]
puzzle_map = [
                {'bg_music': 'audio/electro_bg.wav',
                 'fg_music': ['audio/electro_support.wav', 'audio/electro_main.wav'],
                 'bpm': 110,
                 'lanes': 2},
]

class AudioController(object):
    def __init__(self, level = 0, bpm = 120, elements = [], beat_callback = None):
        self.mode = 'exploration'
        self.level = level
        self.level_music = level_map[self.level]
        self.level_puzzle = puzzle_map[self.level]

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

        # Exploration
        #############

        # create generators
        self.bg_gen = WaveGenerator(WaveFile(self.level_music['bg_music']), True)
        self.bg_gen.set_gain(0.3)
        self.fg_gen = WaveGenerator(WaveFile(self.level_music['fg_music']), True)
        self.fg_gen.set_gain(0)

        # add generators to mixer
        self.mixer.add(self.sched)
        self.mixer.add(self.bg_gen)
        self.mixer.add(self.fg_gen)

        # keeping track of ticks
        self.walk_ticks = set()
        self.object_ticks = {}

        # beat tracking
        self.beat = 0
        self.beat_callback = beat_callback

        # times of player moves
        self.move_times = []
        self.fg_gain = 0.5

        # Puzzle
        ########
        self.lane = 0
        self.solved = False

        # create generators
        self.puzzle_gens = []
        for index, fg_track in enumerate(self.level_puzzle['fg_music']):
            file = WaveFile(fg_track)
            gen = WaveGenerator(file, True)
            gen.pause()
            gen.set_gain(1)

            # tot num frames in generator
            data = file.get_frames(0, 1000000000)
            tot_frames = len(data) // 2 # for stereo

            rand_offset = random.randint(-4, 3)
            if rand_offset < 0:
                rand_offset -= 2
            else:
                rand_offset += 3
            self.puzzle_gens.append({'generator': gen, 'frames': tot_frames, 'lane': index, 'offset': rand_offset, 'started': False})

        # frames per offset
        self.frames_per_frac_beat = int(44100 / (2 * self.bpm / 60))

        self.play_ticks = {}


    def change_game_modes(self, mode):
        self.mode = mode

        if mode == 'exploration':
            self.move_times = []
            self.walk_ticks = set()
            self.object_ticks = {}

            # add generators to mixer
            self.mixer.add(self.sched)
            self.mixer.remove(self.bg_gen)
            self.mixer.add(self.bg_gen)
            self.mixer.add(self.fg_gen)

            self.bg_gen.set_gain(0.3)

        if mode == 'puzzle':
            self.play_ticks = {}

            self.mixer.remove(self.fg_gen)
            self.bg_gen.set_gain(0.5)

            now = self.sched.get_tick()
            next_downbeat = quantize_tick_up(now, self.note_grid * 16)

            for gen_props in self.puzzle_gens:
                play_tick = next_downbeat - gen_props['offset'] * self.note_grid/2
                if play_tick < now:
                    play_tick += self.note_grid*16

                self.play_ticks[gen_props['lane']] = play_tick
                self.sched.post_at_tick(self.play_track, play_tick, gen_props)


    ####################
    # Exploration Mode #
    ####################

    def get_key(self):
        key_gen = WaveGenerator(WaveFile(self.level_music['key_sfx']))
        key_gen.set_gain(0.15)
        self.mixer.add(key_gen)

    def jump(self):
        jump_gen = WaveGenerator(WaveFile(self.level_music['jump_sfx']))
        jump_gen.set_gain(0.6)
        self.mixer.add(jump_gen)

    def walk_once(self, tick, ignore):
        if tick in self.walk_ticks:
            walk_gen = WaveGenerator(WaveFile(self.level_music['walk_sfx']))
            walk_gen.set_gain(0.5)
            self.mixer.add(walk_gen)
            self.walk_ticks.remove(tick)

    def object_sound(self, tick, object_props):
        index, sound = object_props
        if tick in self.object_ticks[index]:
            obj_gen = WaveGenerator(WaveFile(sound))
            obj_gen.set_gain(self.object_ticks[index][tick])
            self.mixer.add(obj_gen)
            self.object_ticks.pop(index)


    ###############
    # Puzzle Mode #
    ###############

    def play_track(self, tick, gen_props):
        if gen_props['lane'] in self.play_ticks and self.play_ticks[gen_props['lane']] == tick and not gen_props['started']:
            self.mixer.add(gen_props['generator'])
            gen_props['generator'].play()
            gen_props['started'] = True
            self.play_ticks.pop(gen_props['lane'])


    #############
    # All Modes #
    #############

    def on_key_down(self, keycode):
        if self.mode == 'exploration':
            if keycode in ['left', 'right', 'spacebar']:
                self.move_times.append(self.sched.get_tick())
        
        if self.mode == 'puzzle':
            if not self.solved:
                # change lanes
                if keycode == 'up':
                    self.lane = max(0, self.lane - 1)
                if keycode == 'down':
                    self.lane = min(len(self.puzzle_gens), self.lane + 1)

                # shift selected track
                if keycode == 'left':
                    offset = self.puzzle_gens[self.lane]['offset']
                    gen = self.puzzle_gens[self.lane]['generator']
                    tot_frames = self.puzzle_gens[self.lane]['frames']

                    current_frame = gen.frame
                    gen.frame = (current_frame - self.frames_per_frac_beat) % tot_frames

                    self.puzzle_gens[self.lane]['offset'] = offset - 1

                if keycode == 'right':
                    offset = self.puzzle_gens[self.lane]['offset']
                    gen = self.puzzle_gens[self.lane]['generator']
                    tot_frames = self.puzzle_gens[self.lane]['frames']

                    current_frame = gen.frame
                    gen.frame = (current_frame + self.frames_per_frac_beat) % tot_frames

                    self.puzzle_gens[self.lane]['offset'] = offset + 1
                    


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

        # Exploration Mode
        ##################
        if self.mode == 'exploration':
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
                for move in self.move_times[-3:]:
                    quantized_move = quantize_tick_up(move, self.note_grid/2)
                    if not (quantized_move - move < 60 or move - (quantized_move - self.note_grid/2) < 120):
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
                # max gain 0.8
                # you start hearing things when you're less than 16 dist away
                gain = 0.2 * max(0, (14 - dist)) / 14
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
                    if index not in self.object_ticks:
                        self.object_ticks[index] = {}

                    if next_tick not in self.object_ticks[index]:
                        self.sched.post_at_tick(self.object_sound, next_tick, (index, obj_sound))

                    self.object_ticks[index][next_tick] = gain

        # Puzzle Mode
        #############
        if self.mode == 'puzzle':
            solved = True
            for gen_props in self.puzzle_gens:
                if gen_props['offset'] % 32 != 0:
                    solved = False
            self.solved = solved