from vec2 import Vec2
from pygame.rect import Rect
from dataclasses import dataclass

@dataclass
class Overlap():
    obj : int
    overlaps : Vec2

def clamp_between(to_clamp, lower, upper):
    output = to_clamp
    if output < lower:
        output = lower
    elif output > upper:
        output = upper
    return output
    
def check_collision(pos1: Vec2, pos2: Vec2, area1 : Vec2, area2 : Vec2):
    x_overlap = False
    y_overlap = False

    # collision detection, problem 2
    # write the math functions to determine if there's been a collision between object 1 and object 2
    # you can write this using logic about the bounds of the object
    # or if you prefer the simple method, just use the pygame Rect class

    # rectangles need to overlap on both the x and y axis to collide
    return x_overlap and y_overlap