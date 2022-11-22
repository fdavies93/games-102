from vec2 import Vec2
from pygame.rect import Rect

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

    rect1 = Rect(pos1.x, pos1.y, area1.x, area1.y)
    rect2 = Rect(pos2.x, pos2.y, area2.x, area2.y)
    
    if rect1.left < rect2.left:
        left = rect1
        right = rect2
    else:
        left = rect2
        right = rect1

    if rect1.top < rect2.top:
        top = rect1
        bottom = rect2
    else:
        top = rect2
        bottom = rect1

    if left.right >= right.left:
        x_overlap = True

    if top.bottom >= bottom.top:
        y_overlap = True

    return x_overlap and y_overlap