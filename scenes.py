from objects import *
from core import *
from scene_manager import *
from kivy.core.window import Window

middle = (window_size[0]/2, window_size[1]/2)

scene_1_ground_map = [6]*50
scene_1_ground_map[5:10] = [7]*4
scene_1_ground_map[15:17] = [4]*2
scene_1_game_elements = [
                                                    TexturedElement(pos = middle,
                                                        z = 0,
                                                        size = window_size,
                                                        texture_path = "graphics/bg_1.png"),
                                                    Terrain(scene_1_ground_map,
                                                        z = 10,
                                                        color = Color(0, 0, 0),
                                                        res = 90.0),
                                                ]
scene_1 = Scene(initial_game_elements = scene_1_game_elements, initial_UI_elements = [])

scenes = [scene_1]