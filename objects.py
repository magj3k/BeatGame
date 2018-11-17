import numpy as np
import random
from math import *
from core import *
from kivy.graphics import Rectangle, Ellipse, Color, Mesh
from kivy.core.image import Image
from kivy.graphics.instructions import InstructionGroup


class Element(object):
    def __init__(self, pos = (0, 0), vel = (0, 0), tag = "", color = None, z = 0, musical = False):
        self.pos = pos
        self.vel = vel
        self.tag = tag
        self.color = color
        self.z = z
        self.shape = None
        self.musical = musical

        if color == None:
            self.color = Color(1, 1, 1)

    def on_update(self, dt):
        self.pos = (self.pos[0]+self.vel[0]*dt, self.pos[1]+self.vel[1]*dt)


class TexturedElement(Element):
    def __init__(self, pos = (0, 0), vel = (0, 0), tag = "", color = None, z = 0, size = (10, 10), texture_path = "", musical = False):
        Element.__init__(self, pos, vel, tag, color, z, musical)
        self.size = size
        self.texture_path = texture_path
        self.shape = Rectangle(pos=((self.pos[0]-(self.size[0]/2))*retina_multiplier, (self.pos[1]-(self.size[1]/2))*retina_multiplier),size=(self.size[0]*retina_multiplier, self.size[1]*retina_multiplier))

        if texture_path != "":
            self.shape.texture = Image(texture_path).texture

    def change_texture(self, new_texture_path):
        self.texture_path = new_texture_path
        if self.texture_path != "":
            self.shape.texture = Image(self.texture_path).texture

    def on_update(self, dt, cam_scalar, cam_offset):
        super().on_update(dt)
        self.shape.pos = (((self.pos[0]-(self.size[0]/2))*retina_multiplier)*cam_scalar + cam_offset[0], ((self.pos[1]-(self.size[1]/2))*retina_multiplier)*cam_scalar + cam_offset[1])
        self.shape.size = (self.size[0]*retina_multiplier*cam_scalar, self.size[1]*retina_multiplier*cam_scalar)


class GeometricElement(Element):
    def __init__(self, pos = (0, 0), vel = (0, 0), tag = "", color = None, z = 0, size = (10, 10), shape = None, musical = False):
        Element.__init__(self, pos, vel, tag, color, z, musical)
        self.size = size
        self.shape = shape
        if self.shape == None:
            self.shape = Rectangle(pos=((self.pos[0]-(self.size[0]/2))*retina_multiplier, (self.pos[1]-(self.size[1]/2))*retina_multiplier),size=(self.size[0]*retina_multiplier, self.size[1]*retina_multiplier))

    def change_shape(self, new_shape):
        self.shape = new_shape

    def on_update(self, dt, cam_scalar, cam_offset):
        super().on_update(dt)
        self.shape.pos = (((self.pos[0]-(self.size[0]/2))*retina_multiplier)*cam_scalar + cam_offset[0], ((self.pos[1]-(self.size[1]/2))*retina_multiplier)*cam_scalar + cam_offset[1])
        self.shape.size = (self.size[0]*retina_multiplier*cam_scalar, self.size[1]*retina_multiplier*cam_scalar)


# element substitutes
#     requires implementation of self.z, self.shape, self.color, self.on_update(dt, cam_scalar, cam_offset), self.musical, self.tag

class ElementGroup(object):
    def __init__(self, elements = [], z = 0, color = None, musical = False, tag = ""):
        self.elements = elements
        self.musical = musical
        self.z = z
        self.tag = tag
        self.color = color
        if color == None:
            self.color = Color(1, 1, 1)

        self.shape = InstructionGroup()
        for element in self.elements:
            self.shape.add(element)

    def on_update(self, dt, cam_scalar, cam_offset):
        for element in self.elements:
            element.on_update(dt)


class Backdrop(object):
    def __init__(self, element, parallax_z = 0, shading_function = None, musical = False, tag = ""):
        self.element = element
        self.shading_function = shading_function
        self.parallax_z = parallax_z
        self.tag = tag

        self.pos = (self.element.pos[0], self.element.pos[1])
        self.z = self.element.z
        self.color = self.element.color
        self.shape = self.element.shape
        self.musical = musical

    # modifies camera-based scaling and offset depending on self.parallax_z
    def on_update(self, dt, cam_scalar, cam_offset):
        new_cam_scalar = cam_scalar*(1/(self.parallax_z+1))
        new_cam_offset_parts = ((cam_offset[0]-(window_size[0]*0.5*retina_multiplier))/cam_scalar, (cam_offset[1]-(window_size[1]*0.5*retina_multiplier))/cam_scalar)
        new_cam_offset = (new_cam_offset_parts[0]*new_cam_scalar + (window_size[0]*0.5*retina_multiplier), new_cam_offset_parts[1]*new_cam_scalar + (window_size[1]*0.5*retina_multiplier))
        self.element.on_update(dt, cam_scalar, new_cam_offset)


