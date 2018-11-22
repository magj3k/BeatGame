from audio_controller import *
from core import *
from objects import *
from kivy.graphics.instructions import InstructionGroup
import numpy as np
from math import *
import random

class SceneManager(InstructionGroup):
    def __init__(self, scenes = [], initial_scene_index = 0):
        super(SceneManager, self).__init__()
        self.fade_rect_added = False
        self.fade_rect = Rectangle(size = (window_size[0]*retina_multiplier, window_size[1]*retina_multiplier), pos = (0, 0))
        self.fade_color = Color(0, 0, 0)
        self.fading = "in" # or "out"

        self.scenes = scenes
        self.current_scene_index = 0
        self.switch_to_scene(initial_scene_index)

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
        if len(self.scenes) > scene_index:
            self.current_scene_index = scene_index
            self.add(self.scenes[self.current_scene_index])

            if self.fade_rect_added == False:
                self.add(self.fade_color)
                self.add(self.fade_rect)
                self.fade_rect_added = True

    def on_update(self, dt, active_keys):
        # fading
        if self.fading == "in":
            self.fade_color.a = self.fade_color.a*0.982
            if self.fade_color.a < 0.005 and self.fade_rect_added == True:
                self.remove(self.fade_rect)
                self.remove(self.fade_color)
                self.fade_rect_added = False
        else:
            self.fade_color.a = self.fade_color.a + ((1.0 - self.fade_color.a) * 4.0 * dt)
            if self.fade_rect_added == False:
                self.add(self.fade_color)
                self.add(self.fade_rect)
                self.fade_rect_added = True
            if self.fade_color.a >= 0.99 and self.fade_color.a != 1.0:
                self.fade_color.a = 1.0

                # switches to next scene
                self.remove_current_scene() # TODO, follow with self.switch_to_scene
                print("Switch to next scene")


        if len(self.scenes) > self.current_scene_index:
            current_scene = self.scenes[self.current_scene_index]
            current_scene.on_update(dt, active_keys)

            # exits current scene
            if current_scene.scene_finished == True:
                self.fading = "out"


