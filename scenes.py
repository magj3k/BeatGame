import math
import random
from objects import *
from core import *
from scene_manager import *
from kivy.core.window import Window
from audio_controller import *

middle = (window_size[0]/2, window_size[1]/2)
far_z = 100000000

#   SCENE CONSTRUCTION NOTE:
# Objects for each scene need to be
# specifically created for each scene,
# NOT copied

# elements uniform across all scenes

scene_resolution = 30.0
scene_elevation_offset = 6

keys_UI = [TexturedElement(pos = (window_size[0]-45, window_size[1]-65),
                        z = 10,
                        size = (166*0.2, 400*0.2),
                        texture_path = "graphics/key_outline.png",
                        tag = "k_1"), 
                    TexturedElement(pos = (window_size[0]-95, window_size[1]-65),
                        z = 10,
                        size = (166*0.2, 400*0.2),
                        texture_path = "graphics/key_outline.png",
                        tag = "k_2"),
                    TexturedElement(pos = (window_size[0]-145, window_size[1]-65),
                        z = 10,
                        size = (166*0.2, 400*0.2),
                        texture_path = "graphics/key_outline.png",
                        tag = "k_3"),
                    TexturedElement(pos = (window_size[0]-66, window_size[1]-49),
                        z = 1,
                        color = Color(0, 0, 0, 0.5),
                        size = (650*0.4, 450*0.4),
                        texture_path = "graphics/rounded_box.png",
                        tag = "keys_bg")]

fight_UI = [
    TexturedElement(pos = (window_size[0]-70, window_size[1]),
        z = 1,
        color = Color(0, 0, 0, 0),
        size = (650*0.64, 450*0.45),
        texture_path = "graphics/rounded_box.png",
        tag = "h_bge"),
    TexturedElement(pos = (70, window_size[1]),
        z = 1,
        color = Color(0, 0, 0, 0),
        size = (650*0.64, 450*0.45),
        texture_path = "graphics/rounded_box.png",
        tag = "h_bg"),
    TexturedElement(pos = (50, window_size[1]-50),
        z = 11,
        size = (206*0.3, 204*0.3),
        texture_path = "graphics/heart.png",
        tag = "h_1",
        color = Color(1, 1, 1, 0)),
    TexturedElement(pos = (177, window_size[1]-50),
        z = 11,
        size = (540*0.28, 181*0.28),
        texture_path = "graphics/health_bar_outline.png",
        tag = "h_baroutline_1",
        color = Color(1, 1, 1, 0)),
    TexturedElement(pos = (177, window_size[1]-50),
        z = 10,
        size = (514*0.28, 155*0.28),
        texture_path = "graphics/health_bar.png",
        tag = "h_bar_1",
        color = Color(1, 1, 1, 0)),
    TexturedElement(pos = (window_size[0]-50, window_size[1]-50),
        z = 11,
        size = (206*0.3, 204*0.3),
        texture_path = "graphics/heart.png",
        tag = "h_1e",
        color = Color(1, 1, 1, 0)),
    TexturedElement(pos = (window_size[0]-177, window_size[1]-50),
        z = 11,
        size = (540*0.28, 181*0.28),
        texture_path = "graphics/health_bar_outline.png",
        tag = "h_baroutline_1e",
        color = Color(1, 1, 1, 0)),
    TexturedElement(pos = (window_size[0]-177, window_size[1]-50),
        z = 10,
        size = (514*0.28, 155*0.28),
        texture_path = "graphics/health_bar.png",
        tag = "h_bar_1e",
        color = Color(1, 1, 1, 0)),
]

# scene 1

