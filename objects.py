import numpy as np
import random
from math import *
from core import *
from kivy.graphics import Rectangle, Ellipse, Color, Mesh
from kivy.core.image import Image
from kivy.graphics.instructions import InstructionGroup


class Element(object):
    def __init__(self, pos = (0, 0), vel = (0, 0), tag = "", color = None, z = 0, musical = False, target_alpha = None):
        self.pos = pos
        self.vel = vel
        self.tag = tag
        self.color = color
        self.z = z
        self.shape = None
        self.musical = musical
        self.target_alpha = target_alpha # try to use this to control alpha whenever possible
        self.misc_t = -1
        self.misc_flag = False
        self.kill_me = False

        if color == None:
            self.color = Color(1, 1, 1)

    def on_update(self, dt):
        if self.vel != None:
            self.pos = (self.pos[0]+self.vel[0]*dt, self.pos[1]+self.vel[1]*dt)
        if self.target_alpha != None:
            self.color.a = self.color.a + ((self.target_alpha - self.color.a)*12.0*dt)

        # misc t
        if self.misc_t > 0:
            self.misc_t += -dt
            self.misc_flag = False
        elif self.misc_flag != True and self.misc_t != -1:
            self.misc_t = -1
            self.misc_flag = True


class TexturedElement(Element):
    def __init__(self, pos = (0, 0), vel = (0, 0), tag = "", color = None, z = 0, size = (10, 10), texture_path = "", musical = False, target_alpha = None):
        Element.__init__(self, pos, vel, tag, color, z, musical, target_alpha)
        self.size = size
        self.initial_size = size
        self.initial_pos = pos
        self.target_pos = None
        self.target_size = None
        self.texture_path = texture_path
        self.shape = Rectangle(pos=((self.pos[0]-(self.size[0]/2))*retina_multiplier, (self.pos[1]-(self.size[1]/2))*retina_multiplier),size=(self.size[0]*retina_multiplier, self.size[1]*retina_multiplier))

        if texture_path != "":
            self.shape.texture = Image(texture_path).texture

    def change_texture(self, new_texture_path):
        if new_texture_path != self.texture_path:
            self.texture_path = new_texture_path
            if self.texture_path != "":
                self.shape.texture = Image(self.texture_path).texture

    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):
        if self.target_pos != None:
            self.pos = (self.pos[0] + ((self.target_pos[0] - self.pos[0])*dt*10.0), self.pos[1] + ((self.target_pos[1] - self.pos[1])*dt*10.0))
        if self.target_size != None:
            self.size = (self.size[0] + ((self.target_size[0] - self.size[0])*dt*10.0), self.size[1] + ((self.target_size[1] - self.size[1])*dt*10.0))

        super().on_update(dt)
        self.shape.pos = (((self.pos[0]-(self.size[0]/2))*retina_multiplier)*cam_scalar + cam_offset[0], ((self.pos[1]-(self.size[1]/2))*retina_multiplier)*cam_scalar + cam_offset[1])
        self.shape.size = (self.size[0]*retina_multiplier*cam_scalar, self.size[1]*retina_multiplier*cam_scalar)


