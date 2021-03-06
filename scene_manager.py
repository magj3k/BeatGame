from audio_controller import *
from core import *
from objects import *
from kivy.graphics.instructions import InstructionGroup
import numpy as np
from math import *
import random
import copy
import sys

class SceneManager(InstructionGroup):
    def __init__(self, scenes = [], initial_scene_index = 0):
        super(SceneManager, self).__init__()
        self.fade_rect_added = False
        self.fade_rect = Rectangle(size = (actual_window_size[0]*retina_multiplier, actual_window_size[1]*retina_multiplier), pos = (0, 0))
        self.fade_color = Color(0, 0, 0)
        self.fading = "in" # or "out"

        self.original_scenes = scenes[:]
        self.scenes = scenes[:]
        self.current_scene_index = -1
        self.switch_to_scene(initial_scene_index)

    def on_multi_key_down(self, keys):
        if len(self.scenes) > self.current_scene_index:
            current_scene = self.scenes[self.current_scene_index]
            if current_scene.audio_controller != None:
                current_scene.audio_controller.on_multi_key_down(keys)

    def on_key_down(self, key): # for audio controller
        if len(self.scenes) > self.current_scene_index:
            current_scene = self.scenes[self.current_scene_index]
            if current_scene.audio_controller != None:
                current_scene.audio_controller.on_key_down(key)

    def on_key_up(self, key): # for audio controller
        if len(self.scenes) > self.current_scene_index:
            current_scene = self.scenes[self.current_scene_index]
            if current_scene.audio_controller != None:
                current_scene.audio_controller.on_key_up(key)

    def remove_current_scene(self):
        self.scenes[self.current_scene_index].clear()
        self.remove(self.scenes[self.current_scene_index])

    def switch_to_scene(self, scene_index):
        if len(self.scenes) > scene_index and scene_index > self.current_scene_index:
            self.add(self.scenes[scene_index])
            self.current_scene_index = scene_index
            if self.fade_rect_added != False:
                self.remove(self.fade_color)
                self.remove(self.fade_rect)
                self.fade_rect_added = False

            # fades in
            self.fading = "in"
            if self.fade_rect_added == False:
                self.add(self.fade_color)
                self.add(self.fade_rect)
                self.fade_rect_added = True

    def on_update(self, dt, active_keys):

        # fading
        if self.fading == "in":
            self.fade_color.a = self.fade_color.a*0.986
            if self.fade_color.a < 0.005 and self.fade_rect_added == True:
                self.remove(self.fade_rect)
                self.remove(self.fade_color)
                self.fade_rect_added = False
        else:
            self.fade_color.a = self.fade_color.a + ((1.0 - self.fade_color.a) * 3.3 * dt)
            if self.fade_rect_added == False:
                self.add(self.fade_color)
                self.add(self.fade_rect)
                self.fade_rect_added = True
            if self.fade_color.a >= 0.99 and self.fade_color.a != 1.0:
                self.fade_color.a = 1.0

                # switches to next scene
                self.remove_current_scene()
                if isinstance(self.scenes[self.current_scene_index], Menu) or isinstance(self.scenes[self.current_scene_index], Panel):
                    next_scene_index = self.scenes[self.current_scene_index].next_scene_index
                    if next_scene_index != -1:
                        self.switch_to_scene(next_scene_index)
                    elif next_scene_index == -1 or next_scene_index >= len(self.scenes):

                        # kills python program
                        sys.exit()
                else:
                    next_scene_index = self.current_scene_index+1
                    if next_scene_index >= len(self.scenes):
                        next_scene_index = 0
                    self.switch_to_scene(next_scene_index)

        if len(self.scenes) > self.current_scene_index:
            current_scene = self.scenes[self.current_scene_index]
            current_scene.on_update(dt, active_keys)

            # exits current scene
            if current_scene.scene_finished == True:
                if current_scene.audio_controller != None:
                    current_scene.audio_controller.target_mixer_gain = 0.0
                self.fading = "out"


