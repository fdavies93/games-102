import pygame, time, sys, math
from enum import IntEnum
from vec2 import Vec2
from utils import clamp_between
from random import randint
from handlers import MoveEventHandler, TrackEventHandler, CustomEvent
from gameobject import GameObject
from layer import Layer
from fpscounter import FpsCounter
pygame.init()

black = (0, 0, 0)
red_circle = pygame.image.load("assets/red-circle-small.png")

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

    def next_id(self):
        cur = self._id
        self._id += 1
        return cur

    def add_layer(self, new_layer):
        # do a binary search based insert at correct position
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
        print([l.priority for l in self.layers])
        

    def setup(self):
        tree_sprite = pygame.image.load("assets/tree.png").convert_alpha()
        ground_tile = pygame.image.load("assets/ground-tile.png").convert()

        self.fps_counter = FpsCounter()
        self.camera = GameObject(self, bounds=Vec2(960,640))
        self.ball = GameObject(self, position=Vec2(320,240), bounds=Vec2(111,111), sprite=pygame.image.load("assets/ball.gif").convert_alpha())
        self.background = GameObject(self, sprite=pygame.image.load("assets/night-sky.png").convert_alpha(), bounds=Vec2(960,640))
        self.mountains = GameObject(self, sprite=pygame.image.load("assets/mountains.png").convert_alpha(), position=Vec2(0,560), bounds=Vec2(1320,640))
        self.physics_objects = [self.ball, self.camera]
        # self.camera_listener = MoveEventHandler(self, self.camera)

        self.objects[self.camera.id] = self.camera
        self.objects[self.ball.id] = self.ball
        self.objects[self.background.id] = self.background
        self.objects[self.mountains.id] = self.mountains

        self.layers = [Layer(0, parallax=Vec2(0,0)), Layer(1, parallax=Vec2(0.5, 0.5)), Layer(3,parallax=Vec2(0.75,0.75)), Layer(2)]
        self.layers[0].add_object(self.background)
        self.layers[1].add_object(self.mountains)
        self.layers[3].add_object(self.ball)

        tree_spacing = 500
        for i in range(5):
            new_tree = GameObject(self, position=Vec2(i * tree_spacing, 640), bounds=Vec2(640,640), sprite=tree_sprite)
            self.objects[new_tree.id] = new_tree
            self.layers[2].add_object(new_tree)

        spacing = 159
        for i in range(10):
            new_ground = GameObject(self, position=Vec2(i * spacing, 1200), bounds=Vec2(159,159), sprite=ground_tile)
            self.objects[new_ground.id] = new_ground
            self.layers[3].add_object(new_ground)

        # width = 10
        # height = 10
        # spacing = 200

        # for i in range(width*height):
        #     obj_pos = Vec2( (i * spacing) % (spacing * width), math.floor(i / height) * spacing )
        #     cur_obj = GameObject(obj_pos, bounds=Vec2(16,16), sprite=red_circle)
        #     self.layers[1].add_object(cur_obj)
        #     self.objects[cur_obj.id] = cur_obj

        # self.sprites.append(self.ball)

        self.key_listeners = [MoveEventHandler(self, self.ball)]
        self.update_listeners = [TrackEventHandler(self, self.camera, self.ball)]

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
                obj_screen_position = ((obj.position[0] - self.camera.position[0]) * layer.parallax.x, (obj.position[1] - self.camera.position[1]) * layer.parallax.y)

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