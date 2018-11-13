import math
from core import *
from kivy.graphics import Rectangle, Ellipse, Color
from kivy.core.image import Image
from kivy.graphics.instructions import InstructionGroup


class Element(object):
    def __init__(self, pos = (0, 0), vel = (0, 0), tag = "", color = None, z = 0):
        self.pos = pos
        self.vel = vel
        self.tag = tag
        self.color = color
        self.z = z
        self.shape = None

        if color == None:
            self.color = Color(1, 1, 1)

    def on_update(self, dt):
        self.pos = (self.pos[0]+self.vel[0]*dt, self.pos[1]+self.vel[1]*dt)


class TexturedElement(Element):
    def __init__(self, pos = (0, 0), vel = (0, 0), tag = "", color = None, z = 0, size = (10, 10), texture_path = ""):
        Element.__init__(self, pos, vel, tag, color, z)
        self.size = size
        self.texture_path = texture_path
        self.shape = Rectangle(pos=((self.pos[0]-(self.size[0]/2))*retina_multiplier, (self.pos[1]-(self.size[1]/2))*retina_multiplier),size=(self.size[0]*retina_multiplier, self.size[1]*retina_multiplier))

        if texture_path != "":
            self.shape.texture = Image(texture_path).texture

    def change_texture(self, new_texture_path):
        self.texture_path = new_texture_path
        if self.texture_path != "":
            self.shape.texture = Image(self.texture_path).texture

    def on_update(self, dt):
        super().on_update(dt)
        self.shape.pos = ((self.pos[0]-(self.size[0]/2))*retina_multiplier, (self.pos[1]-(self.size[1]/2))*retina_multiplier)
        self.shape.size = (self.size[0]*retina_multiplier, self.size[1]*retina_multiplier)


class GeometricElement(Element):
    def __init__(self, pos = (0, 0), vel = (0, 0), tag = "", color = None, z = 0, size = (10, 10), shape = None):
        Element.__init__(self, pos, vel, tag, color, z)
        self.size = size
        self.shape = shape
        if self.shape == None:
            self.shape = Rectangle(pos=((self.pos[0]-(self.size[0]/2))*retina_multiplier, (self.pos[1]-(self.size[1]/2))*retina_multiplier),size=(self.size[0]*retina_multiplier, self.size[1]*retina_multiplier))

    def change_shape(self, new_shape):
        self.shape = new_shape

    def on_update(self, dt):
        super().on_update(dt)
        self.shape.pos = ((self.pos[0]-(self.size[0]/2))*retina_multiplier, (self.pos[1]-(self.size[1]/2))*retina_multiplier)
        self.shape.size = (self.size[0]*retina_multiplier, self.size[1]*retina_multiplier)


# element substitutes
#     requires implementation of self.z, self.shape, self.color, self.on_update()

class ElementGroup(object):
    def __init__(self, elements = [], z = 0, color = None):
        self.elements = elements
        self.z = z
        self.color = color
        if color == None:
            self.color = Color(1, 1, 1)

        self.shape = InstructionGroup()
        for element in self.elements:
            self.shape.add(element)

    def on_update(self, dt):
        for element in self.elements:
            element.on_update(dt)


class Backdrop(object):
    def __init__(self, element, parallax_z = 0, shading_function = None):
        self.element = element
        self.shading_function = shading_function
        self.parallax_z = parallax_z

        self.pos = (self.element.pos[0], self.element.pos[1])
        self.z = self.element.z
        self.color = self.element.color
        self.shape = self.element.shape

    def process_position(self, camera_parallax_z):
        distance_factor = 1/max(math.fabs(camera_parallax_z - (self.parallax_z+1)), 1)
        self.pos = (self.element.pos[0]*distance_factor + window_size[0]*0.5*(1-distance_factor), self.element.pos[1]*distance_factor + window_size[1]*0.5*(1-distance_factor))

    def on_update(self, dt):
        for element in self.elements:
            element.on_update(dt)