class Scene(InstructionGroup):
    def __init__(self, initial_game_elements = [], initial_UI_elements = [], game_camera = None, ground_map = [], res = 20.0, audio_controller = None, player = None, num_keys = 3, puzzle_mode_supported = True, tag = 5):
        super(Scene, self).__init__()

        # general setup
        self.game_elements = initial_game_elements[:]
        self.queued_game_elements = []
        self.UI_elements = initial_UI_elements[:]
        self.queued_UI_elements = []
        self.game_camera = game_camera        
        self.res = res
        self.game_mode = "explore" # also "puzzle" and "fight"
        self.scene_finished = False
        self.scene_cleared = False
        self.num_keys = num_keys
        self.puzzle_mode_supported = puzzle_mode_supported
        self.tag = tag

        # sets up audio controller
        self.audio_controller = audio_controller
        if self.audio_controller != None:
            self.audio_controller.beat_callback = self.on_beat
            self.audio_controller.queue_ui_callback = self.append_ui_element
            self.audio_controller.remove_ui_callback = self.remove_ui_element
            self.audio_controller.add_fight_gem_callback = self.add_fight_gem
            self.song_length = 16 * 60 / self.audio_controller.bpm

        # player and game elements
        self.player = player
        if self.player == None: self.player = Player(res = res, initial_world_pos = (2, 6))
        self.game_elements.append(self.player.element)

        self.ground_map = ground_map
        self.objs_by_z_order_old = {}
        self.num_UI_elements_old = 0
        self.num_game_elements_old = 0

        # key collection and puzzle mode
        self.num_keys_collected = 0
        self.puzzle_key_initial_offsets = []
        self.puzzle_solved_timer = 0
        self.puzzle_solved_started = False
        self.puzzle_solved_animation_duration = 0
        self.puzzle_solved_door_front_created = False

        # fights
        self.fight_enemy = None
        self.fight_t = 0
        self.fight_enemy_sword = None
        self.fight_player_sword = None
        self.fight_end_timer = -1

    def clear(self): # called when the scene is finished and faded out

        # resets UI keys
        for element in self.UI_elements:
            if element.tag[:2] == "k_":
                if element.tag[2] == '1':
                    element.tag = "k_1"
                    element.change_texture("graphics/key_outline.png")
                    element.target_pos = None
                    element.target_size = None
                    element.z = 10
                    element.size = (166*0.2, 400*0.2)
                    element.pos = (window_size[0]-45, window_size[1]-65)
                elif element.tag[2] == '2':
                    element.tag = "k_2"
                    element.change_texture("graphics/key_outline.png")
                    element.target_pos = None
                    element.target_size = None
                    element.z = 10
                    element.size = (166*0.2, 400*0.2)
                    element.pos = (window_size[0]-95, window_size[1]-65)
                elif element.tag[2] == '3':
                    element.tag = "k_3"
                    element.change_texture("graphics/key_outline.png")
                    element.target_pos = None
                    element.target_size = None
                    element.z = 10
                    element.size = (166*0.2, 400*0.2)
                    element.pos = (window_size[0]-145, window_size[1]-65)

        self.scene_cleared = True
        self.player = None
        self.game_elements = []
        self.UI_elements = []
        self.game_camera = None
        self.ground_map = []
        self.audio_controller = None

    def change_game_modes(self, new_mode):
        if new_mode != self.game_mode:
            if new_mode == "explore":
                self.audio_controller.change_game_modes(new_mode)
                self.game_mode = new_mode
                
                self.game_camera.bounds_enabled = True
                self.game_camera.target_zoom_factor = self.game_camera.initial_target_zoom_factor
                self.game_camera.speed = self.game_camera.initial_speed
                self.player.controls_disabled = False
                self.player.target_world_pos = None

                # safely removes sword objects if needed
                if self.fight_player_sword != None:
                    self.fight_player_sword.target_alpha = 0.0
                    self.fight_player_sword = None
                if self.fight_enemy_sword != None:
                    self.fight_enemy_sword.target_alpha = 0.0
                    self.fight_enemy_sword = None
            elif new_mode == "puzzle_skip" and self.game_mode == "explore":
                self.game_mode = new_mode

                self.game_camera.bounds_enabled = False
                self.player.controls_disabled = True
                self.player.set_animation_state("standing")

                # updates camera
                for i in range(len(self.game_elements)):
                    element = self.game_elements[i]
                    if element.tag == "door":
                        self.game_camera.update_target((element.pos[0]/self.res, element.pos[1]/self.res))
                        self.game_camera.target_zoom_factor = 2.5
                        self.game_camera.speed = 1.4

            elif new_mode == "puzzle" and self.game_mode == "explore":
                self.audio_controller.change_game_modes(new_mode)
                self.game_mode = new_mode

                self.game_camera.bounds_enabled = False
                self.player.controls_disabled = True
                self.player.set_animation_state("standing")

                # adds UI bg
                new_bg = GeometricElement(pos = (window_size[0]*0.5, window_size[1]*0.5), tag = "UI_bg", color = Color(0, 0, 0, 0.011), z = 2, size = window_size)
                self.queued_UI_elements.append(new_bg)

                # adds mute button
                mute_button = TexturedElement(pos = (window_size[0]*0.5, window_size[1]-100),
                    z = 10,
                    size = (355*0.2, 356*0.2),
                    texture_path = "graphics/mute_on.png",
                    tag = "puzzle_mute")
                self.queued_UI_elements.append(mute_button)

                # adds gems
                gem_data = []
                colors = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
                two_keys_offset = 0
                if len(self.audio_controller.get_offsets()) == 1:
                    two_keys_offset = -176/2
                for index, gem_path in enumerate(self.audio_controller.level_puzzle['fg_gems']):
                    song_data = SongData(colors[index])
                    song_data.read_data(gem_path)

                    gem_props = {}
                    gem_props['gem_times'] = song_data.get_gem_data()
                    offset_y = 176*(-index+1) + 40 + two_keys_offset
                    gem_props['gem_y_pos'] = window_size[1]*0.43 + offset_y
                    if index == self.audio_controller.num_lanes:
                        gem_props['offset'] = 0
                    else:
                        gem_props['offset'] = self.audio_controller.puzzle_gens[index]['offset']

                    gem_data.append(gem_props)

                self.puzzle_gems = PuzzleGems(gem_data, self.audio_controller.bpm, self.audio_controller.get_song_time, self.append_ui_element, self.audio_controller.get_offsets)

                # adds lines to BG and stores key offsets
                self.puzzle_key_initial_offsets = self.audio_controller.get_offsets()
                for i in range(len(self.audio_controller.get_offsets())+1):
                    offset_y = 176*(-i+1) + 40 
                    new_line = GeometricElement(pos = (window_size[0]*0.5, window_size[1]*0.43 + offset_y + two_keys_offset), tag = "puzzle_line_"+str(i), color = Color(0.35, 0.35, 0.35, 0.0), target_alpha = 1, z = 3, size = (window_size[0], 6))
                    self.queued_UI_elements.append(new_line)

                # updates camera
                for i in range(len(self.game_elements)):
                    element = self.game_elements[i]
                    if element.tag == "door":
                        self.game_camera.update_target((element.pos[0]/self.res, element.pos[1]/self.res))
                        self.game_camera.target_zoom_factor = 2.5
                        self.game_camera.speed = 1.4

            elif new_mode == "fight" and self.game_mode == "explore" and self.fight_enemy != None:
                self.audio_controller.change_game_modes(new_mode)
                self.game_mode = new_mode

                # updates related variables
                self.fight_t = 0
                platforms = []
                for i in range(len(self.game_elements)):
                    element = self.game_elements[i]
                    if isinstance(element, Platform):
                        platforms.append(element)
                self.audio_controller.begin_fight(self.player, self.fight_enemy)

                # updates player
                self.player.controls_disabled = True
                self.player.set_animation_state("standing")
                self.player.target_world_pos = (self.player.world_pos[0]-0.25, self.player.get_highest_ground(self.ground_map, platforms)+self.player.world_size[1])
                self.player.fight_pos = self.player.target_world_pos
                
                # updates enemy
                self.fight_enemy.in_fight = True
                self.fight_enemy.target_velocity = (0, 0)
                self.fight_enemy.set_animation_state("standing")
                self.fight_enemy.target_world_pos = (self.player.target_world_pos[0]+2.0, self.player.target_world_pos[1])
                self.fight_enemy.fight_pos = self.fight_enemy.target_world_pos

                # updates camera
                self.game_camera.bounds_enabled = False
                self.game_camera.update_target( ((self.player.target_world_pos[0] + self.fight_enemy.target_world_pos[0])/2, 0.85+((self.player.target_world_pos[1] + self.fight_enemy.target_world_pos[1])/2)) )
                self.game_camera.target_zoom_factor = 5.5
                self.game_camera.speed = 4.0

                # adds UI bg
                new_bg = GeometricElement(pos = (window_size[0]*0.5, window_size[1]*0.7), tag = "UI_bg_fight", color = Color(0, 0, 0, 0.011), z = 2, size = (window_size[0], window_size[1]*0.285))
                new_bg.target_alpha = 0.5
                self.queued_UI_elements.append(new_bg)

                # adds lines to BG
                # now_bar = GeometricElement(pos = (window_size[0]*0.5, window_size[1] * 0.7), tag = "fight_now_bar", color = Color(0.1, 0.1, 0.1), z = 4, size = (39, window_size[1]*0.2))
                # self.queued_UI_elements.append(now_bar)
                for i in range(3):
                    offset_y = window_size[1]*(-i+1) * 0.07
                    new_line = GeometricElement(pos = (window_size[0]*0.5, window_size[1]*0.7 + offset_y), tag = "fight_line_"+str(i), color = Color(0.85, 0.85, 0.85, 0.0), target_alpha = 1, z = 3, size = (window_size[0], 6))
                    self.queued_UI_elements.append(new_line)

                    new_button_ind = TexturedElement(pos = (window_size[0]*0.5, window_size[1]*0.7 + offset_y),
                        z = 5,
                        size = (377*0.1, 378*0.1),
                        texture_path = "graphics/beat_"+str(i+1)+".png",
                        tag = "fight_button_indicator",
                        color = Color(1, 1, 1, 0), 
                        target_alpha = 1.0)
                    self.queued_UI_elements.append(new_button_ind)


    def on_beat(self, beat):
        for i in range(len(self.game_elements)):
            element = self.game_elements[i]

            if isinstance(element, Platform):
                quant_beat = int(beat) % 8
                if quant_beat in element.beats:
                    element.toggle_active_state()
            elif isinstance(element, Enemy):
                quant_beat = int(beat) % 2
                if quant_beat == 0:
                    element.advance_moves()
            elif isinstance(element, JumpPad):
                quant_beat = int(beat) % 8
                if quant_beat in element.beats:
                    element.toggle_active_state()

                    # boosts player upwards if close enough
                    if element.active and self.player.world_pos[0] > element.world_pos[0]-0.9 and self.player.world_pos[0] < element.world_pos[0]+0.9 and self.player.world_pos[1] <= element.initial_world_pos[1]+1 and self.player.world_pos[1] > element.initial_world_pos[1]-0.15:
                        self.player.world_vel = (self.player.world_vel[0], 36.0)
            elif isinstance(element, Spikes):
                quant_beat = int(beat) % 8
                if quant_beat in element.beats:
                    element.toggle_active_state()

    def append_ui_element(self, element):
        self.queued_UI_elements.append(element)

    def remove_ui_element(self, element_tag = None, particle_type = ""):
        for j in range(len(self.UI_elements)):
            element = self.UI_elements[j]
            if element.tag == element_tag:

                # adds particles if necessary
                if particle_type == "shoot_left":
                    element.target_alpha = 0.0
                elif particle_type == "shoot_right":
                    element.target_alpha = 0.0
                elif particle_type == "circular":
                    for i in range(6):
                        new_particle = Particle(GeometricElement(pos = element.pos,
                            vel = (random.random()*150.0 - 75.0, random.random()*150.0 - 75.0),
                            color = Color(1, 1, 1, 0.65),
                            size = (32, 32),
                            shape = Ellipse(pos = element.pos, size = (0.01, 0.01))),
                            z = 10,
                            resize_period = 0.4+(random.random()*0.7))
                        self.UI_elements.append(new_particle)

                    # removes element
                    element.kill_me = True

    def add_fight_gem(self, left_or_right, lane, gem_uuid, fight_gem_data):
        if left_or_right == "left" or left_or_right == "right":
            ellipse = Ellipse(size=(0.01, 0.01))
            color = Color(fight_gem_data[lane-1]['color'][0], fight_gem_data[lane-1]['color'][1], fight_gem_data[lane-1]['color'][2])
            size = fight_gem_data[lane-1]['size']
            pos = (0, fight_gem_data[lane-1]['y_pos'])
            z = 7
            if left_or_right == "left":
                pos = (window_size[0], fight_gem_data[lane-1]['y_pos'])
                z = 6
            print(pos)
            gem_element = GeometricElement(pos=pos, tag = gem_uuid, color = color, z = z, size = (size, size), shape = ellipse)
            self.queued_UI_elements.append(gem_element)

    def on_update(self, dt, active_keys):
        if self.scene_cleared == False:

            # dev, flight mode
            # if active_keys['4'] == True:
            #     self.player.flight_enabled = not self.player.flight_enabled

            # adds queued objects
            for elm in self.queued_UI_elements:
                self.UI_elements.append(elm)
            for elm in self.queued_game_elements:
                self.game_elements.append(elm)
            self.queued_UI_elements = []
            self.queued_game_elements = []

            # gets important camera information
            camera_scalar = None
            ref_camera_scalar = None
            camera_offset = None # in world units
            if self.game_camera != None:
                self.game_camera.on_update(dt)

                camera_scalar = self.game_camera.zoom_factor * screen_dilation
                ref_camera_scalar = self.game_camera.initial_target_zoom_factor * screen_dilation
                camera_offset = (-self.game_camera.world_focus[0]*camera_scalar*retina_multiplier*self.res+(actual_window_size[0]*0.5*retina_multiplier), -self.game_camera.world_focus[1]*camera_scalar*retina_multiplier*self.res+(actual_window_size[1]*0.5*retina_multiplier))

            # puzzle mode solving
            if (self.audio_controller != None and self.audio_controller.solved == True) or self.game_mode == "puzzle_skip":
                self.puzzle_solved_timer += dt
                if self.puzzle_solved_started != True:
                    self.puzzle_solved_started = True
                    self.puzzle_solved_animation_duration = 5.5
                    self.player.collisions_enabled = False

                    # creates particle effects
                    if self.game_mode == "puzzle":
                        for i in range(len(self.UI_elements)):
                            element = self.UI_elements[i]
                            if element.tag[:2] == "k_" and element.target_pos != None:
                                for i in range(7):
                                    new_particle = Particle(GeometricElement(pos = element.target_pos,
                                        vel = (random.random()*300.0 - 150.0, random.random()*300.0 - 150.0),
                                        color = Color(1, 1, 1, 0.75),
                                        size = (45, 45),
                                        shape = Ellipse(pos = element.target_pos, size = (0.01, 0.01))),
                                        z = 11,
                                        resize_period = 0.8+(random.random()*1.4))
                                    self.UI_elements.append(new_particle)
                    else:
                        self.puzzle_solved_animation_duration = 1.5

                if self.puzzle_solved_timer >= self.puzzle_solved_animation_duration:
                    self.player.set_animation_state("run_right")
                    if self.game_mode == "puzzle":
                        self.puzzle_gems.create_gems = False
                    else:
                        self.audio_controller.solved = True
                    if self.puzzle_solved_timer >= self.puzzle_solved_animation_duration+1.5:
                        self.scene_finished = True

            if self.game_mode == "puzzle":
                self.puzzle_gems.on_update(dt)

                if self.audio_controller.lane == -1:
                    self.puzzle_gems.pulsing_enabled = False
                else:
                    self.puzzle_gems.pulsing_enabled = True

            # fight mode
            if self.game_mode == "fight":
                self.fight_t += dt

                if self.fight_t > 1.25: # fight gameplay

                    # resets sword graphics
                    if self.fight_player_sword != None and self.fight_player_sword.misc_flag == True:
                        self.fight_player_sword.misc_flag = False
                        self.fight_player_sword.change_texture("graphics/sword_1_right_up.png")

                    if self.fight_enemy_sword != None and self.fight_enemy_sword.misc_flag == True:
                        self.fight_enemy_sword.misc_flag = False
                        self.fight_enemy_sword.change_texture("graphics/sword_1_left_up.png")

                    # enemy death
                    if self.fight_enemy.health <= 0 and self.fight_enemy_sword != None:
                        self.fight_end_timer = 1.75

                        # removes enemy sword
                        self.game_elements.remove(self.fight_enemy_sword)
                        self.remove(self.fight_enemy_sword.color)
                        self.remove(self.fight_enemy_sword.shape)
                        self.fight_enemy_sword = None

                        # creates key if applicable
                        if self.fight_enemy.has_key == True:
                            self.fight_enemy.has_key = False

                            new_key = Pickup(TexturedElement(pos = (self.fight_enemy.world_pos[0]*self.res, (self.fight_enemy.world_pos[1] + 0.8)*self.res),
                                size = (166*0.091, 400*0.091),
                                texture_path = "graphics/key.png"), z = 110, radius = 20)
                            new_key.element.target_alpha = 1.0
                            new_key.element.color.a = 0
                            new_key.element.size = (0.01, 0.01)
                            self.queued_game_elements.append(new_key)

                    # player death
                    if self.player.health <= 0 and self.fight_player_sword != None:
                        self.fight_end_timer = 1.75

                        # removes player sword
                        self.game_elements.remove(self.fight_player_sword)
                        self.remove(self.fight_player_sword.color)
                        self.remove(self.fight_player_sword.shape)
                        self.fight_player_sword = None

                        # creates particles
                        for i in range(12):
                            new_particle = Particle(GeometricElement(pos = self.player.element.pos,
                                vel = (random.random()*100.0 - 50.0, random.random()*65.0 - 15.0),
                                color = Color(0, 0, 0),
                                size = (30, 30),
                                shape = Ellipse(pos = self.player.element.pos, size = (0.01, 0.01))),
                                z = self.player.z,
                                resize_period = 0.5+(random.random()*1.6))
                            self.game_elements.append(new_particle)

                    # fight end timer
                    if self.fight_end_timer > 0:
                        self.audio_controller.fighting_enabled = False
                        self.fight_end_timer += -dt
                    elif self.fight_end_timer != -1:
                        self.fight_end_timer = -1
                        self.player.sword = None
                        self.change_game_modes("explore")

                        # respawns player if necessary
                        if self.player.health <= 0:
                            self.player.world_pos = self.player.initial_world_pos
                            self.player.reset_health()
                            self.player.fight_hit_animation_t = 0

                            # resets enemy
                            self.fight_enemy.in_fight = False
                            self.fight_enemy.target_world_pos = None
                            self.fight_enemy.sword = None

                elif self.fight_t > 0.9: # creates swords
                    if self.fight_player_sword == None:
                        self.fight_player_sword = TexturedElement(pos = ((self.player.world_pos[0]+0.5)*self.res, self.player.world_pos[1]*self.res),
                            z = self.player.z+1,
                            size = (500*0.1, 500*0.1),
                            color = Color(1, 1, 1, 0),
                            target_alpha = 1.0,
                            texture_path = "graphics/sword_1_right_up.png",
                            tag = "sword_player")
                        self.game_elements.append(self.fight_player_sword)
                        self.player.sword = self.fight_player_sword
                    if self.fight_enemy_sword == None and self.fight_enemy != None:
                        self.fight_enemy_sword = TexturedElement(pos = ((self.fight_enemy.world_pos[0]-0.5)*self.res, self.fight_enemy.world_pos[1]*self.res),
                            z = self.fight_enemy.z-1,
                            size = (500*0.1, 500*0.1),
                            color = Color(1, 1, 1, 0),
                            target_alpha = 1.0,
                            texture_path = "graphics/sword_1_left_up.png",
                            tag = "sword_enemy")
                        self.game_elements.append(self.fight_enemy_sword)
                        self.fight_enemy.sword = self.fight_enemy_sword

            # loops over all objects in the current scene for rendering based on z positions
            objs_by_z_order = {} # tracks objects by non-zero z-order
            max_game_z = 0
            object_indices_to_remove = [] # tracks which objcets need to be deleted
            UI_indices_to_remove = []
            platforms = []
            door = None
            door_warning = None
            for k in range(len(self.game_elements)):
                element = self.game_elements[k]
                element.on_update(dt, ref_camera_scalar, camera_scalar, camera_offset)

                # collisions w/ pickups and enemies
                if isinstance(element, Pickup) or isinstance(element, Enemy):
                    hypo = np.sqrt(np.power(element.element.pos[0] - self.player.world_pos[0]*self.res, 2.0) + np.power(element.element.pos[1] - self.player.world_pos[1]*self.res, 2.0))
                    if hypo < element.radius and self.game_mode == "explore":
                        if isinstance(element, Pickup): # pickups
                            object_indices_to_remove.append(k)
                            self.num_keys_collected += 1
                            self.audio_controller.get_key()

                            # creates particles
                            for i in range(7):
                                new_particle = Particle(GeometricElement(pos = element.element.pos,
                                    vel = (random.random()*150.0 - 75.0, random.random()*150.0 - 75.0),
                                    color = Color(1, 0.9, 0.7),
                                    size = (16, 16),
                                    shape = Ellipse(pos = element.element.pos, size = (0.01, 0.01))),
                                    z = self.player.z-1,
                                    resize_period = 0.5+(random.random()*0.8))
                                self.game_elements.append(new_particle)
                        elif isinstance(element, Enemy) and self.player.world_vel[1] > -0.95 and self.player.world_vel[1] < 0.3: # enemies
                            # enters fight mode
                            self.fight_enemy = element
                            self.change_game_modes("fight")

                # spikes
                if isinstance(element, Spikes):

                    # damages player if nearby
                    if self.player.fight_hit_animation_t <= 0 and element.active and self.player.world_pos[0] > element.world_pos[0]-0.95 and self.player.world_pos[0] < element.world_pos[0]+0.95 and self.player.world_pos[1] <= element.initial_world_pos[1]+1.05 and self.player.world_pos[1] > element.initial_world_pos[1]-0.15:
                        self.player.hit(False)

                        if self.player.health <= 0:

                            # creates particles
                            for i in range(12):
                                new_particle = Particle(GeometricElement(pos = self.player.element.pos,
                                    vel = (random.random()*100.0 - 50.0, random.random()*65.0 - 15.0),
                                    color = Color(0, 0, 0),
                                    size = (30, 30),
                                    shape = Ellipse(pos = self.player.element.pos, size = (0.01, 0.01))),
                                    z = self.player.z,
                                    resize_period = 0.5+(random.random()*1.6))
                                self.game_elements.append(new_particle)

                            self.player.world_pos = (self.player.initial_world_pos[0], 40.0)
                            self.player.reset_health()
                            self.player.fight_hit_animation_t = 0
                            self.spawning_freeze = True

                        else:
                            x_vel = 15.0
                            if self.player.world_pos[0] < element.world_pos[0]:
                                x_vel = -15.0
                            self.player.world_vel = (self.player.world_vel[0], 18.0)
                            self.player.world_vel_temp = (x_vel, 0.0)

                # enemies
                if isinstance(element, Enemy):
                    if element.health <= 0:
                        object_indices_to_remove.append(k)
                                
                        # creates particles
                        for i in range(12):
                            new_particle = Particle(GeometricElement(pos = element.element.pos,
                                vel = (random.random()*100.0 - 50.0, random.random()*65.0 - 15.0),
                                color = Color(0, 0, 0),
                                size = (30, 30),
                                shape = Ellipse(pos = element.element.pos, size = (0.01, 0.01))),
                                z = element.z,
                                resize_period = 0.5+(random.random()*1.6))
                            self.game_elements.append(new_particle)

                # platforms
                if isinstance(element, Platform):
                    platforms.append(element)

                # door
                if element.tag == "door":
                    door = element
                    if self.audio_controller.solved == True:
                        door.change_texture("graphics/door_open.png")

                        if self.puzzle_solved_door_front_created == False:
                            self.puzzle_solved_door_front_created = True

                            door_front = TexturedElement(pos = door.pos,
                                z = 112,
                                size = door.size,
                                texture_path = "graphics/door_open_front.png",
                                tag = "door_front")
                            self.queued_game_elements.append(door_front)

                # door warning
                if element.tag == "door_warning":
                    door_warning = element
                elif element.tag != "player": # removes invisible objects
                    if element.color.a < 0.01:
                        object_indices_to_remove.append(k)

                # particles
                if element.tag == "particle":
                    if element.kill_me == True:
                        object_indices_to_remove.append(k)

                # tracks objects by z-order
                max_game_z = max(max_game_z, element.z)
                if element.z not in objs_by_z_order:
                    objs_by_z_order[element.z] = [k]
                else:
                    objs_by_z_order[element.z].append(k)

            for j in range(len(self.UI_elements)):
                element = self.UI_elements[j]
                element.on_update(dt, 1.0, screen_dilation, (0, 0))

                # removes gems if flagged to kill
                if element.tag[:10] == "fight_gem_":
                    if element.kill_me == True or (element.target_alpha == 0.0 and element.color.a < 0.05):
                        element.color.a = 0
                        UI_indices_to_remove.append(j)

                # updating collected keys
                if (element.tag == "k_1" and self.num_keys_collected >= 1) or (element.tag == "k_2" and self.num_keys_collected >= 2) or (element.tag == "k_3" and self.num_keys_collected >= 3):
                    element.change_texture("graphics/key.png")
                    element.tag = element.tag+"x"
                if self.audio_controller != None and len(self.audio_controller.get_offsets()) == 1 and element.tag == "k_3":
                    element.color.a = 0

                # updates key bg
                if element.tag == "keys_bg":
                    if len(self.audio_controller.get_offsets()) == 1:
                        element.pos = (window_size[0]-16, element.pos[1])
                    else:
                        element.pos = (window_size[0]-66, element.pos[1])

                # particles
                if element.tag == "particle":
                    if element.kill_me == True:
                        UI_indices_to_remove.append(j)

                # health UI elements
                if element.tag[:2] == "h_":
                    if self.game_mode == "fight":
                        if element.tag[:4] == "h_bg": # bg
                            element.target_alpha = 0.5
                        else: # hearts
                            element.target_alpha = 1.0
                            if element.tag[:6] == "h_bar_":
                                if element.tag[-1] == "e": # enemy health
                                    health_coeff = (self.fight_enemy.health/self.fight_enemy.max_health)
                                    element.target_size = (element.initial_size[0]*health_coeff, element.initial_size[1])
                                    element.target_pos = (element.initial_pos[0]+((1-health_coeff)*element.initial_size[0]*0.5), element.initial_pos[1])
                                else: # player health
                                    health_coeff = (self.player.health/self.player.max_health)
                                    element.target_size = (element.initial_size[0]*health_coeff, element.initial_size[1])
                                    element.target_pos = (element.initial_pos[0]-((1-health_coeff)*element.initial_size[0]*0.5), element.initial_pos[1])
                    else:
                        element.target_alpha = 0.0

                if element.tag[:11] == "fight_line_" or element.tag == "UI_bg_fight" or element.tag == "fight_button_indicator":
                    if self.game_mode != "fight":
                        element.target_alpha = 0.0
                        if element.color.a <= 0.05:
                            UI_indices_to_remove.append(j)

                # puzzle mode
                if self.game_mode == "puzzle":

                    if element.tag == "gem":
                        element.pos = (element.pos[0] - window_size[0] * dt/(self.song_length/2), element.pos[1])
                        if element.pos[0] < -50:
                            UI_indices_to_remove.append(j)

                        if self.audio_controller.lane == -1:
                            element.target_alpha = 0.5
                        else:
                            element.target_alpha = 1.0

                    if self.audio_controller != None and len(self.audio_controller.get_offsets()) == 2:
                        if element.tag == "k_1x":
                            offset = (self.audio_controller.get_offsets()[0] - self.puzzle_key_initial_offsets[0]) * window_size[0]/16
                            element.target_pos = (window_size[0]*0.25 + offset, window_size[1]*0.43 + 176)
                            element.target_size = (166*0.34, 400*0.34)
                        elif element.tag == "k_2x":
                            offset = (self.audio_controller.get_offsets()[1] - self.puzzle_key_initial_offsets[1]) * window_size[0]/16
                            element.target_pos = (window_size[0]*0.25 + offset, window_size[1]*0.43)
                            element.target_size = (166*0.34, 400*0.34)
                        elif element.tag == "k_3x":
                            offset = 0
                            element.target_pos = (window_size[0]*0.25 + offset, window_size[1]*0.43 - 176)
                            element.target_size = (166*0.34, 400*0.34)
                    elif self.audio_controller != None and len(self.audio_controller.get_offsets()) == 1:
                        if element.tag == "k_1x":
                            offset = (self.audio_controller.get_offsets()[0] - self.puzzle_key_initial_offsets[0]) * window_size[0]/16
                            element.target_pos = (window_size[0]*0.25 + offset, window_size[1]*0.43 + 176 - (176/2))
                            element.target_size = (166*0.34, 400*0.34)
                        elif element.tag == "k_2x":
                            offset = 0
                            element.target_pos = (window_size[0]*0.25 + offset, window_size[1]*0.43 - (176/2))
                            element.target_size = (166*0.34, 400*0.34)
                    
                    if self.audio_controller.solved == False:
                        if element.tag == "keys_bg":
                            element.target_alpha = 0.0
                        elif element.tag == "UI_bg":
                            element.target_alpha = 0.8

                        # keys
                        if element.tag[:2] == "k_":
                            if element.tag == "k_"+str(self.audio_controller.lane + 1)+"x":
                                element.change_texture("graphics/key_selected.png")
                            else:
                                element.change_texture("graphics/key.png")

                        # bg lines
                        if element.tag[:12] == "puzzle_line_":
                            if element.tag == "puzzle_line_"+str(self.audio_controller.lane):
                                element.target_alpha = 1.0
                            else:
                                element.target_alpha = 0.6

                        # mute button
                        if element.tag == "puzzle_mute":
                            if self.audio_controller.lane == -1:
                                element.target_alpha = 1.0
                                element.change_texture("graphics/mute_off.png")
                            else:
                                element.target_alpha = 0.5
                                element.change_texture("graphics/mute_on.png")

                    elif self.puzzle_solved_timer > self.puzzle_solved_animation_duration:
                        element.target_alpha = 0.0
                        self.game_camera.target_zoom_factor = 3.0
                    elif self.audio_controller.solved:
                        if element.tag[:12] == "puzzle_line_":
                            element.target_alpha = 1.0
                        elif element.tag[:2] == "k_":
                            element.change_texture("graphics/key.png")

                elif self.game_mode == "fight": # fight mode
                    if element.tag[:2] == "k_" or element.tag == "keys_bg":
                        element.target_alpha = 0.0

                    # FIX: move gems according to tag/uuid direction, do NOT delete
                    if element.tag[:10] == "fight_gem_":

                        # if element.tag[:10] == "right_gem_":
                        #     if element.pos[0] < window_size[0]/2 - element.size[0]:
                        #         UI_indices_to_remove.append(j)
                        #     element.pos = (element.pos[0] - window_size[0] * dt/(self.song_length/4), element.pos[1])

                        # if element.tag[:9] == "left_gem_":
                        #     if element.pos[0] > window_size[0]/2 + element.size[0]:
                        #         UI_indices_to_remove.append(j)
                        #     element.pos = (element.pos[0] + window_size[0] * dt/(self.song_length/4), element.pos[1])
                        if element.tag[-5:] == "right":
                            element.pos = (element.pos[0] + window_size[0] * dt/(self.song_length/4), element.pos[1])
                        elif element.tag[-4:] == "left":
                            element.pos = (element.pos[0] - window_size[0] * dt/(self.song_length/4), element.pos[1])

                        # removing fight gems after fight has ended
                        if self.fight_end_timer > 0:
                            element.target_alpha = 0.0
                            if element.color.a <= 0.05:
                                UI_indices_to_remove.append(j)

                elif self.game_mode == "explore": # explore mode
                    if element.tag[:2] == "k_" and element.target_alpha != 1.0:
                        element.target_alpha = 1.0

                        if self.audio_controller != None and len(self.audio_controller.get_offsets()) == 1:
                            if element.tag[:3] == "k_1":
                                element.pos = (window_size[0]-95, element.pos[1])
                            elif element.tag[:3] == "k_2":
                                element.pos = (window_size[0]-45, element.pos[1])
                        else:
                            if element.tag[:3] == "k_1":
                                element.pos = (window_size[0]-145, element.pos[1])
                            elif element.tag[:3] == "k_2":
                                element.pos = (window_size[0]-95, element.pos[1])
                            elif element.tag[:3] == "k_3":
                                element.pos = (window_size[0]-45, element.pos[1])
                    elif element.tag == "keys_bg" and element.target_alpha != 0.5:
                        element.target_alpha = 0.5
                    elif "gem" in element.tag:
                        UI_indices_to_remove.append(j)

                # tracks objects by z-order
                if element.z+100+max_game_z not in objs_by_z_order:
                    objs_by_z_order[element.z+100+max_game_z] = [j]
                else:
                    objs_by_z_order[element.z+100+max_game_z].append(j)

            # applying z-order
            all_z_orders = list(objs_by_z_order.keys())
            all_z_orders.sort()
            refresh_chained = False # should always be set to False here
            if len(self.objs_by_z_order_old.keys()) == 0: refresh_chained = True
            if self.num_game_elements_old != len(self.game_elements): refresh_chained = True
            if self.num_UI_elements_old != len(self.UI_elements): refresh_chained = True
            if self.game_mode == "fight": refresh_chained = True
            for z in all_z_orders:
                object_inds_at_z = objs_by_z_order[z]

                if refresh_chained == True or z not in self.objs_by_z_order_old.keys() or len(self.objs_by_z_order_old[z]) != len(object_inds_at_z):
                    refresh_chained = True
                    for ind in object_inds_at_z:

                        # removes and re-adds visual components to canvas
                        if z <= max_game_z:
                            obj = self.game_elements[ind]
                            if obj.shape != None:
                                self.remove(obj.color)
                                self.add(obj.color)
                                self.remove(obj.shape)
                                self.add(obj.shape)
                        else:
                            obj = self.UI_elements[ind]
                            if obj.shape != None:
                                self.remove(obj.color)
                                self.add(obj.color)
                                self.remove(obj.shape)
                                self.add(obj.shape)
            self.objs_by_z_order_old = objs_by_z_order
            self.num_game_elements_old = len(self.game_elements)
            self.num_UI_elements_old = len(self.UI_elements)

            # deletes objects
            for i in range(len(object_indices_to_remove)):
                i_2 = len(object_indices_to_remove)-1-i
                if i_2 < len(object_indices_to_remove) and object_indices_to_remove[i_2] < len(self.game_elements):
                    self.remove(self.game_elements[object_indices_to_remove[i_2]].color)
                    self.remove(self.game_elements[object_indices_to_remove[i_2]].shape)
                    del self.game_elements[object_indices_to_remove[i_2]]
            for i in range(len(UI_indices_to_remove)):
                i_2 = len(UI_indices_to_remove)-1-i
                if i_2 < len(UI_indices_to_remove) and UI_indices_to_remove[i_2] < len(self.UI_elements):
                    self.remove(self.UI_elements[UI_indices_to_remove[i_2]].color)
                    self.remove(self.UI_elements[UI_indices_to_remove[i_2]].shape)
                    del self.UI_elements[UI_indices_to_remove[i_2]]

            # updates player collisions
            override_x_velocity = None
            if self.audio_controller != None and self.audio_controller.solved and self.puzzle_solved_timer >= self.puzzle_solved_animation_duration: override_x_velocity = 3.5
            self.player.on_update(dt, self.ground_map, active_keys, camera_scalar, camera_offset, self.audio_controller, platforms, door, override_x_velocity)
            if self.game_camera != None and self.game_mode == "explore": self.game_camera.update_target(self.player.world_pos)

            # if level 5, guards against bad respawnable_x
            if self.tag == "5":
                if self.player.last_respawnable_x in [50.5, 51.5]:
                    self.player.last_respawnable_x += -3
                elif self.player.last_respawnable_x in [67.5, 68.5]:
                    self.player.last_respawnable_x += 3

            # swords
            if self.fight_player_sword != None:
                self.fight_player_sword.pos = ((self.player.world_pos[0]+0.5)*self.res, self.player.world_pos[1]*self.res)
            if self.fight_enemy_sword != None and self.fight_enemy != None:
                self.fight_enemy_sword.pos = ((self.fight_enemy.world_pos[0]-0.5)*self.res, self.fight_enemy.world_pos[1]*self.res)

            # door proximity & updates
            if door_warning != None and self.game_mode != "puzzle":
                target_warning_alpha = 0.0
                if fabs(door.pos[0] - (self.player.world_pos[0]*self.player.res)) < 105.0 and self.player.on_ground:
                    num_keys_required = 3
                    if len(self.audio_controller.get_offsets()) == 1: num_keys_required = 2
                    if self.num_keys_collected < num_keys_required:
                        target_warning_alpha = 1.0
                    else:
                        # enters puzzle mode if puzzle mode supported
                        if self.puzzle_mode_supported:
                            self.change_game_modes("puzzle")
                        else:
                            self.change_game_modes("puzzle_skip")
                door_warning.color.a = door_warning.color.a + ((target_warning_alpha - door_warning.color.a)*dt*8.0)

            # audio controller update
            if self.audio_controller != None: self.audio_controller.on_update(dt, self.player, active_keys)

    def add_UI_element(self, element):
        self.UI_elements.append(element)

    def add_game_element(self, element):
        self.game_elements.append(element)


