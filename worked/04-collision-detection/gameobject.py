from vec2 import Vec2

class GameObject():
    def __init__(self, gm : "Game", position = Vec2(0,0), bounds=Vec2(0,0), speed = Vec2(0,0), sprite = None):
        self.id = gm.next_id()
        self.position = position
        self.bounds = bounds
        self.speed = speed
        self.sprite = sprite
        self.last_updated = 0