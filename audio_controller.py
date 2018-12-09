from core import *
from audio.audio import *
from audio.clock import *
from audio.mixer import *
from audio.wavegen import *
from audio.wavesrc import *
from objects import *
import random

level_map = [
                {'bg_music': 'audio/electro_bg.wav', # scene 0
                 'fg_music': 'audio/electro_fg.wav',
                 'jump_sfx': 'audio/jump_sound.wav',
                 'walk_sfx': 'audio/walk_sound_soft.wav',
                 'key_sfx': 'audio/key_sfx.wav',
                 'fg_gain': 0.5,
                 'bpm': 110},

                 {'bg_music': 'audio/hiphop_bg.wav', # scene 1
                 'fg_music': 'audio/silence_12s.wav',
                 'jump_sfx': 'audio/jump_sound.wav',
                 'walk_sfx': 'audio/walk_sound_soft.wav',
                 'key_sfx': 'audio/key_a_sfx.wav',
                 'fg_gain': 0,
                 'bpm': 110},

                 {'bg_music': 'audio/hiphop_bg.wav', # scene 2
                 'fg_music': 'audio/hiphop_main.wav',
                 'jump_sfx': 'audio/jump_sound.wav',
                 'walk_sfx': 'audio/walk_sound_soft.wav',
                 'key_sfx': 'audio/key_a_sfx.wav',
                 'fg_gain': 0.25,
                 'bpm': 110},

                 {'bg_music': 'audio/hiphop_bg.wav', # scene 2
                 'fg_music': 'audio/hiphop_fg.wav',
                 'jump_sfx': 'audio/jump_sound.wav',
                 'walk_sfx': 'audio/walk_sound_soft.wav',
                 'key_sfx': 'audio/key_a_sfx.wav',
                 'fg_gain': 0.25,
                 'bpm': 110},
]
puzzle_map = [
                {'bg_music': 'audio/electro_bg.wav', # scene 0
                 'fg_music': ['audio/electro_support.wav', 'audio/electro_main.wav'],
                 'fg_gems': ['audio/electro_support_gems.txt', 'audio/electro_main_gems.txt', 'audio/electro_bg_gems.txt'],
                 'bpm': 110,
                 'lanes': 2}, # number of moving lanes (not include background)

                {'bg_music': 'audio/min_bg.wav', # scene 1
                 'fg_music': ['audio/silence_12s.wav'],
                 'lanes': 0},

                {'bg_music': 'audio/hiphop_bg.wav', # scene 2
                 'fg_music': ['audio/hiphop_main.wav'],
                 'fg_gems': ['audio/hiphop_main_gems.txt', 'audio/hiphop_bg_gems.txt'],
                 'bpm': 110,
                 'lanes': 1}, # number of moving lanes (not include background)

                {'bg_music': 'audio/hiphop_bg.wav', # scene 2
                 'fg_music': ['audio/hiphop_main.wav', 'audio/hiphop_support.wav'],
                 'fg_gems': ['audio/hiphop_main_gems.txt', 'audio/hiphop_support_gems.txt', 'audio/hiphop_bg_gems.txt'],
                 'bpm': 110,
                 'lanes': 1}, # number of moving lanes (not include background)
]
fight_map = [
                {'right_sfx': ['audio/snare.wav', 'audio/snare.wav', 'audio/snare.wav'], # scene 0
                 'left_sfx': ['audio/sword.wav', 'audio/sword.wav', 'audio/sword.wav'],
                 'left_beats': [4], # eighth notes in a measure
                 'right_beats': [0], # eighth notes in a measure
                 'miss_sfx': 'audio/error_sound.wav',
                 'hit_sfx': 'audio/snare.wav',
                 'block_sfx': 'audio/sword.wav',
                 'gem_creation': (2, 10), # create if less than, out of
                 'lanes': 3},

                 {'lanes': 0}, # scene 1

                 {'right_sfx': ['audio/snare.wav', 'audio/snare.wav', 'audio/snare.wav'], # scene 2
                 'left_sfx': ['audio/sword.wav', 'audio/sword.wav', 'audio/sword.wav'],
                 'left_beats': [4], # eighth notes in a measure
                 'right_beats': [0], # eighth notes in a measure
                 'miss_sfx': 'audio/error_sound.wav',
                 'hit_sfx': 'audio/snare.wav',
                 'block_sfx': 'audio/sword.wav',
                 'gem_creation': (8, 10), # create if less than, out of
                 'lanes': 3},

                 {'right_sfx': ['audio/snare.wav', 'audio/snare.wav', 'audio/snare.wav'], # scene 3
                 'left_sfx': ['audio/sword.wav', 'audio/sword.wav', 'audio/sword.wav'],
                 'left_beats': [2, 6], # eighth notes in a measure
                 'right_beats': [0, 4], # eighth notes in a measure
                 'miss_sfx': 'audio/error_sound.wav',
                 'hit_sfx': 'audio/snare.wav',
                 'block_sfx': 'audio/sword.wav',
                 'gem_creation': (2, 10), # create if less than, out of
                 'lanes': 3},
]