class GeometricElement(Element):
    def __init__(self, pos = (0, 0), vel = (0, 0), tag = "", color = None, z = 0, size = (10, 10), shape = None, musical = False, target_alpha = None):
        Element.__init__(self, pos, vel, tag, color, z, musical, target_alpha)
        self.size = size
        self.target_size = None
        self.shape = shape
        if self.shape == None:
            self.shape = Rectangle(pos=((self.pos[0]-(self.size[0]/2))*retina_multiplier, (self.pos[1]-(self.size[1]/2))*retina_multiplier),size=(self.size[0]*retina_multiplier, self.size[1]*retina_multiplier))

        # size safety
        if self.shape.size[0] == 0:
            self.shape.size = (0.01, self.shape.size[1])
        if self.shape.size[1] == 0:
            self.shape.size = (self.shape.size[0], 0.01)

    def change_shape(self, new_shape):
        self.shape = new_shape

    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):
        super().on_update(dt)
        self.shape.pos = (((self.pos[0]-(self.size[0]/2))*retina_multiplier)*cam_scalar + cam_offset[0], ((self.pos[1]-(self.size[1]/2))*retina_multiplier)*cam_scalar + cam_offset[1])

        # size management
        if self.target_size != None:
            self.size = (self.size[0] + ((self.target_size[0] - self.size[0])*dt*10.0), self.size[1] + ((self.target_size[1] - self.size[1])*dt*10.0))
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

    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):
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
    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):
        new_cam_scalar = cam_scalar*(1/(self.parallax_z+1))
        new_cam_offset_parts = ((cam_offset[0]-(actual_window_size[0]*0.5*retina_multiplier))/cam_scalar, (cam_offset[1]-(actual_window_size[1]*0.5*retina_multiplier))/cam_scalar)
        new_cam_offset = (new_cam_offset_parts[0]*new_cam_scalar + (actual_window_size[0]*0.5*retina_multiplier), new_cam_offset_parts[1]*new_cam_scalar + (actual_window_size[1]*0.5*retina_multiplier))

        self.element.on_update(dt, ref_cam_scalar, cam_scalar, new_cam_offset)


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

    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):
        for i in range(len(self.meshes)):
            processed_vertices = self.mesh_vertices[i][:]
            for j in [0, 4, 8, 12, 16, 20]:
                processed_vertices[j] = (processed_vertices[j]*cam_scalar) + cam_offset[0]
            for j in [1, 5, 9, 13, 17, 21]:
                processed_vertices[j] = (processed_vertices[j]*cam_scalar) + cam_offset[1]
            self.meshes[i].vertices = processed_vertices


class Platform(object):
    def __init__(self, cell_bounds, type = "dirt", z = 0, musical = False, beats = [1, 3], texture = "", res = 20.0, tag = "", active = True, sound_path = ""):
        self.type = type
        if self.type == "mech":
            musical = True
        self.musical = musical
        self.beats = beats # measured in half-beats
        self.texture = texture
        self.cell_bounds = cell_bounds # in world_pos coordinate system
        self.z = z
        self.res = res
        self.tag = tag
        self.active = True
        self.sound_path = sound_path

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

        if active == False:
            self.toggle_active_state()

    def toggle_active_state(self):
        self.active = not self.active
        if self.active:
            if self.type == "dirt":
                self.shape.mode="triangle_fan"
        else:
            if self.type == "dirt":
                self.shape.mode="line_loop"

    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):
        self.t += dt
        if self.type != "dirt":
            self.element.on_update(dt, ref_cam_scalar, cam_scalar, cam_offset)
        else:
            processed_vertices = self.vertices[:]
            for j in [0, 4, 8, 12, 16, 20, 24, 28]:
                processed_vertices[j] = (processed_vertices[j]*cam_scalar) + cam_offset[0]
            for j in [1, 5, 9, 13, 17, 21, 25, 29]:
                processed_vertices[j] = (processed_vertices[j]*cam_scalar) + cam_offset[1]
            self.shape.vertices = processed_vertices


