from audio import *
from core import *
from objects import *
from kivy.graphics.instructions import InstructionGroup
import numpy as np

class SceneManager(InstructionGroup):
    def __init__(self, scenes = [], initial_scene_index = 0):
        super(SceneManager, self).__init__()
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

    def switch_to_scene(self, scene_index):
        if len(self.scenes) > scene_index:
            # TODO: remove current scene before switching

            self.current_scene_index = scene_index
            self.add(self.scenes[self.current_scene_index])

    def on_update(self, dt, active_keys):
        if len(self.scenes) > self.current_scene_index:
            current_scene = self.scenes[self.current_scene_index]
            current_scene.on_update(dt, active_keys)

            # loops over all objects in the current scene for rendering based on z positions
            objs_by_z_order = {} # tracks objects by non-zero z-order
            max_game_z = 0
            for i in range(len(current_scene.game_elements)):
                element = current_scene.game_elements[i]

                # tracks objects by z-order
                max_game_z = max(max_game_z, element.z)
                if element.z not in objs_by_z_order:
                    objs_by_z_order[element.z] = [i]
                else:
                    objs_by_z_order[element.z].append(i)
            for i in range(len(current_scene.UI_elements)):
                element = current_scene.UI_elements[i]

                # tracks objects by z-order
                if element.z+1+max_game_z not in objs_by_z_order:
                    objs_by_z_order[element.z+1+max_game_z] = [i]
                else:
                    objs_by_z_order[element.z+1+max_game_z].append(i)

            # applying z-order
            all_z_orders = list(objs_by_z_order.keys())
            all_z_orders.sort()
            for z in all_z_orders:
                object_inds_at_z = objs_by_z_order[z]
                for ind in object_inds_at_z:

                    # removes and re-adds visual components to canvas
                    if z <= max_game_z:
                        obj = current_scene.game_elements[ind]
                        self.remove(obj.color)
                        self.add(obj.color)
                        if obj.shape != None:
                            self.remove(obj.shape)
                            self.add(obj.shape)
                    else:
                        obj = current_scene.UI_elements[ind]
                        self.remove(obj.color)
                        self.add(obj.color)
                        if obj.shape != None:
                            self.remove(obj.shape)
                            self.add(obj.shape)


class Scene(InstructionGroup):
    def __init__(self, initial_game_elements = [], initial_UI_elements = [], game_camera = None, ground_map = [], res = 20.0, audio_controller = None):
        super(Scene, self).__init__()
        self.game_elements = initial_game_elements
        self.UI_elements = initial_UI_elements
        self.game_camera = game_camera
        self.audio_controller = audio_controller
        self.res = res

        self.player = Player(res = res, initial_world_pos = (2, 6))
        self.game_elements.append(self.player.element)

        self.ground_map = ground_map

    def on_update(self, dt, active_keys):

        # gets important camera information
        camera_scalar = None
        camera_offset = None # in world units
        if self.game_camera != None:
            self.game_camera.on_update(dt)

            camera_scalar = self.game_camera.zoom_factor
            camera_offset = (-self.game_camera.world_focus[0]*camera_scalar*2.0*self.res+window_size[0], -self.game_camera.world_focus[1]*camera_scalar*2.0*self.res+window_size[1])

        # updates player collisions
        self.player.on_update(dt, self.ground_map, active_keys, camera_scalar, camera_offset)
        if self.game_camera != None: self.game_camera.update_target(self.player.world_pos)

        for element in self.game_elements:
            element.on_update(dt, camera_scalar, camera_offset)

        for element in self.UI_elements:
            element.on_update(dt, camera_scalar, camera_offset)

        # audio controller update
        if self.audio_controller != None: self.audio_controller.on_update(dt, self.player, active_keys)

    def add_UI_element(self, element):
        self.UI_elements.append(element)

    def add_game_element(self, element):
        self.game_elements.append(element)


class Camera(object):
    def __init__(self, initial_world_focus = (0, 0), initial_world_target = (0, 0), zoom_factor = 1.1, speed = 1.0):
        self.world_focus = initial_world_focus
        self.world_target = initial_world_target
        self.zoom_factor = zoom_factor
        self.speed = speed

    def update_target(self, new_target):
        self.world_target = new_target

    def on_update(self, dt):
        self.world_focus = (self.world_focus[0] + ((self.world_target[0] - self.world_focus[0])  * dt * self.speed), self.world_focus[1] + ((self.world_target[1] - self.world_focus[1]) * dt * self.speed))

