from objects import *
from core import *
from scene_manager import *
from kivy.core.window import Window

middle = (window_size[0]/2, window_size[1]/2)

scene_1_ground_map = [6]*50
scene_1_ground_map[5:10] = [7]*4
scene_1_ground_map[14:18] = [4]*4
scene_1_ground_map[21:23] = [7]*2
scene_1_ground_map[23] = 8
scene_1_ground_map[24] = 9
scene_1_ground_map[25] = 10
scene_1_ground_map[26] = 11
scene_1_ground_map[27] = 12
scene_1_ground_map[28:31] = [1]*3
scene_1_ground_map[30:32] = [10]*2
scene_1_ground_map[34:36] = [8]*2
scene_1_resolution = 30.0
scene_1_game_elements = [
                                                    TexturedElement(pos = middle,
                                                        z = 0,
                                                        size = window_size,
                                                        texture_path = "graphics/bg_1.png"),
                                                    Terrain(scene_1_ground_map,
                                                        z = 10,
                                                        color = Color(0, 0, 0),
                                                        res = scene_1_resolution),
                                                ]
scene_1 = Scene(initial_game_elements = scene_1_game_elements, initial_UI_elements = [], ground_map = scene_1_ground_map, res = scene_1_resolution)

scenes = [scene_1]