class JumpPad(object):
    def __init__(self, world_pos = (2, 6), z = 0, color = None, beats = [1, 3], res = 20.0, tag = "", sound_path = ""):
        self.world_pos = world_pos
        self.initial_world_pos = world_pos
        self.target_world_pos = world_pos
        self.musical = True
        self.beats = beats # measured in half-beats
        self.z = z
        self.color = color
        if self.color == None:
            self.color = Color(1, 0, 0)
        self.res = res
        self.tag = tag
        self.active = False
        self.sound_path = sound_path

        # musical elements
        self.t = 0
        self.anim_t = 0

        # creates element for jump pad
        self.element = TexturedElement(color = self.color, size = (146*0.3, 420*0.3), texture_path = "graphics/jump_pad.png")
        self.shape = self.element.shape

    def toggle_active_state(self):
        self.active = not self.active
        self.anim_t = 0
        if not self.active:
            self.target_world_pos = self.initial_world_pos

    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):
        self.t += dt

        # manages world_pos
        self.world_pos = (self.world_pos[0] + ((self.target_world_pos[0] - self.world_pos[0]) * dt * 30.0), self.world_pos[1] + ((self.target_world_pos[1] - self.world_pos[1]) * dt * 30.0))
        if self.active:
            self.anim_t += dt
            self.target_world_pos = (self.initial_world_pos[0], self.initial_world_pos[1] + 1.0 + (np.sin(self.anim_t*30.0)*0.1*max(0, (0.75-self.anim_t)/0.75)))

        # updates element with correct position
        self.element.pos = (self.world_pos[0]*self.res, (self.world_pos[1]-1)*self.res - (self.element.size[1]*0.5))
        self.element.on_update(dt, ref_cam_scalar, cam_scalar, cam_offset)


class Spikes(object):
    def __init__(self, world_pos = (2, 6), z = 0, color = None, beats = [1, 3], res = 20.0, tag = "", sound_path = ""):
        self.world_pos = world_pos
        self.initial_world_pos = world_pos
        self.target_world_pos = world_pos
        self.musical = True
        self.beats = beats # measured in half-beats
        self.z = z
        self.color = color
        if self.color == None:
            self.color = Color(1, 0, 0)
        self.res = res
        self.tag = tag
        self.active = False
        self.sound_path = sound_path

        # musical elements
        self.t = 0
        self.anim_t = 0

        # creates element for jump pad
        self.element = TexturedElement(color = self.color, size = (146*0.3, 420*0.3), texture_path = "graphics/spikes.png")
        self.shape = self.element.shape

    def toggle_active_state(self):
        self.active = not self.active
        self.anim_t = 0
        if not self.active:
            self.target_world_pos = self.initial_world_pos

    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):
        self.t += dt

        # manages world_pos
        self.world_pos = (self.world_pos[0] + ((self.target_world_pos[0] - self.world_pos[0]) * dt * 30.0), self.world_pos[1] + ((self.target_world_pos[1] - self.world_pos[1]) * dt * 30.0))
        if self.active:
            self.anim_t += dt
            self.target_world_pos = (self.initial_world_pos[0], self.initial_world_pos[1] + 1.0 + (np.sin(self.anim_t*30.0)*0.1*max(0, (0.75-self.anim_t)/0.75)))

        # updates element with correct position
        self.element.pos = (self.world_pos[0]*self.res, (self.world_pos[1]-1)*self.res - (self.element.size[1]*0.5))
        self.element.on_update(dt, ref_cam_scalar, cam_scalar, cam_offset)


class Pickup(object):
    def __init__(self, element, z = 10, radius = 10, musical = False, tag = ""): # self.z, self.shape, self.color, self.on_update(), self.musical
        self.element = element
        self.element.target_size = self.element.size
        self.color = self.element.color
        self.initial_pos = self.element.pos
        self.z = z
        self.shape = self.element.shape
        self.radius = radius*retina_multiplier
        self.t = random.random()*3.14159*2.0
        self.musical = musical
        self.tag = tag

    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):
        self.t += dt
        self.element.pos = (self.initial_pos[0], self.initial_pos[1] + (np.sin(self.t*6.5)*2*retina_multiplier))
        self.element.on_update(dt, ref_cam_scalar, cam_scalar, cam_offset)