class AudioController(object):
    def __init__(self, level = 0, bpm = 120, elements = [], beat_callback = None, queue_ui_callback = None, queue_ui_remove_callback = None, add_fight_gem_callback = None):
        self.mode = 'explore'
        self.level = level
        self.level_music = level_map[self.level]
        self.level_puzzle = puzzle_map[self.level]
        self.level_fight = fight_map[self.level]

        self.bpm = self.level_music['bpm']
        self.note_grid = 480

        self.musical_elements = []
        self.player = None
        for el in elements:
            if el.musical:
                self.musical_elements.append(el)
            if el.tag == 'player':
                self.player = el

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
        self.remove_ui_callback = queue_ui_remove_callback
        self.add_fight_gem_callback = add_fight_gem_callback

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
        self.fg_gain = self.level_music['fg_gain']

        # Puzzle
        ########
        self.lane = 0
        self.num_lanes = self.level_puzzle['lanes']
        self.solved = False
        self.playing_melody = False

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
        self.fighting_enabled = True
        self.fight_lanes = self.level_fight['lanes']
        self.fight_gem_tracking = {} # e.g. self.fight_gem_tracking[gem_uuid/tag] = (gem position, lane, direction, status)
        self.fight_gem_margin = 50
        self.last_gem_uuid = 0
        self.fight_keys = {'1': False, '2': False, '3': False}
        self.fight_keys_timer = 0
        self.fight_gem_data = [
                                {'color': [0.3, 0.3, 1],
                                 'size': 39,
                                 'y_pos': window_size[1]*0.7 + 0.07 * window_size[1]},
                                {'color': [0.3, 1, 0.3],
                                 'size': 39,
                                 'y_pos': window_size[1]*0.7},
                                {'color': [1, 0.3, 0.3],
                                 'size': 39,
                                 'y_pos': window_size[1]*0.7 - 0.07 * window_size[1]},
        ]
        self.current_enemy = None

    def get_new_gem_uuid_suffix(self, direction):
        self.last_gem_uuid += 1

        suffix = str(self.last_gem_uuid)
        while len(suffix) < 6:
            suffix = "0"+suffix
        return suffix+"_"+direction

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

            self.fg_gen.set_gain(0)
            self.bg_gen.set_gain(0.5)

            now = self.sched.get_tick()
            next_downbeat = quantize_tick_up(now, self.note_grid * 16)

            play_now = True
            for gen_props in self.puzzle_gens:
                play_tick = next_downbeat - gen_props['offset'] * self.note_grid/2
                if play_tick - now < self.note_grid * 8 * 0.75:
                    play_now = False

            for gen_props in self.puzzle_gens:
                play_tick = next_downbeat - gen_props['offset'] * self.note_grid/2
                if not play_now:
                    play_tick += self.note_grid*16

                self.play_ticks[gen_props['lane']] = play_tick
                self.sched.post_at_tick(self.play_track, play_tick, gen_props)

        if mode == 'fight':
            self.fighting_enabled = True
            self.fight_gem_tracking = {}


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

    def begin_fight(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def create_right_gem(self, lane):

        # visual
        # ellipse = Ellipse(size=(0.01, 0.01))
        # color = self.fight_gem_data[lane-1]['color']
        # size = self.fight_gem_data[lane-1]['size']
        # pos = (window_size[0], self.fight_gem_data[lane-1]['y_pos'])
        # gem_element = GeometricElement(pos=pos, tag = "right_gem_" + str(lane), color = color, z = 7, size = (size, size), shape = ellipse)
        # self.queue_ui_callback(gem_element)
        # self.fight_gems.append(gem_element)

        # FIX: callback to create gem in scene_manager, store unique gem id and track position in audio_controller, remove self.fight_gems
        gem_uuid = "fight_gem_"+self.get_new_gem_uuid_suffix("right")
        self.fight_gem_tracking[gem_uuid] = [0, lane, "right"]
        self.add_fight_gem_callback("right", lane, gem_uuid, self.fight_gem_data)

        # audio
        # lane_sfx = WaveGenerator(WaveFile(self.level_fight['right_sfx'][lane-1]))
        # self.mixer.add(lane_sfx)

    def create_left_gem(self, lane):
        # ellipse = Ellipse(size=(0.01, 0.01))
        # color = self.fight_gem_data[lane-1]['color']
        # size = self.fight_gem_data[lane-1]['size']
        # pos = (0, self.fight_gem_data[lane-1]['y_pos'])
        # gem_element = GeometricElement(pos=pos, tag = "left_gem_" + str(lane), color = color, z = 6, size = (size, size), shape = ellipse)
        # self.queue_ui_callback(gem_element)
        # self.fight_gems.append(gem_element)

        # FIX: callback to create gem in scene_manager, store unique gem id and track position in audio_controller, remove self.fight_gems
        gem_uuid = "fight_gem_"+self.get_new_gem_uuid_suffix("left")
        self.fight_gem_tracking[gem_uuid] = [window_size[0], lane, "left"]
        self.add_fight_gem_callback("left", lane, gem_uuid, self.fight_gem_data)

        # audio
        # lane_sfx = WaveGenerator(WaveFile(self.level_fight['left_sfx'][lane-1]))
        # self.mixer.add(lane_sfx)

    # hit right gem
    def block(self, lane):
        if self.fighting_enabled:
            # sfx
            block_sfx = WaveGenerator(WaveFile(self.level_fight['left_sfx'][lane-1]))
            block_sfx.set_gain(0.8)
            self.mixer.add(block_sfx)
            # graphics
            self.enemy.attack()
            self.player.block()

    # hit left gem
    def hit(self, lane):
        if self.fighting_enabled:
            # sfx
            hit_sfx = WaveGenerator(WaveFile(self.level_fight['right_sfx'][lane-1]))
            self.mixer.add(hit_sfx)
            # graphics
            self.player.attack()
            self.enemy.hit()

    # miss right gem
    def missed_block(self, lane, gain=1):
        if self.fighting_enabled:
            # sfx
            hit_sfx = WaveGenerator(WaveFile(self.level_fight['hit_sfx']))
            hit_sfx.set_gain(gain)
            self.mixer.add(hit_sfx)
            error_sfx = WaveGenerator(WaveFile(self.level_fight['miss_sfx']))
            self.mixer.add(error_sfx)
            # graphics
            self.enemy.attack()
            self.player.hit()

    # miss left gem
    def missed_hit(self, lane, animate = True, gain=1):
        if self.fighting_enabled:
            # sfx
            block_sfx = WaveGenerator(WaveFile(self.level_fight['block_sfx']))
            block_sfx.set_gain(0.6 * gain)
            self.mixer.add(block_sfx)
            error_sfx = WaveGenerator(WaveFile(self.level_fight['miss_sfx']))
            self.mixer.add(error_sfx)
            # graphics
            if animate:
                self.player.attack()
                self.enemy.block()

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
                    self.lane = max(-1, self.lane - 1)
                if keycode == 'down':
                    self.lane = min(self.num_lanes - 1, self.lane + 1)
                
                if self.lane == -1:
                    self.playing_melody = True
                else:
                    self.playing_melody = False
                    if not self.puzzle_gens[self.lane]['started']:
                        if keycode == 'left':
                            play_tick = self.play_ticks[self.lane] + self.note_grid/2
                            self.play_ticks[self.lane] = play_tick
                            self.sched.post_at_tick(self.play_track, play_tick, self.puzzle_gens[self.lane])

                            offset = self.puzzle_gens[self.lane]['offset']
                            self.puzzle_gens[self.lane]['offset'] = offset - 1
                        if keycode == 'right':
                            play_tick = self.play_ticks[self.lane] - self.note_grid/2
                            self.play_ticks[self.lane] = play_tick
                            self.sched.post_at_tick(self.play_track, play_tick, self.puzzle_gens[self.lane])

                            offset = self.puzzle_gens[self.lane]['offset']
                            self.puzzle_gens[self.lane]['offset'] = offset + 1
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

    def on_multi_key_down(self, keys):
        if self.mode == 'fight':
            to_remove = []
            if set(keys) <= {'1', '2', '3'} and self.fight_keys_timer <= 0:
                # self.fight_keys[keycode] = True
                self.fight_keys_timer = 0.15

                now_gems = []
                # for gem in self.fight_gems:
                #     if gem.tag[:10] == 'right_gem_':
                #         if gem.pos[0] < window_size[0]/2 + gem.size[0]*3 and gem.pos[0] >= window_size[0]/2 - gem.size[0]:
                #             now_gems.append(gem)
                #     if gem.tag[:9] == 'left_gem_':
                #         if gem.pos[0] > window_size[0]/2 - gem.size[0]*3 and gem.pos[0] <= window_size[0]/2 + gem.size[0]:
                #             now_gems.append(gem)

                # FIX: replace self.fight_gems with uuid-based position tracking dict, append uuids to now_gems
                for gem_uuid in self.fight_gem_tracking.keys():
                    gem_pos = self.fight_gem_tracking[gem_uuid][0]
                    if gem_pos <= window_size[0]/2 + self.fight_gem_margin and gem_pos >= window_size[0]/2 - self.fight_gem_margin:
                        now_gems.append(gem_uuid)

                # temporal miss
                if len(now_gems) == 0:
                    self.missed_hit(int(keys[0]))
                    return

                # hit
                gems_hit = {"right":0, "left":0}
                gems_missed = {"right":0, "left":0}
                lanes_in = set()
                # for now_gem in now_gems:
                #     gem_hit = False
                #     if now_gem.tag[:10] == 'right_gem_':
                #         if now_gem.tag[10:] == keycode:
                #             self.block(int(keycode))
                #             now_gem.target_size = now_gem.size
                #             now_gem.size = (now_gem.size[0] + gem.size[0], now_gem.size[1] + gem.size[0])
                #             gem_hit = True
                #     if now_gem.tag[:9] == 'left_gem_':
                #         if now_gem.tag[9:] == keycode:
                #             self.hit(int(keycode))
                #             now_gem.target_size = now_gem.size
                #             now_gem.size = (now_gem.size[0] + gem.size[0], now_gem.size[1] + gem.size[0])
                #             gem_hit = True
                #     if gem_hit:
                #         to_remove.append(now_gem)
                #         any_gem_hit = True

                # FIX: clean up unnecessary code and handle now_gems uuids, hit scene_manager callback for gem hit animations
                for gem_uuid in now_gems:
                    lanes_in.add(str(self.fight_gem_tracking[gem_uuid][1]))
                    # gem_hit = False
                    if str(self.fight_gem_tracking[gem_uuid][1]) in keys: # correct lane
                        # gem_hit = True

                        if gem_uuid[-5:] == "right":
                            gems_hit["right"] += 1
                        elif gem_uuid[-4:] == "left":
                            gems_hit["left"] +=1

                        to_remove.append((gem_uuid, "circular"))
                        # if gem_uuid[-5:] == "right":
                        #     self.hit(int(keycode))
                        # elif gem_uuid[-4:] == "left":
                        #     self.block(int(keycode))
                    else:
                        if gem_uuid[-5:] == "right":
                            gems_missed["right"] += 1
                            to_remove.append((gem_uuid, "shoot_right"))
                        elif gem_uuid[-4:] == "left":
                            gems_missed["left"] += 1
                            to_remove.append((gem_uuid, "shoot_left"))

                wrong_lane = True
                if set(keys) <= lanes_in:
                    wrong_lane = False
                # calculate hit or miss precendence
                # no left gems
                if gems_hit["left"] + gems_missed["left"] == 0:
                    right_hit_proportion = gems_hit["right"]/(gems_hit["right"] + gems_missed["right"])
                    if right_hit_proportion == 1 and not wrong_lane:
                        self.hit(int(keys[0]))
                    else:
                        self.missed_hit(int(keys[0]))
                # no right gems
                elif gems_hit["right"] + gems_missed["right"] == 0:
                    left_hit_proportion = gems_hit["left"]/(gems_hit["left"] + gems_missed["left"])
                    if left_hit_proportion == 1:
                        self.block(int(keys[0]))
                    else:
                        self.missed_block(int(keys[0]))
                # both gems exist
                else:
                    right_hit_proportion = gems_hit["right"]/(gems_hit["right"] + gems_missed["right"])
                    left_hit_proportion = gems_hit["left"]/(gems_hit["left"] + gems_missed["left"])
                    if right_hit_proportion == 1:
                        if left_hit_proportion == 1:
                            if not wrong_lane:
                                self.hit(int(keys[0]))
                            else:
                                self.missed_hit(int(keys[0]))
                        else:
                            self.block(int(keys[0]))
                    else:
                        if left_hit_proportion == 1:
                            self.block(int(keys[0]))
                        else:
                            self.missed_block(int(keys[0]))


                # lane miss
                # if not any_gem_hit:
                    # if now_gems[0].tag[:10] == 'right_gem_':
                    #     self.missed_block(int(now_gems[0].tag[10:]))
                    # else:
                    #     self.missed_hit(int(now_gems[0].tag[9:]))
                    # for now_gem in now_gems:
                    #     to_remove.append(now_gem)

                    # FIX: store lane in now_gems and use those to call missed_block and missed_hit
                    # for gem_uuid in now_gems:
                    #     if gem_uuid[-5:] == "right":
                    #         self.missed_block(self.fight_gem_tracking[gem_uuid][1])
                    #         to_remove.append((gem_uuid, "shoot_right"))
                    #     elif gem_uuid[-4:] == "left":
                    #         self.missed_hit(self.fight_gem_tracking[gem_uuid][1])
                    #         to_remove.append((gem_uuid, "shoot_left"))

            for gem_data in to_remove:
                gem_uuid = gem_data[0]
                particle_type = gem_data[1]
                # self.fight_gems.remove(gem)

                # FIX: add callback for scene_manager to delete gems by UUID
                self.remove_ui_callback(gem_uuid, particle_type)
                self.fight_gem_tracking.pop(gem_uuid)

                    
    def get_song_time(self):
        return self.song_time

    def on_key_up(self, keycode):
        if keycode in ['1', '2', '3'] and self.fight_keys[keycode] == True:
            self.fight_keys[keycode] = False

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
                if isinstance(element, Platform):
                    cell_bounds = element.cell_bounds
                    x_dist = min(abs(player_pos[0] - cell_bounds[0][0]), abs(player_pos[0] - cell_bounds[1][0]))
                    y_dist = min(abs(player_pos[1] - cell_bounds[0][1]), abs(player_pos[1] - cell_bounds[1][1]))
                    dist = (x_dist**2 + y_dist**2)**0.5
                    dist = max(0, dist - 2)
                    # max gain 0.2
                    # you start hearing things when you're less than 16 dist away
                    gain = 0.2 * max(0, (16 - dist)) / 16
                    obj_sound = element.sound_path
                else:
                    element_pos = element.initial_world_pos
                    x_dist = abs(player_pos[0] - element_pos[0])
                    y_dist = abs(player_pos[1] - element_pos[1])
                    dist = (x_dist**2 + y_dist**2)**0.5
                    dist = max(0, dist - 2)
                    # max gain 0.3
                    # you start hearing things when you're less than 16 dist away
                    gain = 0.3 * max(0, (16 - dist)) / 16
                    obj_sound = element.sound_path

                if gain > 0 and obj_sound:
                    # find closest beat to now
                    beats = element.beats
                    prev_beat = quantize_tick_up(now, self.note_grid*4) - self.note_grid*4
                    next_tick = prev_beat + 8*self.note_grid
                    for i, beat_num in enumerate(beats):
                        if isinstance(element, JumpPad) and i != 0:
                            continue
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
            if self.playing_melody:
                melody_target = 1
                puzzle_gens_target = 0
            else:
                melody_target = 0
                puzzle_gens_target = 1

            melody_gain = self.fg_gen.get_gain() + ((melody_target - self.fg_gen.get_gain()) * dt * 0.9)
            self.fg_gen.set_gain(melody_gain)

            for gen_props in self.puzzle_gens:
                gen_gain = gen_props['generator'].get_gain() + ((puzzle_gens_target - gen_props['generator'].get_gain()) * dt * 0.9)
                gen_props['generator'].set_gain(gen_gain)

            solved = True
            for gen_props in self.puzzle_gens:
                if gen_props['offset'] % 32 != 0:
                    solved = False
            self.solved = solved

        # Fight Mode
        ############
        if self.mode == 'fight' and self.fighting_enabled == True:
            # foreground music should turn off
            fg_gain = self.fg_gen.get_gain() + ((0 - self.fg_gen.get_gain()) * dt * 0.9)
            self.fg_gen.set_gain(fg_gain)

            # fight key timeouts
            self.fight_keys_timer += -dt
            if self.fight_keys_timer < 0:
                self.fight_keys_timer = 0

            # advances fight_gem_tracking
            song_length = 16 * 60 / self.bpm
            for gem_uuid in self.fight_gem_tracking.keys():
                if self.fight_gem_tracking[gem_uuid][2] == "right":
                    self.fight_gem_tracking[gem_uuid][0] += window_size[0] * dt/(song_length/4)
                elif self.fight_gem_tracking[gem_uuid][2] == "left":
                    self.fight_gem_tracking[gem_uuid][0] -= window_size[0] * dt/(song_length/4)

            # plus or minus 2 is hit
            if new_beat:
                create_if, out_of = self.level_fight['gem_creation']
                used_lanes = []
                for attack in self.level_fight['left_beats']:
                    if self.half_beat % 8 == attack:
                        create_bool = random.randint(0, out_of) < create_if
                        for lane in range(1, self.fight_lanes + 1):
                            use_lane = random.randint(1, self.fight_lanes) == 1
                            if create_bool and use_lane:
                                self.create_left_gem(lane)
                                used_lanes.append(lane)

                for attack in self.level_fight['right_beats']:
                    if self.half_beat % 8 == attack:
                        create_bool = random.randint(0, out_of) < create_if
                        for lane in range(1, self.fight_lanes + 1):
                            use_lane = random.randint(1, self.fight_lanes) == 1
                            if create_bool and use_lane and lane not in used_lanes:
                                self.create_right_gem(lane)
                

            to_remove = []
            # for gem in self.fight_gems:
            #     if gem.tag[:10] == 'right_gem_':
            #         if gem.pos[0] < window_size[0]/2 - gem.size[0]:
            #             self.missed_block(int(gem.tag[10:]))
            #             to_remove.append(gem)
            #     if gem.tag[:9] == 'left_gem_':
            #         if gem.pos[0] > window_size[0]/2 + gem.size[0]:
            #             self.missed_hit(int(gem.tag[9:]))
            #             to_remove.append(gem)

            # FIX: use uuid-based position gem tracking dict instead of self.fight_gems, add UUIDs to to_remove
            missed_hits = []
            missed_blocks = []
            for gem_uuid in self.fight_gem_tracking.keys():
                gem_pos = self.fight_gem_tracking[gem_uuid][0]
                if gem_uuid[-4:] == "left":
                    if gem_pos < window_size[0]/2 - self.fight_gem_margin:
                        missed_blocks.append(self.fight_gem_tracking[gem_uuid][1])
                        to_remove.append((gem_uuid, "shoot_left"))
                elif gem_uuid[-5:] == "right":
                    if gem_pos > window_size[0]/2 + self.fight_gem_margin:
                        missed_hits.append(self.fight_gem_tracking[gem_uuid][1])
                        to_remove.append((gem_uuid, "shoot_right"))

            if len(missed_hits) > 0:
                self.missed_hit(missed_hits[0], True)
            if len(missed_blocks):
                self.missed_block(missed_blocks[0])

            for gem_data in to_remove:
                gem_uuid = gem_data[0]
                particle_type = gem_data[1]
                # self.fight_gems.remove(gem)

                # FIX: add callback for scene_manager to delete gems by UUID
                self.remove_ui_callback(gem_uuid, particle_type)
                self.fight_gem_tracking.pop(gem_uuid)