class Menu(Scene):
    def __init__(self, initial_game_elements = [], initial_UI_elements = [], game_camera = None, ground_map = [], res = 20.0, audio_controller = None, player = None, num_options = 1, option_actions = [["", -1]]):
        Scene.__init__(self, initial_game_elements, initial_UI_elements, game_camera, ground_map, res, audio_controller, player)

        self.menu_active = True
        self.option_selected = 0
        self.num_options = num_options
        self.option_actions = option_actions # list of lists; option_actions[option_index] = [action_type, scene or menu index]
        self.initial_player_y = self.player.world_pos[1]

        # menu navigation
        self.key_listen_buffer_timer = 0

        # destination scene
        self.next_scene_index = -1

    def on_update(self, dt, active_keys):

        # menu navigation
        if self.menu_active == True:
            if self.key_listen_buffer_timer <= 0:
                self.key_listen_buffer_timer = 0

                if active_keys["up"] == True:
                    self.key_listen_buffer_timer = 0.25
                    self.option_selected += -1
                if active_keys["down"] == True:
                    self.key_listen_buffer_timer = 0.25
                    self.option_selected += 1

                if self.option_selected < 0:
                    self.option_selected = self.num_options-1
                if self.option_selected >= self.num_options:
                    self.option_selected = 0
            else:
                self.key_listen_buffer_timer += -dt

            if active_keys["enter"] == True: # selecting an option
                selected_action = self.option_actions[self.option_selected][0]
                self.key_listen_buffer_timer = 0.25
                self.menu_active = False

                if selected_action == "quit":
                    sys.exit()
                elif selected_action == "scene":
                    self.next_scene_index = int(self.option_actions[self.option_selected][1])
                    self.scene_finished = True

        # visual updates for selected option
        self.player.target_world_pos = (self.player.world_pos[0], self.initial_player_y-(self.option_selected*0.45))
        for i in range(len(self.UI_elements)):
            element = self.UI_elements[i]

            if element.tag[:7] == "option_":
                if element.tag == "option_"+str(self.option_selected+1):
                    element.target_alpha = 1.0
                else:
                    element.target_alpha = 0.5

        # normally updates elements
        super().on_update(dt, active_keys)

