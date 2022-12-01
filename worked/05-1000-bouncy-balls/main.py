import pygame, sys, time, random
from pygame.rect import Rect
from enum import IntEnum
pygame.init()

size = width, height = (1280, 960)
black = (0, 0, 0)
screen = pygame.display.set_mode(size)

ball_sprite = pygame.image.load("assets/red-circle-small.png").convert_alpha()
block_sprite = pygame.image.load("assets/block.png").convert_alpha()

game_objects = []

seconds_per_frame = 1 / 32

frames = 0
prev_render = 0
prev_frames = 0

font = pygame.font.Font(None, 24)

class OBJECT_TYPE(IntEnum):
    BALL = 0,
    BLOCK = 1

class GameObject():
    def __init__(self, obj_type : OBJECT_TYPE, position : Rect, speed = [5, 5]):
        if obj_type == OBJECT_TYPE.BALL:
            sprite = ball_sprite
        elif obj_type == OBJECT_TYPE.BLOCK:
            sprite = block_sprite

        self.rect = Rect(position.top, position.left, sprite.get_width(), sprite.get_height())
        self.sprite = sprite
        self.type = obj_type
        self.speed = [speed[0], speed[1]]

def process_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

def next_rect(timestep, obj):
    speed = [obj.speed[0] * timestep, obj.speed[1] * timestep]
    return Rect(obj.rect.top + speed[0],obj.rect.top + speed[1], obj.rect.w, obj.rect.h)

def check_collision(obj_1, obj_2, callback = None):
    if obj_1.rect.colliderect(obj_2.rect):
        if callback != None:
            callback(obj_1, obj_2, {})
        return True

def ball_oob_handler(obj, data):
    if data["x"]:
        obj.speed[0] = -obj.speed[0]
    if data["y"]:
        obj.speed[1] = -obj.speed[1]

def ball_collision_handler(obj_1, obj_2, data):    
    obj_1.speed[0] = -obj_1.speed[0]
    obj_1.speed[1] = -obj_1.speed[1]
    obj_2.speed[0] = -obj_2.speed[0]
    obj_2.speed[1] = -obj_2.speed[1]

def check_out_of_bounds(obj : GameObject, callback):
    oob_data = {"x": False, "y": False}
    new_rect = obj.rect
    if new_rect.left < 0 or new_rect.right > width:
        oob_data["x"] = True

    if new_rect.top < 0 or new_rect.bottom > height:
        oob_data["y"] = True

    if oob_data["x"] or oob_data["y"]:
        callback(obj, oob_data)

def update():
    for i, obj in enumerate(game_objects):
        # bounds check

        if obj.type == OBJECT_TYPE.BALL:
            handler = ball_collision_handler
        
        # # shaky collisions bug; probably need to get everything's next position before doing checks on moving objs
        for obj_2 in game_objects[i+1:]:
            check_collision(obj, obj_2, handler)

        if obj.type == OBJECT_TYPE.BALL:
            handler = ball_oob_handler

        check_out_of_bounds(obj, handler)

        this_update = (obj.speed[0], obj.speed[1])
        obj.rect = obj.rect.move(this_update)

        

def render(frame_lag = 0):

    global prev_render
    global prev_frames
    global frames
    global font

    screen.fill(black)

    if time.time() > prev_render + 0.25:
        prev_frames = (frames * 4)
        frames = 0
        prev_render = time.time()

    for obj in game_objects:
        render_position = ( 
            obj.rect[0] + (obj.speed[0] * frame_lag),
            obj.rect[1] + (obj.speed[1] * frame_lag)
        )

        if obj.type == OBJECT_TYPE.BALL:
            sprite = ball_sprite
        elif obj.type == OBJECT_TYPE.BLOCK:
            sprite = block_sprite

        screen.blit(sprite, render_position)

    font_surface = font.render(f"FPS: {str(prev_frames)}", True, (255,255,255))
    screen.blit(font_surface, ( width - (width / 5), 20 ))

    pygame.display.flip()    
    frames += 1

def setup():
    for i in range(101):   
        new_rect = Rect(random.randint(50, width - 50), random.randint(50, width - 50), 0, 0)
        new_obj = GameObject(OBJECT_TYPE.BALL, new_rect)
        collisions = 1
        while collisions > 0:
            collisions = 0
            for obj in game_objects:
                if check_collision(new_obj, obj):
                    collisions += 1
                    new_obj.rect.x = random.randint(50, width - 50)
                    new_obj.rect.y = random.randint(50, width - 50)
                    break
                
        
        game_objects.append(new_obj)

def loop_separated(correction = False):
    prev = time.time()
    lag = 0.0
    setup()

    while(True):
        current = time.time()
        delta = current - prev
        prev = current
        lag += delta
        
        process_input()

        while(lag >= seconds_per_frame):
            update()
            lag -= seconds_per_frame
        
        if correction:
            render(lag / seconds_per_frame)
        else:
            render()


if __name__ == "__main__":
    loop_separated(True)