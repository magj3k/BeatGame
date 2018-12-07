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

# scene 0

scene_0_water_map = [0]*95
scene_0_ground_map = [0+scene_elevation_offset]*86
scene_0_ground_map[0:24] = [1+scene_elevation_offset]*24
scene_0_ground_map[0:22] = [2+scene_elevation_offset]*22
scene_0_ground_map[0:21] = [4+scene_elevation_offset]*21
scene_0_ground_map[0:18] = [8+scene_elevation_offset]*18
scene_0_ground_map[0:16] = [10+scene_elevation_offset]*16
scene_0_ground_map[0:12] = [11+scene_elevation_offset]*12
scene_0_ground_map[36:38] = [1+scene_elevation_offset]*2
scene_0_ground_map[38:51] = [-5+scene_elevation_offset]*13
scene_0_water_map[38:51] = [-1+scene_elevation_offset]*13
scene_0_ground_map[51:53] = [1+scene_elevation_offset]*2
scene_0_ground_map[59:67] = [1+scene_elevation_offset]*8
scene_0_ground_map[80:95] = [4+scene_elevation_offset]*15
scene_0_player = Player(res = scene_resolution, initial_world_pos = (27.5, 8), z = 110)
scene_0_door = TexturedElement(pos = (2445, 213),
                                z = 101,
                                size = (500*0.13, 500*0.13),
                                texture_path = "graphics/door_closed.png",
                                tag = "door")

scene_0_enemies = [
    Enemy(res = scene_resolution, initial_world_pos = (73, 7), radius = 40, z = 110, moves_per_beat = ["stop", "left", "stop", "right", "stop", "right", "stop", "left"], has_key = True),
    Enemy(res = scene_resolution, initial_world_pos = (64, 8), radius = 40, z = 110, moves_per_beat = ["stop", "left", "stop", "right"])
]