class Particle(object):
    def __init__(self, element, z = 10, resize_period = 2.0, musical = False, tag = "particle"): # self.z, self.shape, self.color, self.on_update(), self.musical
        self.element = element
        self.color = self.element.color
        self.initial_pos = self.element.pos
        self.z = z
        self.shape = self.element.shape
        self.initial_size = self.element.size
        self.musical = musical
        self.tag = tag
        self.kill_me = False

        # animations
        self.t = random.random()*0.35
        self.resize_period = resize_period

    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):
        self.t += dt

        # updates size
        coeff = ((-cos(self.t * 2 * 3.14159/self.resize_period)+1)*0.5)
        self.element.size = (self.initial_size[0] * coeff, self.initial_size[1] * coeff)
        if coeff <= 0.01 and self.t/self.resize_period >= 1.0:
            self.kill_me = True

        self.element.on_update(dt, ref_cam_scalar, cam_scalar, cam_offset)


# element-substitute world-coordinated objects, 
#     requires implementation of self.world_pos, self.world_size

class Player(object):
    def __init__(self, res = 20.0, initial_world_pos = (0, 0), z = 10, tag = ""):
        self.world_size = (0.9, 1.0)
        self.res = res
        self.initial_world_pos = initial_world_pos
        self.world_pos = initial_world_pos # world units are measured by res
        self.target_world_pos = None
        self.world_vel = (0, 0)
        self.world_vel_temp = (0, 0)
        self.z = z
        self.musical = False
        self.on_ground = True
        self.last_respawnable_x = self.world_pos[0]
        self.controls_disabled = False
        self.spawning_freeze = False
        self.tag = tag
        self.jump_used = False
        self.collisions_enabled = True
        self.hidden = False
        self.flight_enabled = False # dev only
        self.flight_y_vel = 0

        # fighting
        self.fight_pos = None
        self.max_health = 8
        self.health = self.max_health
        self.fight_hit_animation_state = -1
        self.fight_hit_animation_t = 0
        self.fight_keys_available = {"attack_1": True, "attack_2": True, "hit_1": True, "hit_2": True}
        self.sword = None

        # animations
        self.valid_animation_states = ["standing", "run_left", "run_right", "jump_right", "jump_left"]
        self.animation_state = "standing"
        self.animation_t = 0
        self.animation_frame = 0
        self.animation_frame_duration = 0.1

        self.element = TexturedElement(pos = (self.world_pos[0]*self.res, self.world_pos[1]*self.res), tag = "player", z = self.z, size = (self.res*2, self.res*2), texture_path = "graphics/player_stand.png")

    def reset_health(self):
        self.health = self.max_health

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

    def get_highest_ground(self, ground_map, platforms = []):
        next_pos = (self.world_pos[0], self.world_pos[1])
        next_player_x_index = min(max(int(next_pos[0]), 0), len(ground_map)-1)
        highest_ground = ground_map[next_player_x_index]

        # platforms
        left_side = next_pos[0] - self.world_size[0]*0.5
        right_side = next_pos[0] + self.world_size[0]*0.5
        current_player_height = self.world_pos[1]-self.world_size[1]
        for platform in platforms:
            if platform.active == True and right_side > platform.cell_bounds[0][0] and left_side < platform.cell_bounds[1][0]+1 and current_player_height > (1+platform.cell_bounds[0][1]+platform.cell_bounds[1][1])/2:
                highest_ground = max(highest_ground, 1+(platform.cell_bounds[0][1]+platform.cell_bounds[1][1])/2)

        return highest_ground

    def attack(self):
        self.world_pos = (self.fight_pos[0]+0.5, self.fight_pos[1])

        if self.sword != None:
            self.sword.misc_t = 0.6
            self.sword.change_texture("graphics/sword_1_right_down.png")

    def hit(self, move = True):
        if move:
            self.world_pos = (self.fight_pos[0]-0.25, self.fight_pos[1])
        self.health = max(self.health-1, 0)
        self.fight_hit_animation_t = 1.0

    def block(self):
        self.world_pos = (self.fight_pos[0]-0.05, self.fight_pos[1])

        if self.sword != None:
            self.sword.misc_t = 0.6
            self.sword.change_texture("graphics/sword_1_right_block.png")

    def on_update(self, dt, ground_map, active_keys, cam_scalar, cam_offset, audio_controller, platforms = [], door = None, override_target_x_vel = None):

        # dev
        if active_keys["1"] == True:
            print("PLAYER POS: "+str(self.world_pos))

        # position update
        target_x_vel = 0
        target_y_vel = 0 # for flight only
        if audio_controller != None and audio_controller.solved == False:
            if self.controls_disabled == False and self.spawning_freeze == False:
                if active_keys["right"] == True:
                    target_x_vel += 9.0
                    self.set_animation_state("run_right")
                if active_keys["left"] == True:
                    target_x_vel += -9.0
                    self.set_animation_state("run_left")
            if active_keys["left"] == False and active_keys["right"] == False:
                self.set_animation_state("standing")
            if active_keys["spacebar"] == False:
                self.jump_used = False
            if active_keys["up"] == True:
                target_y_vel += 0.12
            if active_keys["down"] == True:
                target_y_vel += -0.12

        accel = -72.0*dt
        if override_target_x_vel != None:
            target_x_vel = override_target_x_vel
        if self.collisions_enabled == False:
            accel = 0
            self.world_vel = (self.world_vel[0], 0)
        if self.flight_enabled:
            accel = 0

        # flight mode
        if target_y_vel != 0:
            self.flight_y_vel = self.flight_y_vel + ((target_y_vel - self.flight_y_vel)*18.0*dt)
        else:
            self.flight_y_vel = self.flight_y_vel*0.91

        self.world_vel_temp = (self.world_vel_temp[0] * 0.915, self.world_vel_temp[1] * 0.915)
        next_vel = (self.world_vel[0]+((target_x_vel - self.world_vel[0])*18.0*dt), self.world_vel[1] + accel + self.flight_y_vel)
        next_pos = (self.world_pos[0] + self.world_vel[0]*dt + self.world_vel_temp[0]*dt, self.world_pos[1] + self.world_vel[1]*dt + self.world_vel_temp[1]*dt)

        # ground & wall collisions
        if self.collisions_enabled == True:
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
                self.spawning_freeze = False
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
                if platform.active == True and right_side > platform.cell_bounds[0][0] and left_side < platform.cell_bounds[1][0]+1:
                    if current_player_height > (1+platform.cell_bounds[0][1]+platform.cell_bounds[1][1])/2:
                        highest_ground = max(highest_ground, 1+(platform.cell_bounds[0][1]+platform.cell_bounds[1][1])/2)

                    if fabs(current_player_height - ((2+platform.cell_bounds[0][1]+platform.cell_bounds[1][1])/2)) < 0.05:
                        self.spawning_freeze = False

            if next_player_height < highest_ground: # is true whenever resting on ground
                next_pos = (next_pos[0], highest_ground+self.world_size[1])
                if active_keys['spacebar'] == True and self.jump_used == False and self.controls_disabled == False and self.spawning_freeze == False and current_player_height > 1.5:
                    next_vel = (next_vel[0], 18.6015*audio_controller.bpm/110)
                    audio_controller.jump()
                    self.on_ground = False
                    self.jump_used = True
                else:
                    next_vel = (next_vel[0], -next_vel[1]*0.15)

            # wall collisions
            if left_side < next_player_x_index and current_player_height < left_height:
                next_pos = (next_player_x_index+self.world_size[0]*0.5, next_pos[1])
                next_vel = (0, next_vel[1])
                self.world_vel_temp = (0, self.world_vel_temp[1])
            elif right_side > next_player_x_index+1 and current_player_height < right_height:
                next_pos = (next_player_x_index+1-self.world_size[0]*0.5, next_pos[1])
                next_vel = (0, next_vel[1])
                self.world_vel_temp = (0, self.world_vel_temp[1])

            # falling/respawning
            if current_player_height <= 1.1:
                next_pos = (self.last_respawnable_x, 40.0)
                next_vel = (0, -0.001)
                self.spawning_freeze = True

        # fight hit animation
        if self.health > 0 and self.hidden == False:
            if self.fight_hit_animation_t > 0:
                self.fight_hit_animation_t += -dt

                if self.fight_hit_animation_t // 0.075 != self.fight_hit_animation_state:
                    self.fight_hit_animation_state = self.fight_hit_animation_t // 0.075
                    self.element.color.a = ((self.fight_hit_animation_state % 2)*0.6) + 0.4
            elif self.fight_hit_animation_state == -2: # triggers recovery animaiton
                self.fight_hit_animation_state = -1.5
                self.fight_hit_animation_t = 4.25
            elif self.fight_hit_animation_state != -1: # delays immediately resets player's opacity to 1
                self.fight_hit_animation_state = -1
                self.element.color.a = 1
        else:
            self.element.color.a = 0
            self.fight_hit_animation_state = -2

        # animations
        self.process_animation(dt)

        # visual update
        if self.target_world_pos != None:
            self.world_vel = ((self.target_world_pos[0] - self.world_pos[0])*10.0, (self.target_world_pos[1] - self.world_pos[1])*10.0)
            self.world_pos = (self.world_pos[0] + self.world_vel[0]*dt, self.world_pos[1] + self.world_vel[1]*dt)
        else:
            self.world_vel = next_vel
            self.world_pos = next_pos
        self.element.pos = (self.world_pos[0]*self.res, self.world_pos[1]*self.res)

