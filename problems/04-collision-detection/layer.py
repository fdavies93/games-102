from vec2 import Vec2

class Layer():
    def __init__(self, priority = 0, parallax = Vec2(1.0,1.0)):
        self.priority = priority
        self.parallax = parallax
        self.objects = [] # store by index
    
    def add_object(self, obj):
        self.objects.append(obj.id)