scene_0_game_elements = [   scene_0_door,
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
                                                    Terrain(scene_0_ground_map,
                                                        z = 100,
                                                        color = Color(0, 0, 0),
                                                        res = scene_resolution),
                                                    Terrain(scene_0_water_map,
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
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    JumpPad(world_pos = (31, 7),
                                                        z = 99,
                                                        color = Color(0, 0, 0),
                                                        beats = [2, 4],
                                                        res = scene_resolution,
                                                        sound_path = "audio/jumppad.wav"),
                                                    Spikes(world_pos = (33, 7),
                                                        z = 99,
                                                        color = Color(0, 0, 0),
                                                        beats = [1, 3],
                                                        res = scene_resolution,
                                                        sound_path = "audio/spike.wav")
                                                ]
scene_0_game_elements.extend(scene_0_enemies)
scene_0_UI_elements = []
scene_0_UI_elements.extend(keys_UI)
scene_0_UI_elements.extend(fight_UI)

scene_0_audio_controller = AudioController(level = 0, bpm = 120, elements = scene_0_game_elements)
scene_0_camera_bounds = ((25, 6.5), (66, 9.5))
scene_0_camera = Camera(zoom_factor = 1.1, initial_world_target = scene_0_player.world_pos, speed = 1.05, bounds = scene_0_camera_bounds)
scene_0 = Scene(initial_game_elements = scene_0_game_elements, initial_UI_elements = scene_0_UI_elements, ground_map = scene_0_ground_map, game_camera = scene_0_camera, res = scene_resolution, audio_controller = scene_0_audio_controller, player = scene_0_player)

# scene 1

scene_1_water_map = [0]*105
scene_1_ground_map = [0+scene_elevation_offset]*105
scene_1_ground_map[0:24] = [1+scene_elevation_offset]*24
scene_1_ground_map[0:22] = [2+scene_elevation_offset]*22
scene_1_ground_map[0:21] = [4+scene_elevation_offset]*21
scene_1_ground_map[0:18] = [8+scene_elevation_offset]*18
scene_1_ground_map[0:16] = [10+scene_elevation_offset]*16
scene_1_ground_map[0:12] = [11+scene_elevation_offset]*12
scene_1_ground_map[35:45] = [1+scene_elevation_offset]*10
scene_1_ground_map[52:55] = [1+scene_elevation_offset]*3
scene_1_ground_map[55:56] = [2+scene_elevation_offset]*1
scene_1_ground_map[56:57] = [3+scene_elevation_offset]*1
scene_1_ground_map[57:58] = [4+scene_elevation_offset]*1
scene_1_ground_map[58:63] = [-1+scene_elevation_offset]*5
scene_1_ground_map[66:68] = [1+scene_elevation_offset]*2
scene_1_ground_map[68:75] = [-5+scene_elevation_offset]*7
scene_1_water_map[68:75] = [-1+scene_elevation_offset]*7
scene_1_ground_map[75:77] = [1+scene_elevation_offset]*2
scene_1_ground_map[85:105] = [4+scene_elevation_offset]*20
scene_1_ground_map[90:105] = [6+scene_elevation_offset]*15
scene_1_ground_map[94:105] = [8+scene_elevation_offset]*11
scene_1_player = Player(res = scene_resolution, initial_world_pos = (27, 7.5), z = 110)
scene_1_door_offset = scene_resolution*5
scene_1_door = TexturedElement(pos = (2445 + scene_1_door_offset, 213),
                                z = 101,
                                size = (500*0.13, 500*0.13),
                                texture_path = "graphics/door_closed.png",
                                tag = "door")

scene_1_game_elements = [   scene_1_door,
                                                    TexturedElement(pos = (2350+scene_1_door_offset, 280),
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
                                                        z = 11,
                                                        size = (window_size[0]*3.0, window_size[1]*0.8),
                                                        texture_path = "graphics/bg_2.png",
                                                        color = Color(0.2, 0.4, 0.15)),
                                                        parallax_z = 60),
                                                    Backdrop(element = TexturedElement(pos = (-100, 50),
                                                        z = 15,
                                                        size = (1466*0.8, 519*0.8),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.35, 0.55, 0.3)),
                                                        parallax_z = 2),
                                                    Backdrop(element = TexturedElement(pos = (960, 10),
                                                        z = 16,
                                                        size = (-1414*0.85, 370*0.85),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.35, 0.55, 0.3)),
                                                        parallax_z = 1),
                                                    Backdrop(element = TexturedElement(pos = (960, 10),
                                                        z = 16,
                                                        size = (-1414*0.85, 370*0.85),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.3, 0.3, 0.9)),
                                                        parallax_z = 1),
                                                    Backdrop(element = TexturedElement(pos = (-220, 40),
                                                        z = 13,
                                                        size = (-1466*0.3, 519*0.3),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.25, 0.45, 0.2)),
                                                        parallax_z = 9),
                                                    Backdrop(element = TexturedElement(pos = (350, 25),
                                                        z = 13,
                                                        size = (1466*0.28, 519*0.28),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.25, 0.45, 0.2)),
                                                        parallax_z = 9),
                                                    Backdrop(element = TexturedElement(pos = (850, 30),
                                                        z = 14,
                                                        size = (1466*-0.6, 519*0.6),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.3, 0.5, 0.25)),
                                                        parallax_z = 3),
                                                    Backdrop(element = TexturedElement(pos = (400, 10),
                                                        z = 14,
                                                        size = (1466*0.6, 519*0.6),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.3, 0.5, 0.25)),
                                                        parallax_z = 3),
                                                    Backdrop(element = TexturedElement(pos = (370, -80),
                                                        z = 5,
                                                        size = (532*1.4, 266*1.4),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 200),
                                                    Backdrop(element = TexturedElement(pos = (540, 30),
                                                        z = 9,
                                                        size = (532*1.0, 266*1.0),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 150),
                                                    Backdrop(element = TexturedElement(pos = (540, 30),
                                                        z = 9,
                                                        size = (532*1.0, 266*1.0),
                                                        texture_path = "graphics/mountain_cap.png",
                                                        color = Color(1, 1, 1)),
                                                        parallax_z = 150),
                                                    Terrain(scene_1_ground_map,
                                                        z = 100,
                                                        color = Color(0, 0, 0),
                                                        res = scene_resolution),
                                                    Terrain(scene_1_water_map,
                                                        z = 111,
                                                        color = Color(0.35, 0.35, 0.95),
                                                        res = scene_resolution,
                                                        type = "water"),
                                                    Pickup(TexturedElement(pos = (40*scene_resolution, 295),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Pickup(TexturedElement(pos = (60.5*scene_resolution, 12*scene_resolution),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Pickup(TexturedElement(pos = (81*scene_resolution, 288),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Platform(((70.2, 6), (71.8, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = False,
                                                        beats = [],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((59.5, 7.5), (60.5, 7.5)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = False,
                                                        beats = [],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav")
                                                ]
scene_1_UI_elements = []
scene_1_UI_elements.extend(keys_UI)
scene_1_UI_elements.extend(fight_UI)

scene_1_audio_controller = AudioController(level = 0, bpm = 120, elements = scene_1_game_elements)
scene_1_camera_bounds = ((25, 6.5), (77, 9.5))
scene_1_camera = Camera(zoom_factor = 1.1, initial_world_target = scene_1_player.world_pos, speed = 1.05, bounds = scene_1_camera_bounds)
scene_1 = Scene(initial_game_elements = scene_1_game_elements, initial_UI_elements = scene_1_UI_elements, ground_map = scene_1_ground_map, game_camera = scene_1_camera, res = scene_resolution, audio_controller = scene_1_audio_controller, player = scene_1_player, puzzle_mode_supported = False)

# scene 2

scene_2_water_map_1 = [0]*155
scene_2_water_map_2 = [0]*155
scene_2_ground_map = [0+scene_elevation_offset]*155
scene_2_ground_map[0:22] = [4+scene_elevation_offset]*22
scene_2_ground_map[0:18] = [6+scene_elevation_offset]*18
scene_2_ground_map[0:14] = [8+scene_elevation_offset]*14
scene_2_ground_map[28:31] = [-1+scene_elevation_offset]*3
scene_2_ground_map[34:36] = [1+scene_elevation_offset]*2
scene_2_ground_map[49:51] = [1+scene_elevation_offset]*2
scene_2_ground_map[36:49] = [-5+scene_elevation_offset]*13
scene_2_water_map_1[36:49] = [-1+scene_elevation_offset]*13
scene_2_ground_map[65:73] = [1+scene_elevation_offset]*8
scene_2_ground_map[66:72] = [2+scene_elevation_offset]*6
scene_2_ground_map[67:71] = [3+scene_elevation_offset]*4
scene_2_ground_map[68:70] = [4+scene_elevation_offset]*2
scene_2_ground_map[74:77] = [-1+scene_elevation_offset]*3
scene_2_ground_map[79:81] = [1+scene_elevation_offset]*2
scene_2_ground_map[81:99] = [-5+scene_elevation_offset]*18
scene_2_water_map_2[81:99] = [-1+scene_elevation_offset]*18
scene_2_ground_map[99:101] = [1+scene_elevation_offset]*2
scene_2_ground_map[108:125] = [2+scene_elevation_offset]*17
scene_2_ground_map[110:122] = [4+scene_elevation_offset]*12
scene_2_ground_map[122] = 3+scene_elevation_offset
scene_2_ground_map[125] = 1+scene_elevation_offset
scene_2_ground_map[131:150] = [4+scene_elevation_offset]*19
scene_2_player = Player(res = scene_resolution, initial_world_pos = (25, 7.5), z = 110)
# scene_2_player.flight_enabled = True
scene_2_door_offset = scene_resolution*51
scene_2_door = TexturedElement(pos = (2445 + scene_2_door_offset, 213),
                                z = 101,
                                size = (500*0.13, 500*0.13),
                                texture_path = "graphics/door_closed.png",
                                tag = "door")

scene_2_game_elements = [   scene_2_door,
                                                    TexturedElement(pos = (615, 213),
                                                        z = 101,
                                                        size = (500*0.13, 500*0.13),
                                                        texture_path = "graphics/door_closed.png"),
                                                    TexturedElement(pos = (2350+scene_2_door_offset, 280),
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
                                                        z = 11,
                                                        size = (window_size[0]*3.0, window_size[1]*0.8),
                                                        texture_path = "graphics/bg_2.png",
                                                        color = Color(0.2, 0.4, 0.15)),
                                                        parallax_z = 60),
                                                    Backdrop(element = TexturedElement(pos = (1100, 80),
                                                        z = 46,
                                                        size = (1414*0.8, 370*0.8),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.35, 0.55, 0.3)),
                                                        parallax_z = 0.4),
                                                    Backdrop(element = TexturedElement(pos = (1100, 80),
                                                        z = 46,
                                                        size = (1414*0.8, 370*0.8),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.3, 0.3, 0.9)),
                                                        parallax_z = 0.4),
                                                    Backdrop(element = TexturedElement(pos = (500, 75),
                                                        z = 44,
                                                        size = (-1414*0.55, 370*0.55),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.3, 0.5, 0.25)),
                                                        parallax_z = 1.4),
                                                    Backdrop(element = TexturedElement(pos = (500, 75),
                                                        z = 44,
                                                        size = (-1414*0.55, 370*0.55),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.2, 0.2, 0.8)),
                                                        parallax_z = 1.4),
                                                    Backdrop(element = TexturedElement(pos = (240, 61),
                                                        z = 40,
                                                        size = (1414*0.4, 370*0.4),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.25, 0.45, 0.2)),
                                                        parallax_z = 3.0),
                                                    Backdrop(element = TexturedElement(pos = (240, 61),
                                                        z = 40,
                                                        size = (1414*0.4, 370*0.4),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.15, 0.15, 0.75)),
                                                        parallax_z = 3.0),
                                                    Backdrop(element = TexturedElement(pos = (2100, 70),
                                                        z = 45,
                                                        size = (1414*0.9, 370*0.9),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.35, 0.55, 0.3)),
                                                        parallax_z = 0.5),
                                                    Backdrop(element = TexturedElement(pos = (2100, 70),
                                                        z = 45,
                                                        size = (1414*0.9, 370*0.9),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.3, 0.3, 0.9)),
                                                        parallax_z = 0.5),
                                                    Backdrop(element = TexturedElement(pos = (1400, 70),
                                                        z = 43,
                                                        size = (1414*0.55, 370*0.55),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.3, 0.5, 0.25)),
                                                        parallax_z = 1.6),
                                                    Backdrop(element = TexturedElement(pos = (1400, 70),
                                                        z = 43,
                                                        size = (1414*0.55, 370*0.55),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.25, 0.25, 0.85)),
                                                        parallax_z = 1.6),
                                                    Backdrop(element = TexturedElement(pos = (1050, 60),
                                                        z = 40,
                                                        size = (1414*0.3, 370*0.3),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.25, 0.45, 0.2)),
                                                        parallax_z = 3.4),
                                                    Backdrop(element = TexturedElement(pos = (1050, 60),
                                                        z = 40,
                                                        size = (1414*0.3, 370*0.3),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.2, 0.2, 0.8)),
                                                        parallax_z = 3.4),
                                                    Backdrop(element = TexturedElement(pos = (70-300, -80),
                                                        z = 5,
                                                        size = (532*1.4, 266*1.4),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 200),
                                                    Backdrop(element = TexturedElement(pos = (240-300, 30),
                                                        z = 9,
                                                        size = (532*1.0, 266*1.0),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 150),
                                                    Backdrop(element = TexturedElement(pos = (240-300, 30),
                                                        z = 9,
                                                        size = (532*1.0, 266*1.0),
                                                        texture_path = "graphics/mountain_cap.png",
                                                        color = Color(1, 1, 1)),
                                                        parallax_z = 150),
                                                    Backdrop(element = TexturedElement(pos = (445-300, -80),
                                                        z = 5,
                                                        size = (532*1.2, 266*1.2),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 200),
                                                    Backdrop(element = TexturedElement(pos = (595, -80),
                                                        z = 5,
                                                        size = (532*1.3, 266*1.3),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 200),
                                                    Backdrop(element = TexturedElement(pos = (-10, 60),
                                                        z = 43,
                                                        size = (1466*0.6, 519*0.6),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.275, 0.475, 0.225)),
                                                        parallax_z = 2),
                                                    Backdrop(element = TexturedElement(pos = (800, 65),
                                                        z = 42,
                                                        size = (-1466*0.58, 519*0.58),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.275, 0.475, 0.225)),
                                                        parallax_z = 2.1),
                                                    Backdrop(element = TexturedElement(pos = (1750, 70),
                                                        z = 42,
                                                        size = (1466*0.62, 519*0.62),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.275, 0.475, 0.225)),
                                                        parallax_z = 2.15),
                                                    Terrain(scene_2_ground_map,
                                                        z = 100,
                                                        color = Color(0, 0, 0),
                                                        res = scene_resolution),
                                                    Terrain(scene_2_water_map_1,
                                                        z = 111,
                                                        color = Color(0.35, 0.35, 0.95),
                                                        res = scene_resolution,
                                                        type = "water"),
                                                    Terrain(scene_2_water_map_2,
                                                        z = 111,
                                                        color = Color(0.35, 0.35, 0.95),
                                                        res = scene_resolution,
                                                        type = "water"),
                                                    Pickup(TexturedElement(pos = (42.75*scene_resolution, 300),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Pickup(TexturedElement(pos = (69*scene_resolution, 14*scene_resolution),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Platform(((39, 6), (40, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = False,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((44.5, 6), (45.5, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((84, 6), (85, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = False,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((89, 6), (90, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((94, 6), (95, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = False,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                ]
scene_2_enemies = [
    Enemy(res = scene_resolution, initial_world_pos = (58, 7), radius = 40, z = 110, moves_per_beat = ["stop", "left", "stop", "right", "stop", "right", "stop", "left"], has_key = False),
    Enemy(res = scene_resolution, initial_world_pos = (113, 11), radius = 40, z = 110, moves_per_beat = ["stop", "right", "stop", "right", "stop", "right", "stop", "left", "stop", "left", "stop", "left"], has_key = True)
]
scene_2_game_elements.extend(scene_2_enemies)
scene_2_UI_elements = []
scene_2_UI_elements.extend(keys_UI)
scene_2_UI_elements.extend(fight_UI)

scene_2_audio_controller = AudioController(level = 0, bpm = 120, elements = scene_2_game_elements)
scene_2_camera_bounds = ((26, 6.5), (121, 9.5))
scene_2_camera = Camera(zoom_factor = 1.1, initial_world_target = scene_2_player.world_pos, speed = 1.05, bounds = scene_2_camera_bounds)
scene_2 = Scene(initial_game_elements = scene_2_game_elements, initial_UI_elements = scene_2_UI_elements, ground_map = scene_2_ground_map, game_camera = scene_2_camera, res = scene_resolution, audio_controller = scene_2_audio_controller, player = scene_2_player)

# scene 3

scene_3_water_map_1 = [0]*155
scene_3_water_map_2 = [0]*155
scene_3_ground_map = [0+scene_elevation_offset]*155
scene_3_ground_map[0:22] = [4+scene_elevation_offset]*22
scene_3_ground_map[32:34] = [1+scene_elevation_offset]*2
scene_3_ground_map[56:58] = [1+scene_elevation_offset]*2
scene_3_ground_map[34:56] = [-5+scene_elevation_offset]*23
scene_3_water_map_1[34:56] = [-1+scene_elevation_offset]*23
scene_3_ground_map[68:70] = [1+scene_elevation_offset]*2
scene_3_ground_map[70:93] = [-5+scene_elevation_offset]*23
scene_3_water_map_1[70:93] = [-1+scene_elevation_offset]*23
scene_3_ground_map[93:95] = [1+scene_elevation_offset]*2
scene_3_ground_map[103:107] = [1+scene_elevation_offset]*4
scene_3_ground_map[105] = 2+scene_elevation_offset
scene_3_ground_map[107] = 3+scene_elevation_offset
scene_3_ground_map[108] = 1+scene_elevation_offset
scene_3_ground_map[110] = -1+scene_elevation_offset
scene_3_ground_map[123:155] = [4+scene_elevation_offset]*32
scene_3_player = Player(res = scene_resolution, initial_world_pos = (25, 7.5), z = 110)
# scene_3_player.flight_enabled = True
scene_3_door_offset = scene_resolution*43
scene_3_door = TexturedElement(pos = (2445 + scene_3_door_offset, 213),
                                z = 101,
                                size = (500*0.13, 500*0.13),
                                texture_path = "graphics/door_closed.png",
                                tag = "door")

scene_3_game_elements = [   scene_3_door,
                                                    TexturedElement(pos = (615, 213),
                                                        z = 101,
                                                        size = (500*0.13, 500*0.13),
                                                        texture_path = "graphics/door_closed.png"),
                                                    TexturedElement(pos = (2350+scene_3_door_offset, 280),
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
                                                        z = 11,
                                                        size = (window_size[0]*3.0, window_size[1]*0.8),
                                                        texture_path = "graphics/bg_2.png",
                                                        color = Color(0.2, 0.4, 0.15)),
                                                        parallax_z = 60),
                                                    Backdrop(element = TexturedElement(pos = (-100, -80),
                                                        z = 5,
                                                        size = (532*1.3, 266*1.3),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 200),
                                                    Backdrop(element = TexturedElement(pos = (50, -90),
                                                        z = 5,
                                                        size = (532*1.2, 266*1.2),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 200),
                                                    Backdrop(element = TexturedElement(pos = (149, -100),
                                                        z = 5,
                                                        size = (532*1.1, 266*1.1),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 200),
                                                    Backdrop(element = TexturedElement(pos = (420, -10),
                                                        z = 5,
                                                        size = (532*0.7, 266*0.7),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 200),
                                                    Backdrop(element = TexturedElement(pos = (560, -10),
                                                        z = 5,
                                                        size = (532*1.25, 266*1.25),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.35, 0.35, 0.35)),
                                                        parallax_z = 200),
                                                    Backdrop(element = TexturedElement(pos = (560, -10),
                                                        z = 5,
                                                        size = (532*1.25, 266*1.25),
                                                        texture_path = "graphics/mountain_cap.png",
                                                        color = Color(1, 1, 1)),
                                                        parallax_z = 200),
                                                    Backdrop(element = TexturedElement(pos = (555, -40),
                                                        z = 12,
                                                        size = (532*1.0, 266*1.0),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.375, 0.375, 0.375)),
                                                        parallax_z = 50),
                                                    Backdrop(element = TexturedElement(pos = (680, -40),
                                                        z = 13,
                                                        size = (532*1.1, 266*1.1),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.4, 0.4, 0.4)),
                                                        parallax_z = 25),
                                                    Backdrop(element = TexturedElement(pos = (570, -90),
                                                        z = 14,
                                                        size = (532*1.15, 266*1.15),
                                                        texture_path = "graphics/mountain.png",
                                                        color = Color(0.425, 0.425, 0.425)),
                                                        parallax_z = 15),
                                                    Backdrop(element = TexturedElement(pos = (600, 60),
                                                        z = 40,
                                                        size = (-1414*0.8, 370*0.8),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.35, 0.55, 0.3)),
                                                        parallax_z = 0.5),
                                                    Backdrop(element = TexturedElement(pos = (600, 60),
                                                        z = 40,
                                                        size = (-1414*0.8, 370*0.8),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.25, 0.25, 0.85)),
                                                        parallax_z = 0.5),
                                                    Backdrop(element = TexturedElement(pos = (1900, 40),
                                                        z = 40,
                                                        size = (1414*0.95, 370*0.95),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.35, 0.55, 0.3)),
                                                        parallax_z = 0.5),
                                                    Backdrop(element = TexturedElement(pos = (1900, 40),
                                                        z = 40,
                                                        size = (1414*0.95, 370*0.95),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.25, 0.25, 0.85)),
                                                        parallax_z = 0.5),
                                                    Backdrop(element = TexturedElement(pos = (1350, 25),
                                                        z = 39,
                                                        size = (1414*0.8, 370*0.8),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.325, 0.525, 0.275)),
                                                        parallax_z = 1.5),
                                                    Backdrop(element = TexturedElement(pos = (1350, 25),
                                                        z = 39,
                                                        size = (1414*0.8, 370*0.8),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.225, 0.225, 0.825)),
                                                        parallax_z = 1.5),
                                                    Backdrop(element = TexturedElement(pos = (750, 67),
                                                        z = 39,
                                                        size = (1466*0.48, 519*0.48),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.325, 0.525, 0.275)),
                                                        parallax_z = 1.5),
                                                    Backdrop(element = TexturedElement(pos = (150, 35),
                                                        z = 39,
                                                        size = (-1414*0.6, 370*0.6),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.325, 0.525, 0.275)),
                                                        parallax_z = 1.5),
                                                    Backdrop(element = TexturedElement(pos = (150, 35),
                                                        z = 39,
                                                        size = (-1414*0.6, 370*0.6),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.225, 0.225, 0.825)),
                                                        parallax_z = 1.5),
                                                    Backdrop(element = TexturedElement(pos = (-170, 45),
                                                        z = 38,
                                                        size = (-1414*0.45, 370*0.45),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.3, 0.5, 0.25)),
                                                        parallax_z = 4.0),
                                                    Backdrop(element = TexturedElement(pos = (-170, 45),
                                                        z = 38,
                                                        size = (-1414*0.45, 370*0.45),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.2, 0.2, 0.8)),
                                                        parallax_z = 4.0),
                                                    Backdrop(element = TexturedElement(pos = (920, 35),
                                                        z = 38,
                                                        size = (1414*0.4, 370*0.4),
                                                        texture_path = "graphics/hill_2.png",
                                                        color = Color(0.3, 0.5, 0.25)),
                                                        parallax_z = 4.0),
                                                    Backdrop(element = TexturedElement(pos = (920, 35),
                                                        z = 38,
                                                        size = (1414*0.4, 370*0.4),
                                                        texture_path = "graphics/hill_2_water.png",
                                                        color = Color(0.2, 0.2, 0.8)),
                                                        parallax_z = 4.0),
                                                    Backdrop(element = TexturedElement(pos = (120, 32),
                                                        z = 37,
                                                        size = (1466*0.35, 519*0.35),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.275, 0.475, 0.225)),
                                                        parallax_z = 6.5),
                                                    Backdrop(element = TexturedElement(pos = (400, 33),
                                                        z = 36,
                                                        size = (-1466*0.34, 519*0.34),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.27, 0.47, 0.22)),
                                                        parallax_z = 7.0),
                                                    Backdrop(element = TexturedElement(pos = (990, 15),
                                                        z = 36,
                                                        size = (1466*0.34, 519*0.34),
                                                        texture_path = "graphics/hill_1.png",
                                                        color = Color(0.27, 0.47, 0.22)),
                                                        parallax_z = 7.0),
                                                    Terrain(scene_3_ground_map,
                                                        z = 100,
                                                        color = Color(0, 0, 0),
                                                        res = scene_resolution),
                                                    Terrain(scene_3_water_map_1,
                                                        z = 111,
                                                        color = Color(0.35, 0.35, 0.95),
                                                        res = scene_resolution,
                                                        type = "water"),
                                                    Terrain(scene_3_water_map_2,
                                                        z = 111,
                                                        color = Color(0.35, 0.35, 0.95),
                                                        res = scene_resolution,
                                                        type = "water"),
                                                    Platform(((37, 6), (38, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = False,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((42, 6), (43, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((47, 6), (48, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = False,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((52, 6), (53, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    JumpPad(world_pos = (63.5, 7),
                                                        z = 99,
                                                        color = Color(0, 0, 0),
                                                        beats = [2, 4],
                                                        res = scene_resolution,
                                                        sound_path = "audio/jumppad.wav"),
                                                    Platform(((74, 6), (79, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [0],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Pickup(TexturedElement(pos = (82*scene_resolution, 10.5*scene_resolution),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                    Platform(((84, 6), (89, 6)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [0],
                                                        res = scene_resolution,
                                                        active = False,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((62, 13), (64, 13)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [2, 4],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((67, 14), (68, 14)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = False,
                                                        beats = [],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((71, 14), (85, 14)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = False,
                                                        beats = [],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((72, 13.5), (84, 13.5)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = False,
                                                        beats = [],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((89, 14), (90, 14)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [0, 4],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Platform(((94, 14), (95, 14)),
                                                        type = "dirt",
                                                        z = 100,
                                                        musical = True,
                                                        beats = [1, 3, 5, 7],
                                                        res = scene_resolution,
                                                        active = True,
                                                        sound_path = "audio/platform_sfx.wav"),
                                                    Pickup(TexturedElement(pos = (101*scene_resolution, 15.5*scene_resolution),
                                                        size = (166*0.091, 400*0.091),
                                                        texture_path = "graphics/key.png"), z = 110, radius = 20),
                                                ]
scene_3_enemies = [
    Enemy(res = scene_resolution, initial_world_pos = (116, 7), radius = 40, z = 110, moves_per_beat = ["stop", "stop", "stop", "right", "stop", "stop", "stop", "left"], has_key = True)
]
scene_3_game_elements.extend(scene_3_enemies)
scene_3_UI_elements = []
scene_3_UI_elements.extend(keys_UI)
scene_3_UI_elements.extend(fight_UI)

scene_3_audio_controller = AudioController(level = 0, bpm = 120, elements = scene_3_game_elements)
scene_3_camera_bounds = ((31.5, 6.5), (111, 11.5))
scene_3_camera = Camera(zoom_factor = 1.1, initial_world_target = scene_3_player.world_pos, speed = 1.05, bounds = scene_3_camera_bounds)
scene_3 = Scene(initial_game_elements = scene_3_game_elements, initial_UI_elements = scene_3_UI_elements, ground_map = scene_3_ground_map, game_camera = scene_3_camera, res = scene_resolution, audio_controller = scene_3_audio_controller, player = scene_3_player)

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

# panel 1

panel_1_objects = [
    (TexturedElement(pos = (window_size[0]/2, (window_size[1]/2)+30), z = 1, size = (1476*0.5, 69*0.5), texture_path = "graphics/text_1.png"), 0.9, None),
    (TexturedElement(pos = (window_size[0]/2, (window_size[1]/2)-30), z = 1, size = (1832*0.5, 69*0.5), texture_path = "graphics/text_2.png"), 3.6, None)
]
panel_1_camera = Camera(zoom_factor = 1.0, initial_world_target = (0, 0), speed = 10.0)
panel_1 = Panel(game_camera = panel_1_camera, timed_objects = panel_1_objects, res = scene_resolution, end_time = 8.0, next_scene_index = 2)

scenes = [menu_1, panel_1, scene_1, scene_2, scene_3, scene_0]
# scenes = [scene_3]
