from math import *
from core import *
from kivy.graphics import Rectangle, Ellipse, Color, Mesh
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

class Player(object):
    def __init__(self, res = 20.0, initial_world_pos = (0, 0), z = 10):
        self.world_size = (0.8, 0.5)
        self.res = res
        self.world_pos = initial_world_pos # world units are measured by res
        self.world_vel = (0, 0)
        self.z = z

        self.element = TexturedElement(pos = (self.world_pos[0]*self.res, self.world_pos[1]*self.res), tag = "player", z = self.z, size = (self.res, self.res), texture_path = "graphics/player_stand.png")

    def on_update(self, dt):
        self.world_pos = (self.world_pos[0] + self.world_vel[0], self.world_pos[1] + self.world_vel[1])


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


class Terrain(object):
    def __init__(self, map, type = "dirt", z = 0, color = None, res = 20.0):
        self.type = type
        self.map = map # numpy height array
        self.res = res

        # placeholder values
        self.z = z
        self.color = color
        if color == None:
            self.color = Color(1, 0, 0)
        self.vertices = []

        # builds mesh
        self.shape = InstructionGroup()
        for x in range(len(self.map)):
            vertices = [
                            x*self.res, 0, 0, 0,
                            x*self.res, self.map[x]*self.res, 0, 0, 
                            (x+0.1)*self.res, self.map[x]*self.res, 0, 0, 
                            (x+0.9)*self.res, self.map[x]*self.res, 0, 0, 
                            (x+1)*self.res, self.map[x]*self.res, 0, 0, 
                            (x+1)*self.res, 0, 0, 0]
            if x-1 > 0:
                if self.map[x-1] < self.map[x]:
                    vertices[5] += -self.res*0.1
                elif self.map[x-1] > self.map[x]:
                    vertices[5] += self.res*0.1
            if x+1 < len(self.map):
                if self.map[x+1] < self.map[x]:
                    vertices[17] += -self.res*0.1
                elif self.map[x+1] > self.map[x]:
                    vertices[17] += self.res*0.1
            indices = [0, 1, 2, 3, 4, 5]
            self.shape.add(Mesh(vertices=vertices, indices=indices, mode="triangle_fan"))

    def on_update(self, dt):
        pass
