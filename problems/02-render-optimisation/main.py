import pygame, time, sys, math
from enum import IntEnum
pygame.init()

black = (0, 0, 0)
red_circle = pygame.image.load("assets/red-circle-small.png")

def clamp_between(to_clamp, lower, upper):
    output = to_clamp
    if output < lower:
        output = lower
    elif output > upper:
        output = upper
    return output

class CustomEvent(IntEnum):
    AFTER_UPDATE = pygame.event.custom_type()

class GameObject():
    def __init__(self, position = (0,0), bounds=(0,0), speed = (0,0), sprite = None):
        self.position = position
        self.bounds = bounds
        self.speed = speed
        self.sprite = sprite
        self.last_updated = 0

# never use this - it's a base class
class EventHandler():
    def __init__(self, obj : GameObject):
        self.object = obj

    def on_event(ev):
        pass

class MoveEventHandler(EventHandler):
    def __init__(self, obj : GameObject, speed = 5):
        self.speed_map = {
            'w': (0, -speed), 
            'a': (-speed, 0),
            's': (0, speed),
            'd': (speed, 0)
        }
        super().__init__(obj)
    
    def change_obj_speed(self, speed, invert):
        cur_speed = self.object.speed
        speed_change = speed
        if invert:
            speed_change = (-speed[0],-speed[1])
        self.object.speed = ( cur_speed[0] + speed_change[0], cur_speed[1] + speed_change[1] )

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
        self.size = self.width, self.height = (640, 480)
        self.screen = pygame.display.set_mode(self.size)
        self.bounds = (-100, 1000) # minimum and maximum values of object positions
        self.fps_counter = FpsCounter()
        self.camera = GameObject(bounds=(640,480))
        self.sprites = []
        self.fps = 1 / 30
        self.update_listeners : list[EventHandler] = []
        Game.instance = self

    def setup(self):
        self.ball = GameObject(position=(320,240), bounds=(111,111), sprite=pygame.image.load("assets/ball.gif"))
        self.physics_objects = [self.ball, self.camera]
        self.camera_listener = MoveEventHandler(self.camera)

        width = 10
        height = 10
        spacing = 100

        for i in range(width*height):
            obj_pos = ( (i * spacing) % (spacing * width), math.floor(i / height) * spacing )
            cur_obj = GameObject(obj_pos, bounds=(16,16), sprite=red_circle)
            self.sprites.append(cur_obj)

        self.sprites.append(self.ball)

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
            new_position = [obj.position[0] + obj.speed[0], obj.position[1] + obj.speed[1]]
            if (new_position[0] < self.bounds[0] or new_position[0] + obj.bounds[0] > self.bounds[1]):
                new_position[0] -= obj.speed[0]
            if (new_position[1] < self.bounds[0] or new_position[1] + obj.bounds[1] > self.bounds[1]):
                new_position[1] -= obj.speed[1]
            obj.position = (new_position[0], new_position[1])
            obj.last_updated = timestamp

        for listener in self.update_listeners:
            listener.on_event(pygame.event.Event(CustomEvent.AFTER_UPDATE,{"timestamp": timestamp}))

    def render(self, correction : float):
        self.screen.fill(black)

        width = self.width

        for obj in self.sprites:
            # 1 - change the rendering of sprites so that they move relative to the camera
            # 2 - only render the things which are actually on screen (view culling)
            # 3 (extension) - get the camera to zoom
            # 4 (extension) - make render correction work again as per bouncy ball demo
            
            self.screen.blit(obj.sprite, obj.position)

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