# holds data for gems
class SongData(object):
    def __init__(self, color):
        super(SongData, self).__init__()
        self.gems_buffer = []
        self.base_color = color

    # read the gems and song data. You may want to add a secondary filepath
    # argument if your barline data is stored in a different txt file.
    def read_data(self, filepath):
        print("READ: "+str(filepath))
        solo_file = open(filepath)
        solo_file_lines = solo_file.readlines()
        for line in range(len(solo_file_lines)):
            line_tokens = solo_file_lines[line].strip().split('\t')

            start_time = line_tokens[0]

            if len(line_tokens) > 1:
                size_word, intensity = line_tokens[1].split(' ')
            else:
                size_word = 'med'
                intensity = '3'

            size = 39
            if size_word == 'big':
                size = 50
            elif size_word == 'small':
                size = 28

            color_diff = 0.15*(5 - float(intensity))
            color = Color(min(1, self.base_color[0] + color_diff), min(1, self.base_color[1] + color_diff), min(1, self.base_color[2] + color_diff))
            
            self.gems_buffer.append({'start_time': float(start_time), 'color': color, 'size': size})
            # self.gems_buffer.append(start_time)
        return self.gems_buffer

    def get_gem_data(self):
        return self.gems_buffer

# Displays and controls gems for puzzle mode
class PuzzleGems(InstructionGroup):
    def __init__(self, gem_data, bpm, get_song_time, queue_UI_element, get_offsets):
        super(PuzzleGems, self).__init__()
        # gems
        self.gem_data = gem_data
        self.onscreen_gems = []
        for i in range(len(self.gem_data)):
            self.onscreen_gems.append({'gems': {}, 'start_index': 0})

        # sync to song
        self.beat_time = 60 / bpm
        self.max_song_time = 16 * 60 / bpm
        self.song_time = 0
        self.playing = False
        self.create_gems = True
        self.pulsing_enabled = True

        self.screen_time = self.max_song_time/2
        self.vel = window_size[0] / self.screen_time # pixels per second

        self.start = False

        # callbacks
        self.get_song_time = get_song_time
        self.queue_UI_element = queue_UI_element
        self.get_offsets = get_offsets

    # call every frame to make gems and barlines flow down the screen
    def on_update(self, dt) :
        self.song_time = self.get_song_time()

        # for each track
        if self.create_gems == True:
            for index, gem_props in enumerate(self.gem_data):
                gem_start = self.onscreen_gems[index]['start_index']
                offset = gem_props['offset'] * self.beat_time / 2

                if index == len(self.gem_data)-1 and not self.start:
                    while gem_start < len(gem_props['gem_times']) and gem_props['gem_times'][gem_start]['start_time'] < (self.song_time + 0.75*self.screen_time + offset) % self.max_song_time - 2*dt:
                        gem_start = gem_start + 1
                gem_start = gem_start % len(gem_props['gem_times'])
                # add gems
                while gem_start < len(gem_props['gem_times']) and (
                    gem_props['gem_times'][gem_start]['start_time'] < (self.song_time + 0.75*self.screen_time + offset) % self.max_song_time + 2*dt
                    and gem_props['gem_times'][gem_start]['start_time'] > (self.song_time + 0.75*self.screen_time + offset) % self.max_song_time - 2*dt):
                    self.start = True
                    pos = (window_size[0], self.gem_data[index]['gem_y_pos'])
                    ellipse = Ellipse(size=(0.01, 0.01))
                    color = gem_props['gem_times'][gem_start]['color']
                    size = gem_props['gem_times'][gem_start]['size']
                    gem_element = GeometricElement(pos=pos, tag = "gem", color = color, z = 9, size = (size, size), shape = ellipse)
                    self.queue_UI_element(gem_element)
                    self.onscreen_gems[index]['gems'][gem_props['gem_times'][gem_start]['start_time']] = (gem_element, gem_props['gem_times'][gem_start])

                    gem_start = (gem_start + 1) % len(gem_props['gem_times'])

                self.onscreen_gems[index]['start_index'] = gem_start

            # pulse when hit
            offsets = self.get_offsets()
            for index, onscreen_props in enumerate(self.onscreen_gems):
                to_remove = []
                if index == len(self.gem_data)-1:
                    offset = 0
                else:
                    offset = offsets[index] * self.beat_time / 2
                for gem_time in onscreen_props['gems'].keys():
                    gem, props = onscreen_props['gems'][gem_time]
                    if gem.pos[0] < -50:
                        to_remove.append(gem_time)
                    elif self.pulsing_enabled == True and gem_time < (self.song_time + offset) % self.max_song_time + dt and gem_time > (self.song_time + offset) % self.max_song_time - dt:
                        size = props['size']
                        gem.size = (size*2, size*2)
                        gem.target_size = (size, size)

                for gem_time in to_remove:
                    onscreen_props['gems'].pop(gem_time)
  

