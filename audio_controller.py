from core import *
from audio.audio import *
from audio.clock import *
from audio.mixer import *
from audio.wavegen import *
from audio.wavesrc import *
from objects import *
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
                 'fg_gems': ['audio/electro_support_gems.txt', 'audio/electro_main_gems.txt', 'audio/electro_bg_gems.txt'],
                 'bpm': 110,
                 'lanes': 2},
]
fight_map = [
                {'right_sfx': ['audio/jump_sound.wav', 'audio/snare.wav', 'audio/snare.wav'],
                 'left_sfx': ['audio/walk_sound.wav', 'audio/platform_sfx.wav', 'audio/platform_sfx.wav'],
                 'left_beats': [0],
                 'right_beats': [4],
                 'miss_sfx': 'audio/error_sound.wav',
                 'hit_sfx': 'audio/key_sfx.wav',
                 'block_sfx': 'audio/droplet.wav',
                 'lanes': 3},
]

class AudioController(object):
    def __init__(self, level = 0, bpm = 120, elements = [], beat_callback = None, queue_ui_callback = None):
        self.mode = 'explore'
        self.level = level
        self.level_music = level_map[self.level]
        self.level_puzzle = puzzle_map[self.level]
        self.level_fight = fight_map[self.level]

        self.bpm = self.level_music['bpm']
        self.note_grid = 480

        self.musical_elements = []
        for el in elements:
            if el.musical:
                self.musical_elements.append(el)

        # create Audio, Mixer
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.mixer_gain = 0.0
        self.target_mixer_gain = 0.7
        # self.mixer.set_gain(self.mixer_gain)
        self.audio.set_generator(self.mixer)

        # create TempoMap, AudioScheduler
        self.tempo_map  = SimpleTempoMap(self.bpm)
        self.sched = AudioScheduler(self.tempo_map)

        # callbacks
        self.queue_ui_callback = queue_ui_callback

        # beat tracking
        self.beat = 0
        self.half_beat = 0
        self.beat_callback = beat_callback
        self.song_time = 0

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

        # times of player moves
        self.move_times = []
        self.fg_gain = 0.5

        # Puzzle
        ########
        self.lane = 0
        self.num_lanes = self.level_puzzle['lanes']
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

            rand_offset = random.randint(-8, -2)
            # if rand_offset < 0:
            #     rand_offset -= 2
            # else:
            #     rand_offset += 1
            self.puzzle_gens.append({'generator': gen, 'frames': tot_frames, 'lane': index, 'offset': rand_offset, 'started': False})

        # frames per offset
        self.frames_per_frac_beat = int(44100 / (2 * self.bpm / 60))

        self.play_ticks = {}

        # Fight
        #######
        # self.fight_gems = FightGems(fight_data, self.bpm, self.get_song_time, self.queue_ui_callback)
        self.fight_lanes = self.level_fight['lanes']
        self.fight_gems = []
        self.fight_gem_data = [
                                {'color': Color(1, 0.1, 0.1),
                                 'size': 39,
                                 'y_pos': window_size[1]*0.6 - 0.07 * window_size[1]},
                                {'color': Color(0.1, 1, 0.1),
                                 'size': 39,
                                 'y_pos': window_size[1]*0.6},
                                {'color': Color(0.1, 0.1, 1),
                                 'size': 39,
                                 'y_pos': window_size[1]*0.6 + 0.07 * window_size[1]},
        ]

    def change_game_modes(self, mode):
        self.mode = mode

        if mode == 'explore':
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

            if self.fg_gen in self.mixer.generators:
                self.mixer.remove(self.fg_gen)
            self.bg_gen.set_gain(0.5)

            now = self.sched.get_tick()
            next_downbeat = quantize_tick_up(now, self.note_grid * 16)

            play_now = True
            for gen_props in self.puzzle_gens:
                play_tick = next_downbeat - gen_props['offset'] * self.note_grid/2
                if play_tick - now < self.note_grid * 7:
                    play_now = False

            for gen_props in self.puzzle_gens:
                play_tick = next_downbeat - gen_props['offset'] * self.note_grid/2
                if not play_now:
                    play_tick += self.note_grid*16

                self.play_ticks[gen_props['lane']] = play_tick
                self.sched.post_at_tick(self.play_track, play_tick, gen_props)

        if mode == 'fight':
            if self.fg_gen in self.mixer.generators:
                self.mixer.remove(self.fg_gen)


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

    def get_offsets(self):
        offsets = [gen_props['offset'] for gen_props in self.puzzle_gens]
        return offsets

    def get_puzzle_gens(self):
        return self.puzzle_gens


    ##############
    # Fight Mode #
    ##############

    def create_right_gem(self, lane):
        # visual
        ellipse = Ellipse(size=(0.01, 0.01))
        color = self.fight_gem_data[lane-1]['color']
        size = self.fight_gem_data[lane-1]['size']
        pos = (window_size[0] + size/2, self.fight_gem_data[lane-1]['y_pos'])
        gem_element = GeometricElement(pos=pos, tag = "right_gem_" + str(lane), color = color, z = 11, size = (size, size), shape = ellipse)
        self.queue_ui_callback(gem_element)
        self.fight_gems.append(gem_element)

        # audio
        lane_sfx = WaveGenerator(WaveFile(self.level_fight['right_sfx'][lane-1]))
        self.mixer.add(lane_sfx)

    def create_left_gem(self, lane):
        ellipse = Ellipse(size=(0.01, 0.01))
        color = self.fight_gem_data[lane-1]['color']
        size = self.fight_gem_data[lane-1]['size']
        pos = (0 - size/2, self.fight_gem_data[lane-1]['y_pos'])
        gem_element = GeometricElement(pos=pos, tag = "left_gem_" + str(lane), color = color, z = 11, size = (size, size), shape = ellipse)
        self.queue_ui_callback(gem_element)
        self.fight_gems.append(gem_element)

        # audio
        lane_sfx = WaveGenerator(WaveFile(self.level_fight['left_sfx'][lane-1]))
        self.mixer.add(lane_sfx)

    def block(self, lane):
        block_sfx = WaveGenerator(WaveFile(self.level_fight['right_sfx'][lane-1]))
        self.mixer.add(block_sfx)

    def hit(self, lane):
        hit_sfx = WaveGenerator(WaveFile(self.level_fight['left_sfx'][lane-1]))
        self.mixer.add(hit_sfx)

    def miss(self):
        miss_sfx = WaveGenerator(WaveFile(self.level_fight['miss_sfx']))
        self.mixer.add(miss_sfx)

    #############
    # All Modes #
    #############

    def on_key_down(self, keycode):
        if self.mode == 'explore':
            if keycode in ['left', 'right', 'spacebar']:
                self.move_times.append(self.sched.get_tick())
        
        if self.mode == 'puzzle':
            if not self.solved:
                # change lanes
                if keycode == 'up':
                    self.lane = max(0, self.lane - 1)
                if keycode == 'down':
                    self.lane = min(self.num_lanes - 1, self.lane + 1)
                
                if not self.puzzle_gens[self.lane]['started']:
                    if keycode == 'left':
                        play_tick = self.play_ticks[self.lane] + self.note_grid/2
                        self.play_ticks[self.lane] = play_tick
                        self.sched.post_at_tick(self.play_track, play_tick, self.puzzle_gens[self.lane])
                    if keycode == 'right':
                        play_tick = self.play_ticks[self.lane] - self.note_grid/2
                        self.play_ticks[self.lane] = play_tick
                        self.sched.post_at_tick(self.play_track, play_tick, self.puzzle_gens[self.lane])
                else:
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

        if self.mode == 'fight':
            to_remove = []
            if keycode in ['1', '2', '3']:
                now_gems = []
                for gem in self.fight_gems:
                    if gem.tag[:10] == 'right_gem_' and gem.pos[0] < window_size[0] - 2:
                        self.miss()
                        to_remove.append(gem)
                    if gem.tag[:9] == 'left_gem_' and gem.pos[0] > window_size[0] + 2:
                        self.miss()
                        to_remove.append(gem)

                    if gem.pos[0] <= window_size[0] + 2 and gem.pos[0] >= window_size[0] - 2:
                        now_gems.append(gem)

                # temporal miss
                if len(now_gems) == 0:
                    self.miss()

                # hit
                for now_gem in now_gems:
                    gem_hit = False
                    if now_gem.tag[:10] == 'right_gem_':
                        if now_gem.tag[10:] == keycode:
                            self.block(int(keycode))
                            now_gem.target_size = now_gem.size
                            now_gem.size = now_gem.size + 10
                            gem_hit = True
                    if now_gem.tag[:9] == 'left_gem_':
                        if now_gem.tag[9:] == keycode:
                            self.hit(int(keycode))
                            now_gem.target_size = now_gem.size
                            now_gem.size = now_gem.size + 10
                            gem_hit = True
                    if gem_hit:
                        to_remove.append(gem)

            for gem in to_remove:
                self.fight_gems.remove(gem)

                    
    def get_song_time(self):
        return self.song_time

    def on_key_up(self, keycode):
        pass

    def on_update(self, dt, player, active_keys):
        # fading
        self.mixer_gain = self.mixer_gain + ((self.target_mixer_gain - self.mixer_gain) * dt * 3.25)
        self.mixer.set_gain(self.mixer_gain)

        self.audio.on_update()
        now = self.sched.get_tick()
        # callbacks/beat tracking
        new_beat = False
        self.song_time += dt
        if now // self.note_grid != self.beat:
            self.beat = now // self.note_grid
            if self.beat % 16 == 0:
                self.song_time = 0

        if now // (self.note_grid*0.5) != self.half_beat:
            self.half_beat = now // (self.note_grid*0.5)
            new_beat = True
            if self.beat_callback != None:
                self.beat_callback(self.half_beat)

        # Exploration Mode
        ##################
        if self.mode == 'explore':
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
                gain = 0.2 * max(0, (16 - dist)) / 16
                obj_sound = element.sound_path

                # find closest beat to now
                beats = element.beats
                prev_beat = quantize_tick_up(now, self.note_grid*4) - self.note_grid*4
                next_tick = prev_beat + 8*self.note_grid
                for beat_num in beats:
                    beat_num = beat_num / 2

                    tick = prev_beat + self.note_grid * (beat_num)
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

        # Fight Mode
        ############
        if self.mode == 'fight':
            # plus or minus 2 is hit
            if new_beat:
                for attack in self.level_fight['right_beats']:
                    if self.half_beat % 8 == attack:
                        create_bool = random.randint(0, 10) < 4
                        lane = random.randint(1, self.fight_lanes)
                        if create_bool:
                            self.create_right_gem(lane)

                for attack in self.level_fight['left_beats']:
                    if self.half_beat % 8 == attack:
                        create_bool = random.randint(0, 10) < 4
                        lane = random.randint(1, self.fight_lanes)
                        if create_bool:
                            self.create_left_gem(lane)