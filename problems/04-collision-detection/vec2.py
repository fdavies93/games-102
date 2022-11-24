import numbers

class Vec2():
    
    def __init__(self, x = 0, y = 0):
        if not (isinstance(x, numbers.Number) and isinstance(y, numbers.Number)):
            raise TypeError()

        self.x = x
        self.y = y

    def __add__(self, other):
        if not isinstance(other, Vec2):
            raise TypeError()

        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Vec2):
            raise TypeError()

        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if not isinstance(other, numbers.Number):
            # note multiplying by another vector is also nonsensical as dot product, cross product are different operations
            # divide operation not implemented because it's mathematically invalid, pass 1 / scalar to mul if you want this function 
            raise TypeError()

        return Vec2(self.x * other, self.y * other)

    def __getitem__(self,key):
        if not isinstance(key, int):
            raise TypeError()
        if not (key == 0 or key == 1):
            raise ValueError()
        if key == 0:
            return self.x
        elif key == 1:
            return self.y

    def negate(self):
        return Vec2(-self.x, -self.y)

    def as_tuple(self):
        return (self.x, self.y)

    def as_list(self):
        return [self.x, self.y]