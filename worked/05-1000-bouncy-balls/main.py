import pygame, sys, time, random, math
from pygame.rect import Rect
from enum import IntEnum
pygame.init()

size = width, height = (1280, 960)
black = (0, 0, 0)
screen = pygame.display.set_mode(size)

ball_sprite = pygame.image.load("assets/red-circle-small.png").convert_alpha()
block_sprite = pygame.image.load("assets/block.png").convert_alpha()

blocks_to_spawn = 25
balls_to_spawn = 1
render_objs = True

game_objects = []
balls = []
blocks = []

seconds_per_frame = 1 / 32

frames = 0
prev_render = 0
prev_frames = 0

static_partition_scale = 500 # 160 is a reasonable size and goes into 1280 and 960 ok
dynamic_partition_objects = 2 # 2 objects is optimal for collision

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

class StaticPartition():
    def __init__(self, cell_size : int):
        self.cell_size = cell_size
        self.cells = {}
    
    def get_grid_coords(self,obj : GameObject):
        return ( math.floor(obj.rect.x / self.cell_size) , math.floor(obj.rect.y / self.cell_size) )

    def add_object(self, obj: GameObject, index : int):
        x_cell, y_cell = self.get_grid_coords(obj)
        
        if x_cell not in self.cells:
            self.cells[x_cell] = {}
        
        if y_cell not in self.cells[x_cell]:
            self.cells[x_cell][y_cell] = set() # list of objects in the appropriate cell

        self.cells[x_cell][y_cell].add(index)

    def get_neighbors(self, obj: GameObject, index : int):
        x_cell, y_cell = self.get_grid_coords(obj)

        if x_cell not in self.cells or y_cell not in self.cells[x_cell] or index not in self.cells[x_cell][y_cell]:
            return []

        return list(self.cells[x_cell][y_cell].difference( {index} ))

    def update_object(self, obj: GameObject, index : int):
        x_cell, y_cell = self.get_grid_coords(obj)
        prev_x_cell = math.floor((obj.rect.x - obj.speed[0]) / self.cell_size)
        prev_y_cell = math.floor((obj.rect.y - obj.speed[1]) / self.cell_size)
        
        # no change
        if x_cell == prev_x_cell and y_cell == prev_y_cell:
            return

        # remove from old location
        self.cells[prev_x_cell][prev_y_cell].remove(index)

        # add to new location
        self.add_object(obj, index)

    def prune_cells(self):
        prune_x_cells = []
        prune_x_y = []
        for cell_x in self.cells:
            prune_x = True
            for cell_y in self.cells[cell_x]:
                if len(self.cells[cell_x][cell_y]) == 0:
                    prune_x_y.append( (cell_x, cell_y) )
                else:
                    prune_x = False
            if prune_x:
                prune_x_cells.append(cell_x)
        
        for cell in prune_x_y:
            del self.cells[cell[0], cell[1]]
        
        for x_cell in prune_x_cells:
            del self.cells[x_cell]


static_partition = StaticPartition(static_partition_scale)

def process_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

def next_rect(timestep, obj):
    speed = [obj.speed[0] * timestep, obj.speed[1] * timestep]
    return Rect(obj.rect.top + speed[0],obj.rect.top + speed[1], obj.rect.w, obj.rect.h)

def check_collision(obj_1, obj_2, callback = None):
    if obj_1.rect.colliderect(obj_2.rect):
        
        if obj_1.type == OBJECT_TYPE.BLOCK or obj_2.type == OBJECT_TYPE.BLOCK:
            print ("Collision!")
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

def check_out_of_bounds(obj : GameObject, callback = None):
    oob_data = {"x": False, "y": False}
    new_rect = obj.rect
    if new_rect.left < 0 or new_rect.right > width:
        oob_data["x"] = True

    if new_rect.top < 0 or new_rect.bottom > height:
        oob_data["y"] = True

    if oob_data["x"] or oob_data["y"]:
        if callback != None:
            callback(obj, oob_data)
        return True
    return False