class Enemy(object):
    def __init__(self, res = 20.0, initial_world_pos = (0, 0), z = 10, tag = "enemy", moves_per_beat = ["stop"], color = None, radius = 25.0, has_key = False, health = 5):
        self.world_size = (0.9, 1.0)
        self.res = res
        self.world_pos = initial_world_pos # world units are measured by res
        self.target_world_pos = None
        self.world_vel = (0, 0)
        self.z = z
        self.musical = False
        self.tag = tag        
        self.color = color
        if color == None:
            self.color = Color(0, 0, 0)
        self.radius = radius
        self.has_key = has_key
        self.hidden = False

        # movement
        self.moves_per_beat = moves_per_beat # e.g. ["stop", "left", "stop", "right"]
        self.current_move_index = 0 # assumes first state is always "stop"
        self.target_velocity = (0, 0)

        # fighting
        self.max_health = health
        self.health = self.max_health
        self.in_fight = False
        self.fight_pos = None
        self.fight_hit_animation_state = -1
        self.fight_hit_animation_t = 0
        self.sword = None

        # animations
        self.valid_animation_states = ["standing", "run_left", "run_right"]
        self.animation_state = "standing"
        self.animation_t = 0
        self.animation_frame = 0
        self.animation_frame_duration = 0.1

        self.element = TexturedElement(pos = (self.world_pos[0]*self.res, self.world_pos[1]*self.res), tag = "enemy", z = self.z, size = (self.res*2, self.res*2), texture_path = "graphics/enemy_stand.png")
        self.shape = self.element.shape

    def reset_health(self):
        self.health = self.max_health

    def attack(self):
        self.world_pos = (self.fight_pos[0]-0.5, self.fight_pos[1])

        if self.sword != None:
            self.sword.misc_t = 0.6
            self.sword.change_texture("graphics/sword_1_left_down.png")

    def hit(self):
        self.world_pos = (self.fight_pos[0]+0.25, self.fight_pos[1])
        self.health = max(self.health-1, 0)
        self.fight_hit_animation_t = 1.0

    def block(self):
        self.world_pos = (self.fight_pos[0]+0.05, self.fight_pos[1])

        if self.sword != None:
            self.sword.misc_t = 0.6
            self.sword.change_texture("graphics/sword_1_left_block.png")

    def set_animation_state(self, new_state): # follow this call with self.process_animation()
        if new_state in self.valid_animation_states and new_state != self.animation_state:
            self.animation_state = new_state
            self.animation_t = 0
            self.animation_frame = -1

            if self.animation_state == "standing":
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
                    self.element.change_texture("graphics/enemy_run_1.png")
                elif self.animation_frame % 3 == 1:
                    self.element.change_texture("graphics/enemy_run_2.png")
                elif self.animation_frame % 3 == 2:
                    self.element.change_texture("graphics/enemy_run_3.png")
            elif self.animation_state == "run_left":
                if self.animation_frame % 3 == 0:
                    self.element.change_texture("graphics/enemy_run_1_r.png")
                elif self.animation_frame % 3 == 1:
                    self.element.change_texture("graphics/enemy_run_2_r.png")
                elif self.animation_frame % 3 == 2:
                    self.element.change_texture("graphics/enemy_run_3_r.png")
            else:
                self.element.change_texture("graphics/enemy_stand.png")

    def advance_moves(self):
        if self.in_fight == False:
            self.current_move_index += 1
            if self.current_move_index >= len(self.moves_per_beat):
                self.current_move_index = 0

            # applies movement rules for each move type
            next_move = self.moves_per_beat[self.current_move_index]
            if next_move == "stop":
                self.target_velocity = (0, 0)
                self.set_animation_state("standing")
            elif next_move == "left":
                self.target_velocity = (-3.5, 0)
                self.set_animation_state("run_left")
            elif next_move == "right":
                self.target_velocity = (3.5, 0)
                self.set_animation_state("run_right")
        else:
            self.current_move_index = 0

    def on_update(self, dt, ref_cam_scalar, cam_scalar, cam_offset):

        # fight hit animation
        if self.hidden == False:
            if self.fight_hit_animation_t > 0:
                self.fight_hit_animation_t += -dt

                if self.fight_hit_animation_t // 0.075 != self.fight_hit_animation_state:
                    self.fight_hit_animation_state = self.fight_hit_animation_t // 0.075
                    self.color.a = ((self.fight_hit_animation_state % 2)*0.6) + 0.4
            elif self.fight_hit_animation_state != -1:
                self.fight_hit_animation_state = -1
                self.color.a = 1
        else:
            self.color.a = 0

        # animations
        self.process_animation(dt)

        # visual update
        if self.target_world_pos != None:
            self.world_vel = ((self.target_world_pos[0] - self.world_pos[0])*12.0, (self.target_world_pos[1] - self.world_pos[1])*12.0)
        else:
            self.world_vel = (self.world_vel[0]+((self.target_velocity[0] - self.world_vel[0])*18.0*dt), self.world_vel[1]+((self.target_velocity[1] - self.world_vel[1])*18.0*dt))
        self.world_pos = (self.world_pos[0] + self.world_vel[0]*dt, self.world_pos[1] + self.world_vel[1]*dt)
        self.element.pos = (self.world_pos[0]*self.res, self.world_pos[1]*self.res)
        self.element.on_update(dt, ref_cam_scalar, cam_scalar, cam_offset)
