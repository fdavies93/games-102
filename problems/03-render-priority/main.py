import pygame, time, sys, math
from enum import IntEnum
from vec2 import Vec2
from utils import clamp_between
from random import randint
pygame.init()

black = (0, 0, 0)
red_circle = pygame.image.load("assets/red-circle-small.png")


class CustomEvent(IntEnum):
    AFTER_UPDATE = pygame.event.custom_type()

class GameObject():
    def __init__(self, position = Vec2(0,0), bounds=Vec2(0,0), speed = Vec2(0,0), sprite = None):
        self.id = Game.next_id()
        self.position = position
        self.bounds = bounds
        self.speed = speed
        self.sprite = sprite
        self.last_updated = 0

class Layer():
    def __init__(self, priority = 0, parallax = Vec2(1.0,1.0)):
        self.priority = priority
        self.parallax = parallax
        self.objects = [] # store by index
    
    def add_object(self, obj):
        self.objects.append(obj.id)

# never use this - it's a base class
class EventHandler():
    def __init__(self, obj : GameObject):
        self.object = obj

    def on_event(ev):
        pass

class MoveEventHandler(EventHandler):
    def __init__(self, obj : GameObject, speed = 5):
        self.speed_map = {
            'w': Vec2(0, -speed), 
            'a': Vec2(-speed, 0),
            's': Vec2(0, speed),
            'd': Vec2(speed, 0)
        }
        super().__init__(obj)
    
    def change_obj_speed(self, speed, invert):
        cur_speed = self.object.speed
        speed_change = speed
        if invert:
            speed_change = speed.negate()
        self.object.speed = cur_speed + speed_change

    def on_event(self, ev : pygame.event.Event):
        key_name = pygame.key.name(ev.key)
        if key_name not in self.speed_map: 
            return
        if (ev.type == pygame.KEYDOWN):
            self.change_obj_speed( self.speed_map[key_name], False )
        elif (ev.type == pygame.KEYUP):
            self.change_obj_speed( self.speed_map[key_name], True)

        # print(f"Position: {self.object.position}, Speed: {self.object.speed}")


class TrackEventHandler(EventHandler):
    def __init__(self, obj : GameObject, to_follow = None):
        self.to_follow = to_follow
        super().__init__(obj)
    
    def on_event(self, ev : pygame.event.Event):

        if self.to_follow == None:
            return
        if ev.type != CustomEvent.AFTER_UPDATE:
            print("returning")
            return

        new_position = [self.to_follow.position[0] - (self.object.bounds[0] / 2), self.to_follow.position[1] - (self.object.bounds[1] / 2)]
        new_speed = [self.to_follow.speed[0], self.to_follow.speed[1]]

        low = Game.instance.bounds[0]
        high = Game.instance.bounds[1]

        if (new_position[0] < Game.instance.bounds[0] or new_position[0] + self.object.bounds[0] > Game.instance.bounds[1]):
                new_position[0] = clamp_between(new_position[0], low, high - self.object.bounds[0])
                new_speed[0] = 0
        if (new_position[1] < Game.instance.bounds[1] or new_position[1] + self.object.bounds[1] > Game.instance.bounds[1]):
                new_position[1] = clamp_between(new_position[1], low, high - self.object.bounds[1])
                new_speed[1] = 0
        
        self.object.speed = (new_speed[0], new_speed[1])
        self.object.position = (new_position[0], new_position[1])


class FpsCounter():
    
    def __init__(self):
        self.frames = 0
        self.prev_render = 0
        self.prev_frames = 0
        self.font = pygame.font.Font(None, 24)
    
    def render(self, surface : pygame.Surface, position : pygame.rect.Rect):
        if time.time() > self.prev_render + 0.25:
            self.prev_frames = (self.frames * 4)
            self.frames = 0
            self.prev_render = time.time()

        self.frames += 1
        font_surface = self.font.render(f"FPS: {str(self.prev_frames)}", True, (255,255,255))
        surface.blit(font_surface, position)