def naive_update():
    for i, obj in enumerate(game_objects):
        # bounds check

        handler = ball_collision_handler

        for obj_2 in game_objects[i+1:]:
            check_collision(obj, obj_2, handler)

        handler = ball_oob_handler

        check_out_of_bounds(obj, handler)

        this_update = (obj.speed[0], obj.speed[1])
        obj.rect = obj.rect.move(this_update)

def old_skool_update():
    for i, obj in enumerate(balls):
        handler = ball_collision_handler

        for obj_2 in balls[i+1:]:
            check_collision(obj, obj_2, handler)
        
        # good optimisation if we only have 1 ball and a ton of blocks
        for block in blocks:
            check_collision(obj, block, handler)

        handler = ball_oob_handler

        check_out_of_bounds(obj, handler)

        this_update = (obj.speed[0], obj.speed[1])
        obj.rect = obj.rect.move(this_update)

def update_cell(cell : set):
    cell_list = list(cell)
    handler = ball_collision_handler
    for i in cell_list:
        obj = game_objects[i]
        for i2 in cell_list[i+1:]:
            obj_2 = game_objects[i2]
            check_collision(obj, obj_2, handler)
        handler = ball_oob_handler
        check_out_of_bounds(obj, handler)
        this_update = (obj.speed[0], obj.speed[1])
        obj.rect = obj.rect.move(this_update)
        static_partition.update_object(obj, i)

def linear_partition_update():

    for x_cell in static_partition.cells:
        for y_cell in static_partition.cells[x_cell]:
            cur_cell = static_partition.cells[x_cell][y_cell]
            update_cell(cur_cell)

    static_partition.prune_cells()
    # for i, obj in enumerate(game_objects):
    #     handler = ball_collision_handler
    #     neighbors = static_partition.get_neighbors(obj, i)
    #     for i2 in neighbors:
    #         # print (i2)
    #         obj_2 = game_objects[i2]
    #         check_collision(obj, obj_2, handler)
    #     handler = ball_oob_handler
    #     check_out_of_bounds(obj, handler)
    #     this_update = (obj.speed[0], obj.speed[1])
    #     obj.rect = obj.rect.move(this_update)
    #     static_partition.update_object(obj, i)

def update():
    # swap this out for different methods
    # 1: naive collision - check everything against everything else
    # gets exponentially worse the more things there are in game
    # can check by increasing blocks or balls easily
    # naive_update()
    # 2: old-skool optimisation - check the balls only (because the blocks don't do anything interesting)
    # gets exponentially worse the more balls there are but only linearly worse for blocks
    # can check by looking at the difference between 1 ball / 200 blocks and 500 balls / 1 block
    # both are rendering similar pixel amounts but 500 ball example is far slower
    # old_skool_update()
    # 3: linear spatial partition (grid system)
    linear_partition_update()
    # 4: dynamic spatial partition (quadtree)
    # 5: combined system (blocks in a quadtree)
    pass

def setup():

    for i in range(blocks_to_spawn):
        new_rect = Rect(random.randint(50, width - 50), random.randint(50, width - 50), 0, 0)
        new_obj = GameObject(OBJECT_TYPE.BLOCK, new_rect, [0,0])
        collisions = True
        while collisions:
            collisions = False
            for obj in game_objects:
                if check_collision(new_obj, obj):
                    collisions = True
                    new_obj.rect.x = random.randint(50, width - 50)
                    new_obj.rect.y = random.randint(50, width - 50)
                    break
        game_objects.append(new_obj)
        blocks.append(new_obj)
        static_partition.add_object(new_obj, len(game_objects) - 1)


    for i in range(balls_to_spawn):   
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
        balls.append(new_obj)
        static_partition.add_object(new_obj, len(game_objects) - 1)
        
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

        if render_objs:
            screen.blit(sprite, render_position)

    font_surface = font.render(f"FPS: {str(prev_frames)}", True, (255,255,255))
    screen.blit(font_surface, ( width - (width / 5), 20 ))

    pygame.display.flip()    
    frames += 1

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