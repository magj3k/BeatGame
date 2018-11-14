import math
import random
from objects import *
from core import *
from scene_manager import *
from kivy.core.window import Window
from audio_controller import *

middle = (window_size[0]/2, window_size[1]/2)
far_z = 100000000

scene_1_resolution = 30.0
scene_1_elevation_offset = 6
scene_1_ground_map = [0+scene_1_elevation_offset]*86
scene_1_ground_map[0:24] = [1+scene_1_elevation_offset]*24
scene_1_ground_map[0:22] = [2+scene_1_elevation_offset]*22
scene_1_ground_map[0:21] = [4+scene_1_elevation_offset]*21
scene_1_ground_map[0:19] = [7+scene_1_elevation_offset]*19
scene_1_ground_map[0:18] = [8+scene_1_elevation_offset]*18
scene_1_ground_map[0:16] = [10+scene_1_elevation_offset]*16
scene_1_ground_map[0:13] = [11+scene_1_elevation_offset]*13
scene_1_ground_map[0:6] = [10+scene_1_elevation_offset]*6
scene_1_ground_map[40:50] = [-1+scene_1_elevation_offset]*10
scene_1_ground_map[57:65] = [1+scene_1_elevation_offset]*8
scene_1_ground_map[80:86] = [4+scene_1_elevation_offset]*6
# scene_1_ground_map[25:30] = [7+scene_1_elevation_offset]*4
# scene_1_ground_map[34:38] = [4+scene_1_elevation_offset]*4
# scene_1_ground_map[41:43] = [7+scene_1_elevation_offset]*2
# scene_1_ground_map[53] = 8+scene_1_elevation_offset
# scene_1_ground_map[54] = 9+scene_1_elevation_offset
# scene_1_ground_map[55] = 10+scene_1_elevation_offset
# scene_1_ground_map[56] = 11+scene_1_elevation_offset
# scene_1_ground_map[57] = 12+scene_1_elevation_offset
# scene_1_ground_map[58:61] = [1+scene_1_elevation_offset]*3
# scene_1_ground_map[60:62] = [10+scene_1_elevation_offset]*2
# scene_1_ground_map[64:66] = [8+scene_1_elevation_offset]*2
scene_1_camera_bounds = ((24, 6.5), (64, 10))
scene_1_resolution = 30.0
scene_1_player = Player(res = scene_1_resolution, initial_world_pos = (25, 6), z = 110)

scene_1_game_elements = [
                                                    Backdrop(element = TexturedElement(pos = (0, 0),
                                                        z = 0,
                                                        size = (window_size[0]*3.0, window_size[1]*1.2),
                                                        texture_path = "graphics/bg_1.png"),
                                                        parallax_z = far_z),
                                                    Backdrop(element = TexturedElement(pos = (0, -340),
                                                        z = 1,
                                                        size = (window_size[0]*3.0, window_size[1]*0.8),
                                                        texture_path = "graphics/bg_2.png",
                                                        color = Color(0.25, 0.45, 0.2)),
                                                        parallax_z = 60),
                                                    Backdrop(element = TexturedElement(pos = (-100, 50),
                                                        z = 5,
                                                        size = (1466*0.8, 519*0.8),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.35, 0.55, 0.3)),
                                                        parallax_z = 2),
                                                    Backdrop(element = TexturedElement(pos = (1000, 50),
                                                        z = 5,
                                                        size = (-1466*0.85, 519*0.85),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.35, 0.55, 0.3)),
                                                        parallax_z = 2),
                                                    Backdrop(element = TexturedElement(pos = (250, 0),
                                                        z = 4,
                                                        size = (1466*-0.6, 519*0.6),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.3, 0.5, 0.25)),
                                                        parallax_z = 3),
                                                    Terrain(scene_1_ground_map,
                                                        z = 100,
                                                        color = Color(0, 0, 0),
                                                        res = scene_1_resolution)
                                                ]

# background trees test
# for i in range(15):
#     rand_size_coeff = (random.random()*0.4 +0.8, random.random()*0.6 + 0.7)
#     new_tree = Backdrop(element = TexturedElement(pos = ((random.random()*2800) - 150, 90+(100*rand_size_coeff[1])),
#                                                         z = 90,
#                                                         size = (234*0.6*rand_size_coeff[0], 451*0.6*rand_size_coeff[1]),
#                                                         color = Color(0.3, 0.4, 0.2),
#                                                         texture_path = "graphics/tree_1.png"),
#                                                         parallax_z = 0.4)
#     scene_1_game_elements.append(new_tree)
# for i in range(25):
#     rand_size_coeff = (random.random()*0.4 +0.8, random.random()*0.6 + 0.7)
#     new_tree = Backdrop(element = TexturedElement(pos = ((random.random()*2000) - 100, 50+(70*rand_size_coeff[1])),
#                                                         z = 80,
#                                                         size = (234*0.35*rand_size_coeff[0], 451*0.35*rand_size_coeff[1]),
#                                                         color = Color(0.4, 0.47, 0.27),
#                                                         texture_path = "graphics/tree_1.png"),
#                                                         parallax_z = 1.1)
#     scene_1_game_elements.append(new_tree)


scene_1_audio_controller = AudioController(level = 0, bpm = 120, elements = scene_1_game_elements)
scene_1_camera = Camera(zoom_factor = 1.1, speed = 0.85, bounds = scene_1_camera_bounds)
scene_1 = Scene(initial_game_elements = scene_1_game_elements, initial_UI_elements = [], ground_map = scene_1_ground_map, game_camera = scene_1_camera, res = scene_1_resolution, audio_controller = scene_1_audio_controller, player = scene_1_player)

scenes = [scene_1]