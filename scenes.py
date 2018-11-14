import math
import random
from objects import *
from core import *
from scene_manager import *
from kivy.core.window import Window
from audio_controller import *

middle = (window_size[0]/2, window_size[1]/2)
far_z = 100000000

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
scene_1_player = Player(res = scene_1_resolution, initial_world_pos = (2, 6), z = 110)

scene_1_game_elements = [
                                                    Backdrop(element = TexturedElement(pos = (0, 0),
                                                        z = 0,
                                                        size = (window_size[0]*3.0, window_size[1]*1.2),
                                                        texture_path = "graphics/bg_1.png"),
                                                        parallax_z = far_z),
                                                    Terrain(scene_1_ground_map,
                                                        z = 100,
                                                        color = Color(0, 0, 0),
                                                        res = scene_1_resolution)
                                                ]
for i in range(40):
    rand_z = (random.random()*50)+25
    new_tree = Backdrop(element = TexturedElement(pos = (random.random()*1300, random.random()*200),
                                                        z = 100-rand_z,
                                                        size = (234*0.8*(100-rand_z)/100, 451*0.8*(100-rand_z)/100),
                                                        color = Color(0.6*rand_z/100, 0.4*rand_z/100, 0.25*rand_z/100),
                                                        texture_path = "graphics/tree_1.png"),
                                                        parallax_z = 1.0+(rand_z/50))
    scene_1_game_elements.append(new_tree)


scene_1_audio_controller = AudioController(level = 0, bpm = 120, elements = scene_1_game_elements)
scene_1_camera = Camera(zoom_factor = 1.1, speed = 0.85)

scene_1 = Scene(initial_game_elements = scene_1_game_elements, initial_UI_elements = [], ground_map = scene_1_ground_map, game_camera = scene_1_camera, res = scene_1_resolution, audio_controller = scene_1_audio_controller, player = scene_1_player)

scenes = [scene_1]