class Game():

    instance = None

    def __init__(self):
        self.size = self.width, self.height = (960, 640)
        self.screen = pygame.display.set_mode(self.size)
        self.bounds = (0, 1320) # minimum and maximum values of object positions
        self.sprites = []
        self.layers = []
        self.fps = 1 / 30
        self.update_listeners : list[EventHandler] = []
        self._id = 0
        self.objects = {}
        Game.instance = self

    def next_id():
        cur = Game.instance._id
        Game.instance._id += 1
        return cur

    def add_layer(self, new_layer):
        # do a binary search based insert at correct position
        # this algorithm is not the easiest to livecode
        pivot = math.floor(len(self.layers) / 2)
        upper = len(self.layers)
        lower = 0
        cur_priority = self.layers[pivot].priority
        while cur_priority != new_layer.priority and upper != lower + 1 and pivot < upper and pivot >= lower:
            cur_priority = self.layers[pivot].priority
            if new_layer.priority < self.layers[pivot].priority:
                upper = pivot
            if new_layer.priority > self.layers[pivot].priority:
                lower = pivot
            pivot = math.floor((upper - lower) / 2) + lower
            
        cur_priority = self.layers[pivot].priority

        if cur_priority == new_layer.priority:
            return

        if pivot == len(self.layers):
            self.layers.append(new_layer)
        else:
            self.layers.insert(pivot + 1, new_layer)
        

    def setup(self):
        tree_sprite = pygame.image.load("assets/tree.png").convert_alpha()
        ground_tile = pygame.image.load("assets/ground-tile.png").convert()

        self.fps_counter = FpsCounter()
        self.camera = GameObject(bounds=Vec2(960,640))
        self.ball = GameObject(position=Vec2(320,240), bounds=Vec2(111,111), sprite=pygame.image.load("assets/ball.gif").convert_alpha())
        self.background = GameObject(sprite=pygame.image.load("assets/night-sky.png").convert_alpha(), bounds=Vec2(960,640))
        self.mountains = GameObject(sprite=pygame.image.load("assets/mountains.png").convert_alpha(), position=Vec2(0,560), bounds=Vec2(1320,640))
        self.physics_objects = [self.ball, self.camera]
        self.camera_listener = MoveEventHandler(self.camera)

        # add ball, camera, background and mountains to object dict by ID
        self.objects[self.camera.id] = self.camera

        # populate layers array
        self.layers = [Layer(0, parallax=Vec2(0.0,0.0))]

        # add objects to layers
        self.layers[0].add_object(self.background)

        tree_spacing = 500
        for i in range(5):
            pass
            # create and add 5 trees at the bottom of the level behind the player somewhere

        spacing = 159
        for i in range(10):
            pass
            # create and add 10 trees at the bottom of the level on the same layer as the player

        self.key_listeners = [MoveEventHandler(self.ball)]
        self.update_listeners = [TrackEventHandler(self.camera, self.ball)]

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                for listener in self.key_listeners:
                    listener.on_event(event)

    def update(self, timestamp):
        for obj in self.physics_objects:
            new_position = obj.position + obj.speed
            if (new_position[0] < self.bounds[0] or new_position[0] + obj.bounds[0] > self.bounds[1]):
                new_position = new_position - Vec2(obj.speed.x, 0)
            if (new_position[1] < self.bounds[0] or new_position[1] + obj.bounds[1] > self.bounds[1]):
                new_position = new_position - Vec2(0, obj.speed.y)
            obj.position = new_position
            obj.last_updated = timestamp

        for listener in self.update_listeners:
            listener.on_event(pygame.event.Event(CustomEvent.AFTER_UPDATE,{"timestamp": timestamp}))

    def render(self, correction : float):
        self.screen.fill(black)

        width = self.width

        for layer in self.layers:
            for obj_id in layer.objects:
                obj = self.objects[obj_id]
                # implement parallaxing in the screen_position variable
                obj_screen_position = (obj.position[0] - self.camera.position[0], obj.position[1] - self.camera.position[1])

                if obj_screen_position[0] + obj.bounds[0] < 0 or obj_screen_position[0] > self.width or obj_screen_position[1] + obj.bounds[1] < 0 or obj_screen_position[1] > self.height:
                    # object is off screen, don't bother rendering    
                    continue

                self.screen.blit(obj.sprite, obj_screen_position)

        self.fps_counter.render(self.screen, ( width - (width / 5), 20 ))

        pygame.display.flip()

    def main(self):
        self.setup()

        prev = time.time()
        lag = 0.0

        while(True):
            current = time.time()
            delta = current - prev
            prev = current
            lag += delta
            
            self.process_input()

            while(lag >= self.fps):
                self.update(current)
                lag -= self.fps

            self.render(lag / self.fps)

if __name__ == "__main__":
    game = Game()
    game.main()