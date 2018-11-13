from objects import *
from core import *
from scene_manager import *
from kivy.core.window import Window

middle = (window_size[0]/2, window_size[1]/2)

scene_1_game_elements = [
                                                    TexturedElement(pos = middle,
                                                        z = 0,
                                                        size = window_size,
                                                        texture_path = "graphics/bg_1.png")
                                                ]
scene_1 = Scene(initial_game_elements = scene_1_game_elements, initial_UI_elements = [])

scenes = [scene_1]