scene_1_water_map = [0]*95
scene_1_ground_map = [0+scene_elevation_offset]*86
scene_1_ground_map[0:24] = [1+scene_elevation_offset]*24
scene_1_ground_map[0:22] = [2+scene_elevation_offset]*22
scene_1_ground_map[0:21] = [4+scene_elevation_offset]*21
scene_1_ground_map[0:18] = [8+scene_elevation_offset]*18
scene_1_ground_map[0:16] = [10+scene_elevation_offset]*16
scene_1_ground_map[0:12] = [11+scene_elevation_offset]*12
scene_1_ground_map[36:38] = [1+scene_elevation_offset]*2
scene_1_ground_map[38:51] = [-5+scene_elevation_offset]*13
scene_1_water_map[38:51] = [-1+scene_elevation_offset]*13
scene_1_ground_map[51:53] = [1+scene_elevation_offset]*2
scene_1_ground_map[59:67] = [1+scene_elevation_offset]*8
scene_1_ground_map[80:95] = [4+scene_elevation_offset]*15
scene_1_player = Player(res = scene_resolution, initial_world_pos = (27.5, 8), z = 110)
# scene_1_player = Player(res = scene_resolution, initial_world_pos = (77, 10), z = 110)
scene_1_door = TexturedElement(pos = (2445, 213),
                                z = 101,
                                size = (500*0.13, 500*0.13),
                                texture_path = "graphics/door_closed.png",
                                tag = "door")

scene_1_enemies = [
    Enemy(res = scene_resolution, initial_world_pos = (73, 7), radius = 40, z = 110, moves_per_beat = ["stop", "left", "stop", "right", "stop", "right", "stop", "left"], has_key = True),
    Enemy(res = scene_resolution, initial_world_pos = (64, 8), radius = 40, z = 110, moves_per_beat = ["stop", "left", "stop", "right"])
]