class Terrain(object): # mesh-based representation of a ground map
    def __init__(self, map, type = "dirt", z = 0, color = None, res = 20.0, tag = ""):
        self.type = type
        self.map = map # numpy height array
        self.res = res
        self.musical = False
        self.tag = tag

        # placeholder values
        self.z = z
        self.color = color
        if color == None:
            self.color = Color(1, 0, 0)
        self.vertices = []

        # builds mesh
        self.shape = InstructionGroup()
        self.mesh_vertices = []
        self.meshes = []

        last_height = -1
        current_vertices = []
        for x in range(len(self.map)+1):
            if x < len(self.map) and last_height != self.map[x]:
                if len(current_vertices) > 0: # saves preexisting mesh
                    current_vertices.extend([
                        (x-0.15)*self.res*retina_multiplier, last_height*self.res*retina_multiplier, 0, 0,
                        (x)*self.res*retina_multiplier, last_height*self.res*retina_multiplier, 0, 0,
                        (x)*self.res*retina_multiplier, -10*self.res*retina_multiplier, 0, 0])

                    if last_height < self.map[x]:
                        current_vertices[17] += 0.15*self.res*retina_multiplier
                    elif last_height > self.map[x]:
                        current_vertices[17] += -0.15*self.res*retina_multiplier
                    if self.type == "water":
                        current_vertices[12] += 0.35*self.res*retina_multiplier
                        current_vertices[16] += 0.35*self.res*retina_multiplier
                        current_vertices[20] += 0.35*self.res*retina_multiplier
                    
                    self.mesh_vertices.append(current_vertices[:])
                    self.meshes.append(Mesh(vertices=self.mesh_vertices[-1], indices=[0, 1, 2, 3, 4, 5], mode="triangle_fan"))
                    self.shape.add(self.meshes[-1])

                if self.map[x] != 0:
                    current_vertices = [
                        x*self.res*retina_multiplier, -10*self.res*retina_multiplier, 0, 0,
                        x*self.res*retina_multiplier, self.map[x]*self.res*retina_multiplier, 0, 0,
                        (x+0.15)*self.res*retina_multiplier, self.map[x]*self.res*retina_multiplier, 0, 0]
                    if x-1 >= 0 and self.map[x-1] > self.map[x] and self.type == "dirt":
                        current_vertices[5] += 0.15*self.res*retina_multiplier
                    elif x-1 >= 0 and self.map[x-1] < self.map[x] and self.type == "dirt":
                        current_vertices[5] += -0.15*self.res*retina_multiplier
                last_height = self.map[x]
            elif x == len(self.map) and len(current_vertices) > 0:
                current_vertices.extend([
                    (x-0.15)*self.res*retina_multiplier, last_height*self.res*retina_multiplier, 0, 0,
                    (x)*self.res*retina_multiplier, last_height*self.res*retina_multiplier, 0, 0,
                    (x)*self.res*retina_multiplier, -10*self.res*retina_multiplier, 0, 0])

                self.mesh_vertices.append(current_vertices[:])
                self.meshes.append(Mesh(vertices=self.mesh_vertices[-1], indices=[0, 1, 2, 3, 4, 5], mode="triangle_fan"))
                self.shape.add(self.meshes[-1])

    def on_update(self, dt, cam_scalar, cam_offset):
        for i in range(len(self.meshes)):
            processed_vertices = self.mesh_vertices[i][:]
            for j in [0, 4, 8, 12, 16, 20]:
                processed_vertices[j] = (processed_vertices[j]*cam_scalar) + cam_offset[0]
            for j in [1, 5, 9, 13, 17, 21]:
                processed_vertices[j] = (processed_vertices[j]*cam_scalar) + cam_offset[1]
            self.meshes[i].vertices = processed_vertices