class Panel(Scene): # essentially just a timed story panel
    def __init__(self, game_camera = None, res = 20.0, audio_controller = None, timed_objects = None, end_time = 30.0, next_scene_index = -1, allow_key_skip = True):
        Scene.__init__(self, [], [], game_camera, None, res, audio_controller, None)
        self.player.controls_disabled = True
        self.player.collisions_enabled = False
        self.allow_key_skip = allow_key_skip

        # panel elements
        self.timed_objects = timed_objects # e.g. self.timed_objects[0] = (object, time_created, time_destroyed)
        self.timed_objects_created = ["False"]*len(self.timed_objects)
        self.end_time = end_time
        self.t = 0

        # destination scene
        self.next_scene_index = next_scene_index

    def on_update(self, dt, active_keys):
        self.t += dt

        # skip button
        if self.allow_key_skip == True:
            for key in active_keys.keys():
                if active_keys[key] == True and self.t > 0.15:
                    self.scene_finished = True

        # adds/removes timed objects
        for i in range(len(self.timed_objects)):
            obj_params = self.timed_objects[i]

            if obj_params[2] != None and self.t > obj_params[2]: # "destroys" objects
                # self.timed_objects_created[i] = False
                existing_object = obj_params[0]
                existing_object.target_alpha = 0.0
            elif self.t > obj_params[1] and self.timed_objects_created[i] != True: # creates objects
                self.timed_objects_created[i] = True
                new_object = obj_params[0]
                new_object.color.a = 0.0
                new_object.target_alpha = 1.0
                self.queued_UI_elements.append(new_object)
            elif self.t <= obj_params[1]: # object not yet created
                self.timed_objects_created[i] = False 

        # end of panel
        if self.t >= self.end_time:
            self.scene_finished = True

        # normally updates elements
        super().on_update(dt, active_keys)

class Camera(object):
    def __init__(self, initial_world_target = (0, 0), zoom_factor = 1.1, speed = 1.0, bounds = None):
        self.world_target = initial_world_target
        self.world_focus = initial_world_target
        self.initial_target_zoom_factor = zoom_factor
        self.target_zoom_factor = zoom_factor
        self.zoom_factor = zoom_factor
        self.initial_speed = speed
        self.speed = speed
        self.bounds = bounds
        self.bounds_enabled = True

        if self.bounds == None:
            self.bounds_enabled = False

    def update_target(self, new_target):
        if self.bounds_enabled:
            self.world_target = (max(self.bounds[0][0], min(new_target[0], self.bounds[1][0])), max(self.bounds[0][1], min(new_target[1], self.bounds[1][1])))
        else:
            self.world_target = (new_target[0], new_target[1])

    def on_update(self, dt):
        self.zoom_factor = max(0.5, self.zoom_factor + ((self.target_zoom_factor - self.zoom_factor)* dt * self.speed))
        self.world_focus = (self.world_focus[0] + ((self.world_target[0] - self.world_focus[0])  * dt * self.speed), self.world_focus[1] + ((self.world_target[1] - self.world_focus[1]) * dt * self.speed))

