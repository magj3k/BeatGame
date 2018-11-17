import math
import random
from objects import *
from core import *
from scene_manager import *
from kivy.core.window import Window
from audio_controller import *

middle = (window_size[0]/2, window_size[1]/2)
far_z = 100000000

keys_UI = [TexturedElement(pos = (window_size[0]-45, window_size[1]-65),
                        z = 1,
                        size = (166*0.2, 400*0.2),
                        texture_path = "graphics/key_outline.png",
                        tag = "k_1"), 
                    TexturedElement(pos = (window_size[0]-95, window_size[1]-65),
                        z = 1,
                        size = (166*0.2, 400*0.2),
                        texture_path = "graphics/key_outline.png",
                        tag = "k_2"),
                    TexturedElement(pos = (window_size[0]-145, window_size[1]-65),
                        z = 1,
                        size = (166*0.2, 400*0.2),
                        texture_path = "graphics/key_outline.png",
                        tag = "k_3"),
                    TexturedElement(pos = (window_size[0]-66, window_size[1]-49),
                        z = 0,
                        color = Color(0, 0, 0, 0.5),
                        size = (650*0.4, 450*0.4),
                        texture_path = "graphics/rounded_box.png")]

scene_1_resolution = 30.0
scene_1_elevation_offset = 6
scene_1_water_map = [0]*86
scene_1_ground_map = [0+scene_1_elevation_offset]*86
scene_1_ground_map[0:24] = [1+scene_1_elevation_offset]*24
scene_1_ground_map[0:22] = [2+scene_1_elevation_offset]*22
scene_1_ground_map[0:21] = [4+scene_1_elevation_offset]*21
scene_1_ground_map[0:18] = [8+scene_1_elevation_offset]*18
scene_1_ground_map[0:16] = [10+scene_1_elevation_offset]*16
scene_1_ground_map[0:12] = [11+scene_1_elevation_offset]*12
scene_1_ground_map[38:51] = [-5+scene_1_elevation_offset]*13
scene_1_water_map[38:51] = [-1+scene_1_elevation_offset]*13
scene_1_ground_map[59:67] = [1+scene_1_elevation_offset]*8
scene_1_ground_map[80:86] = [4+scene_1_elevation_offset]*6
scene_1_camera_bounds = ((25, 6.5), (64, 9.5))
scene_1_resolution = 30.0
scene_1_player = Player(res = scene_1_resolution, initial_world_pos = (27.5, 8), z = 110)
scene_1_door = TexturedElement(pos = (2445, 213),
                                z = 101,
                                size = (500*0.13, 500*0.13),
                                texture_path = "graphics/door_closed.png",
                                tag = "door")

scene_1_game_elements = [   scene_1_door,
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
                                                    Backdrop(element = TexturedElement(pos = (-220, 40),
                                                        z = 3,
                                                        size = (-1466*0.3, 519*0.3),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.25, 0.45, 0.2)),
                                                        parallax_z = 9),
                                                    Backdrop(element = TexturedElement(pos = (350, 25),
                                                        z = 3,
                                                        size = (1466*0.28, 519*0.28),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.25, 0.45, 0.2)),
                                                        parallax_z = 9),
                                                    Backdrop(element = TexturedElement(pos = (250, 0),
                                                        z = 4,
                                                        size = (1466*-0.6, 519*0.6),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.3, 0.5, 0.25)),
                                                        parallax_z = 3),
                                                    Terrain(scene_1_ground_map,
                                                        z = 100,
                                                        color = Color(0, 0, 0),
                                                        res = scene_1_resolution),
                                                    Terrain(scene_1_water_map,
                                                        z = 111,
                                                        color = Color(0.35, 0.35, 0.95),
                                                        res = scene_1_resolution,
                                                        type = "water"),
                                                    Pickup(TexturedElement(pos = (65*scene_1_resolution, 295),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Pickup(TexturedElement(pos = (44.8*scene_1_resolution, 302),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Pickup(TexturedElement(pos = (25*scene_1_resolution, 370),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Platform(((41, 7), (42, 7)),
                                                        type = "dirt",
                                                        z = 100,
                                                        res = scene_1_resolution),
                                                    Platform(((46.5, 7), (47.5, 7)),
                                                        type = "dirt",
                                                        z = 100,
                                                        res = scene_1_resolution)
                                                ]
scene_1_UI_elements = []
scene_1_UI_elements.extend(keys_UI)

scene_1_audio_controller = AudioController(level = 0, bpm = 120, elements = scene_1_game_elements)
scene_1_camera = Camera(zoom_factor = 1.1, speed = 0.85, bounds = scene_1_camera_bounds)
scene_1 = Scene(initial_game_elements = scene_1_game_elements, initial_UI_elements = scene_1_UI_elements, ground_map = scene_1_ground_map, game_camera = scene_1_camera, res = scene_1_resolution, audio_controller = scene_1_audio_controller, player = scene_1_player)

scenes = [scene_1]