class Platform(object):
    def __init__(self, cell_bounds, type = "dirt", z = 0, musical = False, beats = [1, 3], texture = "", res = 20.0, tag = ""):
        self.type = type
        if self.type == "mech":
            musical = True
        self.musical = musical
        self.beats = beats
        self.texture = texture
        self.cell_bounds = cell_bounds # in world_pos coordinate system
        self.z = z
        self.res = res
        self.tag = tag

        # musical elements
        self.t = 0

        # creates element for platform
        self.element = None
        if self.type == "dirt":
            self.vertices = [
                (self.cell_bounds[0][0])*self.res*retina_multiplier, (self.cell_bounds[0][1]+0.15)*self.res*retina_multiplier, 0, 0,
                (self.cell_bounds[0][0])*self.res*retina_multiplier, (self.cell_bounds[0][1]+0.85)*self.res*retina_multiplier, 0, 0,
                (self.cell_bounds[0][0]+0.15)*self.res*retina_multiplier, (self.cell_bounds[0][1]+1)*self.res*retina_multiplier, 0, 0,
                (self.cell_bounds[1][0]+0.85)*self.res*retina_multiplier, (self.cell_bounds[1][1]+1)*self.res*retina_multiplier, 0, 0,
                (self.cell_bounds[1][0]+1)*self.res*retina_multiplier, (self.cell_bounds[1][1]+0.85)*self.res*retina_multiplier, 0, 0,
                (self.cell_bounds[1][0]+1)*self.res*retina_multiplier, (self.cell_bounds[1][1]+0.15)*self.res*retina_multiplier, 0, 0,
                (self.cell_bounds[1][0]+0.85)*self.res*retina_multiplier, (self.cell_bounds[1][1])*self.res*retina_multiplier, 0, 0,
                (self.cell_bounds[0][0]+0.15)*self.res*retina_multiplier, (self.cell_bounds[0][1])*self.res*retina_multiplier, 0, 0]
            indices = [0, 1, 2, 3, 4, 5, 6, 7]
            self.shape = Mesh(vertices=self.vertices, indices=indices, mode="triangle_fan")
            self.color = Color(0, 0, 0)
        elif self.type == "mech":
            self.shape = self.element.shape
            self.color = self.element.color

    def on_update(self, dt, cam_scalar, cam_offset):
        self.t += dt
        if self.type != "dirt":
            self.element.on_update(dt, cam_scalar, cam_offset)
        else:
            processed_vertices = self.vertices[:]
            for j in [0, 4, 8, 12, 16, 20, 24, 28]:
                processed_vertices[j] = (processed_vertices[j]*cam_scalar) + cam_offset[0]
            for j in [1, 5, 9, 13, 17, 21, 25, 29]:
                processed_vertices[j] = (processed_vertices[j]*cam_scalar) + cam_offset[1]
            self.shape.vertices = processed_vertices


class Pickup(object):
    def __init__(self, element, z = 10, radius = 10, musical = False, tag = ""): # self.z, self.shape, self.color, self.on_update(), self.musical
        self.element = element
        self.color = self.element.color
        self.initial_pos = self.element.pos
        self.z = z
        self.shape = self.element.shape
        self.radius = radius*retina_multiplier
        self.t = random.random()*3.14159*2.0
        self.musical = musical
        self.tag = tag

    def on_update(self, dt, cam_scalar, cam_offset):
        self.t += dt
        self.element.pos = (self.initial_pos[0], self.initial_pos[1] + (np.sin(self.t*6.5)*2*retina_multiplier))
        self.element.on_update(dt, cam_scalar, cam_offset)



# element-substitute world-coordinated objects, 
#     requires implementation of self.world_pos, self.world_size

