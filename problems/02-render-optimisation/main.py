import pygame, time, sys, math
pygame.init()

black = (0, 0, 0)
red_circle = pygame.image.load("assets/red-circle-small.png")

# a basic GameObject storing some simple information about an object
class GameObject():
    def __init__(self, position = (0,0), bounds=(0,0), speed = (0,0), sprite = None):
        self.position = position
        self.bounds = bounds
        self.speed = speed
        self.sprite = sprite

# never use this directly - it's a base class
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
    
    # this function helps with setting the movement speed of an object
    def change_obj_speed(self, speed, invert ):
        cur_speed = self.object.speed
        speed_change = speed
        if invert:
            speed_change = (-speed[0],-speed[1])
        self.object.speed = ( cur_speed[0] + speed_change[0], cur_speed[1] + speed_change[1] )


    def on_event(self, ev : pygame.event.Event):
        key_name = pygame.key.name(ev.key)
        # first, exit out of the function if no valid keys are pressed
        # second, check if the key was pressed or released:
        # if pressed, we can alter the speed based on which key was pressed
        # if released, we do the same but negate the values in speed_map 


# helper class for rendering the FPS counter UI element
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
    def __init__(self):
        self.size = self.width, self.height = (640, 480)
        self.screen = pygame.display.set_mode(self.size)
        self.bounds = (-10000, 10000) # minimum and maximum values of object positions
        self.fps_counter = FpsCounter()
        self.camera = GameObject(bounds=(640,480))
        self.sprites = []
        self.fps = 1 / 30

    def setup(self):
        self.ball = GameObject(position=(320,240), bounds=(111,111), sprite=pygame.image.load("assets/ball.gif"))
        # add the camera and the ball so that they're affected by update()
        self.physics_objects = []

        width = 50
        height = 50
        spacing = 100

        # DON'T EDIT: NEEDED LATER
        for i in range(width*height):
            obj_pos = ( (i * spacing) % (spacing * width), math.floor(i / height) * spacing )
            cur_obj = GameObject(obj_pos, sprite=red_circle)
            self.sprites.append(cur_obj)

        self.sprites.append(self.ball)
        #--------------------------

        # add some MoveEventListeners for the ball and the camera to make them respond to input
        self.key_listeners = []

    def process_input(self):
        for event in pygame.event.get():
            # this checks for window closed
            if event.type == pygame.QUIT: sys.exit()
            # this checks if a key was pressed or released
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                for listener in self.key_listeners:
                    listener.on_event(event)

    def update(self):
        for obj in self.physics_objects:
            new_position = [obj.position[0] + obj.speed[0], obj.position[1] + obj.speed[1]]
            if (new_position[0] < self.bounds[0] or new_position[0] + obj.bounds[0] > self.bounds[1]):
                new_position[0] -= obj.speed[0]
            if (new_position[1] < self.bounds[0] or new_position[1] + obj.bounds[1] > self.bounds[1]):
                new_position[1] -= obj.speed[1]
            obj.position = (new_position[0], new_position[1])

    def render(self, correction : float):
        self.screen.fill(black)

        width = self.width

        # for each object in the game sprites list (i.e. objects to render)
        # stage 1: render them at their position *relative to the camera*
        # stage 2: use the camera and sprite position to choose which sprites we actually want to render
        # stage 3 (extension): modify the setup function to allocate objects a position in a quadmap, use that to cull more efficiently
        # stage 3a (super extension): modify the update function to only simulate objects in tiles surrounding the quadmap and to move them between cells

        for obj in self.sprites:
            self.screen.blit(obj.sprite, obj.position)

        # where to render the FPS counter on the screen
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
                self.update()
                lag -= self.fps

            self.render(lag / self.fps)

if __name__ == "__main__":
    game = Game()
    game.main()