scene_1_game_elements = [   scene_1_door,
                                                    TexturedElement(pos = (2350, 280),
                                                        z = 99,
                                                        size = (458*0.17, 490*0.17),
                                                        texture_path = "graphics/not_enough_keys.png",
                                                        tag = "door_warning"),
                                                    Backdrop(element = TexturedElement(pos = (0, 0),
                                                        z = 0,
                                                        size = (window_size[0]*3.0, window_size[1]*1.2),
                                                        texture_path = "graphics/bg_1.png"),
                                                        parallax_z = far_z),
                                                    Backdrop(element = TexturedElement(pos = (0, -300),
                                                        z = 1,
                                                        size = (window_size[0]*3.0, window_size[1]*0.8),
                                                        texture_path = "graphics/bg_2.png",
                                                        color = Color(0.2, 0.4, 0.15)),
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
                                                        res = scene_resolution),
                                                    Terrain(scene_1_water_map,
                                                        z = 111,
                                                        color = Color(0.35, 0.35, 0.95),
                                                        res = scene_resolution,
                                                        type = "water"),
                                                    Pickup(TexturedElement(pos = (65*scene_resolution, 295),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Pickup(TexturedElement(pos = (44.8*scene_resolution, 312),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Pickup(TexturedElement(pos = (25*scene_resolution, 362),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Platform(((41, 6), (42, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = False,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((46.5, 6), (47.5, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav")
                                                ]
scene_1_game_elements.extend(scene_1_enemies)
scene_1_UI_elements = []
scene_1_UI_elements.extend(keys_UI)
scene_1_UI_elements.extend(fight_UI)

scene_1_audio_controller = AudioController(level = 0, bpm = 120, elements = scene_1_game_elements)
scene_1_camera_bounds = ((25, 6.5), (66, 9.5))
scene_1_camera = Camera(zoom_factor = 1.1, initial_world_target = scene_1_player.world_pos, speed = 1.05, bounds = scene_1_camera_bounds)
scene_1 = Scene(initial_game_elements = scene_1_game_elements, initial_UI_elements = scene_1_UI_elements, ground_map = scene_1_ground_map, game_camera = scene_1_camera, res = scene_resolution, audio_controller = scene_1_audio_controller, player = scene_1_player)

# menu 1

menu_1_water_map = [0]*95
menu_1_ground_map = [0+scene_elevation_offset]*86
menu_1_ground_map[0:24] = [1+scene_elevation_offset]*24
menu_1_ground_map[0:22] = [2+scene_elevation_offset]*22
menu_1_ground_map[0:21] = [4+scene_elevation_offset]*21
menu_1_ground_map[0:18] = [8+scene_elevation_offset]*18
menu_1_ground_map[0:16] = [10+scene_elevation_offset]*16
menu_1_ground_map[0:12] = [11+scene_elevation_offset]*12
menu_1_ground_map[36:38] = [1+scene_elevation_offset]*2
menu_1_ground_map[38:51] = [-5+scene_elevation_offset]*13
menu_1_water_map[38:51] = [-1+scene_elevation_offset]*13
menu_1_ground_map[51:53] = [1+scene_elevation_offset]*2
menu_1_ground_map[59:67] = [1+scene_elevation_offset]*8
menu_1_ground_map[80:95] = [4+scene_elevation_offset]*15
menu_1_player = Player(res = scene_resolution, initial_world_pos = (38, 9.5), z = 110)
menu_1_player.collisions_enabled = False
menu_1_player.controls_disabled = True
menu_1_player.hidden = True

menu_1_game_elements = [      Backdrop(element = TexturedElement(pos = (0, 0),
                                                        z = 0,
                                                        size = (window_size[0]*3.0, window_size[1]*1.2),
                                                        texture_path = "graphics/bg_1.png"),
                                                        parallax_z = far_z),
                                                    Backdrop(element = TexturedElement(pos = (0, -300),
                                                        z = 1,
                                                        size = (window_size[0]*3.0, window_size[1]*0.8),
                                                        texture_path = "graphics/bg_2.png",
                                                        color = Color(0.2, 0.4, 0.15)),
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
                                                    Terrain(menu_1_ground_map,
                                                        z = 100,
                                                        color = Color(0, 0, 0),
                                                        res = scene_resolution),
                                                    Terrain(menu_1_water_map,
                                                        z = 111,
                                                        color = Color(0.35, 0.35, 0.95),
                                                        res = scene_resolution,
                                                        type = "water")
                                                ]
menu_1_UI_elements = [
    TexturedElement(pos = (330, window_size[1]-170),
        z = 1,
        size = (878*0.55, 318*0.55),
        texture_path = "graphics/logo.png",
        tag = "logo"),
    TexturedElement(pos = (window_size[0]-(539*0.3*0.5)-40, 135),
        z = 1,
        size = (539*0.3, 157*0.3),
        texture_path = "graphics/option_play.png",
        tag = "option_1"),
    TexturedElement(pos = (window_size[0]-(490*0.3*0.5)-40, 65),
        z = 1,
        size = (490*0.3, 155*0.3),
        texture_path = "graphics/option_quit.png",
        tag = "option_2")
]

menu_1_audio_controller = AudioController(level = 0, bpm = 120, elements = menu_1_game_elements)
menu_1_camera = Camera(zoom_factor = 0.85, initial_world_target = menu_1_player.world_pos, speed = 8.0)
menu_1 = Menu(num_options = 2, option_actions = [["scene", 1], ["quit", -1]], initial_game_elements = menu_1_game_elements, initial_UI_elements = menu_1_UI_elements, ground_map = menu_1_ground_map, game_camera = menu_1_camera, res = scene_resolution, audio_controller = menu_1_audio_controller, player = menu_1_player)

# SCENE 2 IS A TEST, currently it copies objects from scene 1, which DOES NOT WORK

scene_2_player = Player(res = scene_resolution, initial_world_pos = (27.5, 8), z = 110)
scene_2_audio_controller = AudioController(level = 0, bpm = 120, elements = scene_1_game_elements[:])
scene_2_camera = Camera(zoom_factor = 1.1, initial_world_target = scene_2_player.world_pos, speed = 0.85, bounds = scene_1_camera_bounds)
scene_2 = Scene(initial_game_elements = scene_1_game_elements, initial_UI_elements = scene_1_UI_elements, ground_map = scene_1_ground_map, game_camera = scene_2_camera, res = scene_resolution, audio_controller = scene_2_audio_controller, player = scene_2_player)

scenes = [menu_1, scene_1]