class Player(object):
    def __init__(self, res = 20.0, initial_world_pos = (0, 0), z = 10, tag = ""):
        self.world_size = (0.9, 1.0)
        self.res = res
        self.world_pos = initial_world_pos # world units are measured by res
        self.world_vel = (0, 0)
        self.z = z
        self.direction = "left" # or "right"
        self.musical = False
        self.on_ground = True
        self.last_respawnable_x = self.world_pos[0]
        self.controls_disabled = False
        self.tag = tag

        # animations
        self.valid_animation_states = ["standing", "run_left", "run_right", "jump_right", "jump_left"]
        self.animation_state = "standing"
        self.animation_t = 0
        self.animation_frame = 0
        self.animation_frame_duration = 0.1

        self.element = TexturedElement(pos = (self.world_pos[0]*self.res, self.world_pos[1]*self.res), tag = "player", z = self.z, size = (self.res*2, self.res*2), texture_path = "graphics/player_stand.png")

    def set_animation_state(self, new_state): # follow this call with self.process_animation()
        if new_state in self.valid_animation_states and new_state != self.animation_state:
            self.animation_state = new_state
            self.animation_t = 0
            self.animation_frame = -1

            if self.animation_state == "standing" or self.animation_state == "jump_right" or self.animation_state == "jump_left":
                self.animation_frame_duration = 30.0
            elif self.animation_state == "run_right" or self.animation_state == "run_left":
                self.animation_frame_duration = 0.075

    def process_animation(self, dt):
        self.animation_t += dt
        next_frame = int(self.animation_t/self.animation_frame_duration)
        if next_frame != self.animation_frame:
            self.animation_frame = next_frame

            # update texture
            if self.animation_state == "run_right":
                if self.animation_frame % 3 == 0:
                    self.element.change_texture("graphics/player_run_1.png")
                elif self.animation_frame % 3 == 1:
                    self.element.change_texture("graphics/player_run_2.png")
                elif self.animation_frame % 3 == 2:
                    self.element.change_texture("graphics/player_run_3.png")
            elif self.animation_state == "run_left":
                if self.animation_frame % 3 == 0:
                    self.element.change_texture("graphics/player_run_1_r.png")
                elif self.animation_frame % 3 == 1:
                    self.element.change_texture("graphics/player_run_2_r.png")
                elif self.animation_frame % 3 == 2:
                    self.element.change_texture("graphics/player_run_3_r.png")
            elif self.animation_state == "jump_right":
                self.element.change_texture("graphics/player_jump.png")
            elif self.animation_state == "jump_left":
                self.element.change_texture("graphics/player_jump_r.png")
            else:
                self.element.change_texture("graphics/player_stand.png")

    def on_update(self, dt, ground_map, active_keys, cam_scalar, cam_offset, audio_controller, platforms = []):

        # position update
        target_x_vel = 0
        if self.controls_disabled == False:
            if active_keys["right"] == True:
                target_x_vel += 9.0
                self.set_animation_state("run_right")
            if active_keys["left"] == True:
                target_x_vel += -9.0
                self.set_animation_state("run_left")
        if active_keys["left"] == False and active_keys["right"] == False:
            self.set_animation_state("standing")

        next_vel = (self.world_vel[0]+((target_x_vel - self.world_vel[0])*18.0*dt), self.world_vel[1] - (60.0*dt))
        next_pos = (self.world_pos[0] + self.world_vel[0]*dt, self.world_pos[1] + self.world_vel[1]*dt)

        # ground & wall collisions
        if self.world_vel[1] < 0 or self.world_vel[0] != 0:
            current_player_x_index = min(max(int(self.world_pos[0]), 0), len(ground_map)-1)
            next_player_x_index = min(max(int(next_pos[0]), 0), len(ground_map)-1)
            highest_ground = ground_map[next_player_x_index]

            left_side = next_pos[0] - self.world_size[0]*0.5
            right_side = next_pos[0] + self.world_size[0]*0.5
            left_height = ground_map[next_player_x_index]
            right_height = ground_map[next_player_x_index]
            next_player_height = next_pos[1]-self.world_size[1]
            current_player_height = self.world_pos[1]-self.world_size[1]

            if fabs(current_player_height - ground_map[current_player_x_index]) < 0.05:
                self.on_ground = True
                if current_player_height > 2.0:
                    self.last_respawnable_x = current_player_x_index+0.5
                self.controls_disabled = False
            else:
                self.on_ground = False

            # ground collisions
            if next_player_x_index - 1 > 0:
                left_height = ground_map[next_player_x_index - 1]
                if left_side < next_player_x_index and current_player_height >= left_height:
                    highest_ground = max(highest_ground, ground_map[next_player_x_index - 1])
            if next_player_x_index + 1 < len(ground_map):
                right_height = ground_map[next_player_x_index + 1]
                if right_side > next_player_x_index+1 and current_player_height >= right_height:
                    highest_ground = max(highest_ground, ground_map[next_player_x_index + 1])

            # platforms
            for platform in platforms:
                if right_side > platform.cell_bounds[0][0] and left_side < platform.cell_bounds[1][0]+1 and current_player_height > (1+platform.cell_bounds[0][1]+platform.cell_bounds[1][1])/2:
                    highest_ground = max(highest_ground, 1+(platform.cell_bounds[0][1]+platform.cell_bounds[1][1])/2)

            if next_player_height < highest_ground: # is true whenever resting on ground
                next_pos = (next_pos[0], highest_ground+self.world_size[1])
                if active_keys['spacebar'] == True:
                    next_vel = (next_vel[0], 18.0)
                    audio_controller.jump()
                    self.on_ground = False
                else:
                    next_vel = (next_vel[0], -next_vel[1]*0.15)

            # wall collisions
            if left_side < next_player_x_index and current_player_height < left_height:
                next_pos = (next_player_x_index+self.world_size[0]*0.5, next_pos[1])
                next_vel = (0, next_vel[1])
            elif right_side > next_player_x_index+1 and current_player_height < right_height:
                next_pos = (next_player_x_index+1-self.world_size[0]*0.5, next_pos[1])
                next_vel = (0, next_vel[1])

            # falling/respawning
            if current_player_height <= 1.0:
                next_pos = (self.last_respawnable_x, 40.0)
                next_vel = (0, -0.001)
                self.controls_disabled = True

        # animations
        self.process_animation(dt)

        # visual update
        self.world_vel = next_vel
        self.world_pos = next_pos
        self.element.pos = (self.world_pos[0]*self.res, self.world_pos[1]*self.res)