class Scene(InstructionGroup):
    def __init__(self, initial_game_elements = [], initial_UI_elements = [], game_camera = None, ground_map = [], res = 20.0, audio_controller = None, player = None):
        super(Scene, self).__init__()
        self.game_elements = initial_game_elements
        self.queued_game_elements = []
        self.UI_elements = initial_UI_elements
        self.queued_UI_elements = []
        self.game_camera = game_camera        
        self.res = res
        self.game_mode = "explore" # also "puzzle" and "fight"
        self.scene_finished = False
        self.scene_cleared = False

        # sets up audio controller
        self.audio_controller = audio_controller
        self.audio_controller.beat_callback = self.on_beat

        # game scenes
        self.player = player
        if self.player == None: self.player = Player(res = res, initial_world_pos = (2, 6))
        self.game_elements.append(self.player.element)

        self.ground_map = ground_map
        self.objs_by_z_order_old = {}

        # key collection and puzzle mode
        self.num_keys_collected = 0
        self.puzzle_key_initial_offsets = []
        self.puzzle_solved_timer = 0
        self.puzzle_solved_started = False
        self.puzzle_solved_animation_duration = 0
        self.puzzle_solved_door_front_created = False

    def clear(self):
        self.scene_cleared = True
        self.player = None
        self.game_elements = []
        self.UI_elements = []
        self.game_camera = None
        self.ground_map = []
        self.audio_controller = None

    def change_game_modes(self, new_mode):
        self.audio_controller.change_game_modes(new_mode)
        self.game_mode = new_mode
        if new_mode == "explore":
            self.game_camera.bounds_enabled = True
        elif new_mode == "puzzle":
            self.game_camera.bounds_enabled = False
            self.player.controls_disabled = True
            self.player.set_animation_state("standing")

            # adds UI bg
            new_bg = GeometricElement(pos = (window_size[0]*0.5, window_size[1]*0.5), tag = "UI_bg", color = Color(0, 0, 0, 0.011), z = 2, size = window_size)
            self.queued_UI_elements.append(new_bg)

            # adds lines to BG and stores key offsets
            self.puzzle_key_initial_offsets = self.audio_controller.get_offsets()
            for i in range(3):
                offset_y = (window_size[1]*0.22)*(-i+1)
                new_line = GeometricElement(pos = (window_size[0]*0.5, window_size[1]*0.5 + offset_y), tag = "puzzle_line_"+str(i), color = Color(0.35, 0.35, 0.35, 0.0), target_alpha = 1, z = 3, size = (window_size[0], window_size[1]*0.008))
                self.queued_UI_elements.append(new_line)

            # updates camera
            for i in range(len(self.game_elements)):
                element = self.game_elements[i]
                if element.tag == "door":
                    self.game_camera.update_target((element.pos[0]/self.res, element.pos[1]/self.res))
                    self.game_camera.target_zoom_factor = 2.5
                    self.game_camera.speed = 1.4

        elif new_mode == "fight":
            self.game_camera.bounds_enabled = False

    def on_beat(self, beat):
        for i in range(len(self.game_elements)):
            element = self.game_elements[i]

            if isinstance(element, Platform):
                element.toggle_active_state()
            elif isinstance(element, Enemy):
                element.advance_moves()

    def on_update(self, dt, active_keys):
        if self.scene_cleared == False:

            # adds queued objects
            for elm in self.queued_UI_elements:
                self.UI_elements.append(elm)
            for elm in self.queued_game_elements:
                self.game_elements.append(elm)
            self.queued_UI_elements = []
            self.queued_game_elements = []

            # gets important camera information
            camera_scalar = None
            camera_offset = None # in world units
            if self.game_camera != None:
                self.game_camera.on_update(dt)

                camera_scalar = self.game_camera.zoom_factor
                camera_offset = (-self.game_camera.world_focus[0]*camera_scalar*retina_multiplier*self.res+(window_size[0]*0.5*retina_multiplier), -self.game_camera.world_focus[1]*camera_scalar*retina_multiplier*self.res+(window_size[1]*0.5*retina_multiplier))

            # puzzle mode solving
            if self.audio_controller.solved == True:
                self.puzzle_solved_timer += dt
                if self.puzzle_solved_started != True:
                    self.puzzle_solved_started = True
                    self.puzzle_solved_animation_duration = 5.5
                    self.player.collisions_enabled = False

                    # creates particle effects
                    for i in range(len(self.UI_elements)):
                        element = self.UI_elements[i]
                        if element.tag[:2] == "k_":
                            for i in range(7):
                                new_particle = Particle(GeometricElement(pos = element.target_pos,
                                    vel = (random.random()*300.0 - 150.0, random.random()*300.0 - 150.0),
                                    color = Color(1, 1, 1, 0.75),
                                    size = (45, 45),
                                    shape = Ellipse(pos = element.target_pos, size = (0.01, 0.01))),
                                    z = 11,
                                    resize_period = 0.8+(random.random()*1.4))
                                self.UI_elements.append(new_particle)

                if self.puzzle_solved_timer >= self.puzzle_solved_animation_duration:
                    self.player.set_animation_state("run_right")
                    if self.puzzle_solved_timer >= self.puzzle_solved_animation_duration+1.5:
                        self.scene_finished = True

            # loops over all objects in the current scene for rendering based on z positions
            objs_by_z_order = {} # tracks objects by non-zero z-order
            max_game_z = 0
            object_indices_to_remove = [] # tracks which objcets need to be deleted
            UI_indices_to_remove = []
            platforms = []
            door = None
            door_warning = None
            for i in range(len(self.game_elements)):
                element = self.game_elements[i]
                element.on_update(dt, camera_scalar, camera_offset)

                # collisions w/ pickups and enemies
                if isinstance(element, Pickup) or isinstance(element, Enemy):
                    hypo = np.sqrt(np.power(element.element.pos[0] - self.player.world_pos[0]*self.res, 2.0) + np.power(element.element.pos[1] - self.player.world_pos[1]*self.res, 2.0))
                    if hypo < element.radius:
                        if isinstance(element, Pickup): # pickups
                            object_indices_to_remove.append(i)
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
                        elif isinstance(element, Enemy): # enemies
                            element.health = 0

                # enemies
                if isinstance(element, Enemy):
                    if element.health <= 0:
                        object_indices_to_remove.append(i)
                                
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
                else: # removes invisible objects
                    if element.color.a < 0.01:
                        object_indices_to_remove.append(i)

                # particles
                if element.tag == "particle":
                    if element.kill_me == True:
                        object_indices_to_remove.append(i)

                # tracks objects by z-order
                max_game_z = max(max_game_z, element.z)
                if element.z not in objs_by_z_order:
                    objs_by_z_order[element.z] = [i]
                else:
                    objs_by_z_order[element.z].append(i)

            for i in range(len(self.UI_elements)):
                element = self.UI_elements[i]
                element.on_update(dt, 1.0, (0, 0))

                # updating collected keys
                if (element.tag == "k_1" and self.num_keys_collected >= 1) or (element.tag == "k_2" and self.num_keys_collected >= 2) or (element.tag == "k_3" and self.num_keys_collected >= 3):
                    element.change_texture("graphics/key.png")
                    element.tag = element.tag+"x"

                # particles
                if element.tag == "particle":
                    if element.kill_me == True:
                        UI_indices_to_remove.append(i)

                # puzzle mode
                if self.game_mode == "puzzle":
                    if element.tag == "k_1x":
                        offset = (self.audio_controller.get_offsets()[0] - self.puzzle_key_initial_offsets[0]) * window_size[0]*0.03
                        element.target_pos = (window_size[0]*0.25 + offset, window_size[1]*(0.5+0.22))
                        element.target_size = (166*0.34, 400*0.34)
                    elif element.tag == "k_2x":
                        offset = (self.audio_controller.get_offsets()[1] - self.puzzle_key_initial_offsets[1]) * window_size[0]*0.03
                        element.target_pos = (window_size[0]*0.25 + offset, window_size[1]*(0.5+0.0))
                        element.target_size = (166*0.34, 400*0.34)
                    elif element.tag == "k_3x":
                        offset = 0
                        element.target_pos = (window_size[0]*0.25 + offset, window_size[1]*(0.5-0.22))
                        element.target_size = (166*0.34, 400*0.34)

                    if self.audio_controller.solved == False:
                        if element.tag == "keys_bg":
                            element.color.a = element.color.a*0.85
                        elif element.tag == "UI_bg":
                            element.color.a = element.color.a + ((0.8 - element.color.a) * 10.0 * dt)

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
                    elif self.puzzle_solved_timer > self.puzzle_solved_animation_duration:
                        element.target_alpha = 0.0
                        self.game_camera.target_zoom_factor = 3.0
                    elif self.audio_controller.solved:
                        if element.tag[:12] == "puzzle_line_":
                            element.target_alpha = 1.0
                        elif element.tag[:2] == "k_":
                            element.change_texture("graphics/key.png")

                # removes invisible objects
                if element.color.a < 0.01:
                    UI_indices_to_remove.append(i)

                # tracks objects by z-order
                if element.z+1+max_game_z not in objs_by_z_order:
                    objs_by_z_order[element.z+1+max_game_z] = [i]
                else:
                    objs_by_z_order[element.z+1+max_game_z].append(i)

            # applying z-order
            all_z_orders = list(objs_by_z_order.keys())
            all_z_orders.sort()
            refresh_chained = False
            if len(self.objs_by_z_order_old.keys()) == 0: refresh_chained = True
            for z in all_z_orders:
                object_inds_at_z = objs_by_z_order[z]

                # print(self.objs_by_z_order_old[z])
                if refresh_chained == True or z not in self.objs_by_z_order_old.keys() or len(self.objs_by_z_order_old[z]) != len(object_inds_at_z):
                    refresh_chained = True
                    for ind in object_inds_at_z:

                        # removes and re-adds visual components to canvas
                        if z <= max_game_z:
                            obj = self.game_elements[ind]
                            self.remove(obj.color)
                            self.add(obj.color)
                            if obj.shape != None:
                                self.remove(obj.shape)
                                self.add(obj.shape)
                        else:
                            obj = self.UI_elements[ind]
                            self.remove(obj.color)
                            self.add(obj.color)
                            if obj.shape != None:
                                self.remove(obj.shape)
                                self.add(obj.shape)
            self.objs_by_z_order_old = objs_by_z_order

            # deletes objects
            for i in range(len(object_indices_to_remove)):
                i_2 = len(object_indices_to_remove)-1-i
                self.remove(self.game_elements[object_indices_to_remove[i_2]].color)
                self.remove(self.game_elements[object_indices_to_remove[i_2]].shape)
                del self.game_elements[object_indices_to_remove[i_2]]
            for i in range(len(UI_indices_to_remove)):
                i_2 = len(UI_indices_to_remove)-1-i
                self.remove(self.UI_elements[UI_indices_to_remove[i_2]].color)
                self.remove(self.UI_elements[UI_indices_to_remove[i_2]].shape)
                del self.UI_elements[UI_indices_to_remove[i_2]]

            # updates player collisions
            override_x_velocity = None
            if self.audio_controller.solved and self.puzzle_solved_timer >= self.puzzle_solved_animation_duration: override_x_velocity = 3.5
            self.player.on_update(dt, self.ground_map, active_keys, camera_scalar, camera_offset, self.audio_controller, platforms, door, override_x_velocity)
            if self.game_camera != None and self.game_mode == "explore": self.game_camera.update_target(self.player.world_pos)

            # door proximity & updates
            if door_warning != None and self.game_mode != "puzzle":
                target_warning_alpha = 0.0
                if fabs(door.pos[0] - (self.player.world_pos[0]*self.player.res)) < 105.0:
                    if self.num_keys_collected < 3: # TODO, change to 3
                        target_warning_alpha = 1.0
                    else:
                        # enters puzzle mode
                        self.change_game_modes("puzzle")
                door_warning.color.a = door_warning.color.a + ((target_warning_alpha - door_warning.color.a)*dt*8.0)

            # audio controller update
            if self.audio_controller != None: self.audio_controller.on_update(dt, self.player, active_keys)

    def add_UI_element(self, element):
        self.UI_elements.append(element)

    def add_game_element(self, element):
        self.game_elements.append(element)


class Camera(object):
    def __init__(self, initial_world_target = (0, 0), zoom_factor = 1.1, speed = 1.0, bounds = None):
        self.world_target = initial_world_target
        self.world_focus = initial_world_target
        self.target_zoom_factor = zoom_factor
        self.zoom_factor = zoom_factor
        self.speed = speed
        self.bounds = bounds
        self.bounds_enabled = True

    def update_target(self, new_target):
        if self.bounds_enabled:
            self.world_target = (max(self.bounds[0][0], min(new_target[0], self.bounds[1][0])), max(self.bounds[0][1], min(new_target[1], self.bounds[1][1])))
        else:
            self.world_target = (new_target[0], new_target[1])

    def on_update(self, dt):
        self.zoom_factor = max(0.5, self.zoom_factor + ((self.target_zoom_factor - self.zoom_factor)* dt * self.speed))
        self.world_focus = (self.world_focus[0] + ((self.world_target[0] - self.world_focus[0])  * dt * self.speed), self.world_focus[1] + ((self.world_target[1] - self.world_focus[1]) * dt * self.speed))

