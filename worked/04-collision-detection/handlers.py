from enum import IntEnum
import pygame
from gameobject import GameObject
from vec2 import Vec2
from utils import clamp_between
import math

class CustomEvent(IntEnum):
    AFTER_UPDATE = pygame.event.custom_type()
    OUT_OF_BOUNDS = pygame.event.custom_type()
    COLLISION = pygame.event.custom_type()

# never use this - it's a base class
class EventHandler():
    def __init__(self, obj : GameObject):
        self.object = obj

    def on_event(ev):
        pass

class PlayerBulletSpawner(EventHandler):
    def __init__(self, game: "Game", obj: GameObject, distance = 0, speed = 10):
        self.game = game
        self.speed = speed
        self.reload = 0.3
        self.last_shot = 0
        self.bullet_sprite = pygame.image.load("assets/red-circle-small.png").convert_alpha()
        self.firing = False
        super().__init__(obj)
    
    def on_event(self, ev : pygame.event.Event):
        if ev.type != pygame.MOUSEBUTTONDOWN and ev.type != pygame.MOUSEBUTTONUP and ev.type != CustomEvent.AFTER_UPDATE:
            return

        if ev.type == pygame.MOUSEBUTTONDOWN:
            self.firing = True
            return

        if ev.type == pygame.MOUSEBUTTONUP:
            self.firing = False
            return       

        if not self.firing:
            return

        if not self.last_shot + self.reload < ev.timestamp:
            return

        obj = self.object
        
        mouse_pos = pygame.mouse.get_pos()

        spawn_location = obj.position + Vec2(obj.bounds[0] / 2, obj.bounds[1] / 2)
        screen_position = spawn_location - self.game.camera.position
        
        diff = Vec2(mouse_pos[0] - screen_position[0], mouse_pos[1] - screen_position[1])
        hypothenuse = math.sqrt( (diff[0] ** 2) + (diff[1] ** 2) )
        unit_speed = Vec2(diff[0] / hypothenuse, diff[1] / hypothenuse)

        sprite = GameObject(self.game, "player_bullet", spawn_location, Vec2(16,16), speed=(unit_speed * self.speed), sprite=self.bullet_sprite)

        self.game.objects[sprite.id] = sprite
        self.game.layers[1].add_object(sprite)
        self.game.physics_objects.append(sprite)
        self.game.update_listeners.append( PlayerBulletCollider(self.game, sprite) )

        self.last_shot = ev.timestamp
        

class PlayerBulletCollider(EventHandler):
    def __init__(self, game: "Game", obj: GameObject):
        self.game = game
        super().__init__(obj)

    def remove_self(self):
        del self.game.objects[self.object.id]
        # physics object removal should be handled automatically
        # self.game.physics_objects.remove(self.object)
        # destroy object
        # remove self from event handler list

    def handle_collision(self, ev : pygame.event.Event):
        ignore_list = ["player", "camera"]

        type_1 = self.game.objects[ev.object].type
        type_2 = self.game.objects[ev.object2].type
        if type_1 in ignore_list or type_2 in ignore_list:
            return

        print(f"Collision between {type_1} and {type_2}")

        if ev.object == self.object.id or ev.object2 == self.object.id:
            self.remove_self()

    def handle_out_of_bounds(self, ev : pygame.event.Event):
        if ev.object != self.object.id:
            return
        
        self.remove_self()

    def on_event(self, ev : pygame.event.Event):
        if ev.type != CustomEvent.OUT_OF_BOUNDS and ev.type != CustomEvent.COLLISION:
            return
        
        if ev.type == CustomEvent.COLLISION:
            self.handle_collision(ev)
            # bug: triggers where there are multiple bullets on screen
            # and any other than the last one is 

        if ev.type == CustomEvent.OUT_OF_BOUNDS:
            self.handle_out_of_bounds(ev)

class MoveEventHandler(EventHandler):
    def __init__(self, game: "Game", obj : GameObject, speed = 5):
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

    def handle_key_event(self, ev : pygame.event.Event):
        key_name = pygame.key.name(ev.key)
        if key_name not in self.speed_map: 
            return
        if (ev.type == pygame.KEYDOWN):
            self.change_obj_speed( self.speed_map[key_name], False )
        elif (ev.type == pygame.KEYUP):
            self.change_obj_speed( self.speed_map[key_name], True)

    def handle_collision(self, ev : pygame.event.Event):

        if ev.object != self.object.id and ev.object2 != self.object.id:
            return

        type_1 = self.game.objects[ev.object].type
        type_2 = self.game.objects[ev.object2].type

        self.object.speed = self.object.speed.negate()

    def on_event(self, ev : pygame.event.Event):

        if (ev.type == pygame.KEYDOWN or ev.type == pygame.KEYUP):
            self.handle_key_event(ev)
            return

        if (ev.type == CustomEvent.COLLISION):
            self.handle_collision(ev)
            return     

        # print(f"Position: {self.object.position}, Speed: {self.object.speed}")


class TrackEventHandler(EventHandler):
    def __init__(self, game : "Game", obj : GameObject, to_follow = None):
        self.to_follow = to_follow
        self.game = game
        super().__init__(obj)
    
    def on_event(self, ev : pygame.event.Event):
        if self.to_follow == None:
            print("Nothing to follow")
            return
        if ev.type != CustomEvent.AFTER_UPDATE:
            return

        new_position = [self.to_follow.position[0] - (self.object.bounds[0] / 2), self.to_follow.position[1] - (self.object.bounds[1] / 2)]
        new_speed = [self.to_follow.speed[0], self.to_follow.speed[1]]

        low = self.game.bounds[0]
        high = self.game.bounds[1]

        if (new_position[0] < self.game.bounds[0] or new_position[0] + self.object.bounds[0] > self.game.bounds[1]):
                new_position[0] = clamp_between(new_position[0], low, high - self.object.bounds[0])
                new_speed[0] = 0
        if (new_position[1] < self.game.bounds[1] or new_position[1] + self.object.bounds[1] > self.game.bounds[1]):
                new_position[1] = clamp_between(new_position[1], low, high - self.object.bounds[1])
                new_speed[1] = 0
        
        self.object.speed = Vec2(new_speed[0], new_speed[1])
        self.object.position = Vec2(new_position[0], new_position[1])