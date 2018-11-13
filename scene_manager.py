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
    def __init__(self, initial_game_elements = [], initial_UI_elements = [], game_camera = None, ground_map = []):
        super(Scene, self).__init__()
        self.game_elements = initial_game_elements
        self.UI_elements = initial_UI_elements
        self.game_camera = game_camera

        self.player = Player(res = 45.0, initial_world_pos = (2, 6))
        self.game_elements.append(self.player.element)

        self.ground_map = ground_map

    def on_update(self, dt, active_keys):
        # updates player collisions
        self.player.on_update(dt, self.ground_map, active_keys)

        for element in self.game_elements:
            element.on_update(dt)

        for element in self.UI_elements:
            element.on_update(dt)

    def add_UI_element(self, element):
        self.UI_elements.append(element)

    def add_game_element(self, element):
        self.game_elements.append(element)


class Camera(object):
    def __init__(self):
        pass

