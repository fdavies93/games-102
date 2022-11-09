import pygame, sys, time
pygame.init()

size = width, height = (640, 480)
speed = [10, 10]
black = (0, 0, 0)
screen = pygame.display.set_mode(size)

ball = pygame.image.load("assets/ball.gif")
ball_rect = ball.get_rect()

seconds_per_frame = 1 / 32

def process_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

def update(timestep = 1.0):
    global ball_rect
    this_update = (speed[0] * timestep, speed[1] * timestep)
    ball_rect = ball_rect.move(this_update)
    if ball_rect.left < 0 or ball_rect.right > width:
        speed[0] = -speed[0]

    if ball_rect.top < 0 or ball_rect.bottom > height:
        speed[1] = -speed[1]

def render(frame_lag = 0):
    global ball_rect
    global ball
    screen.fill(black)

    render_position = ( 
        ball_rect[0] + (speed[0] * frame_lag),
        ball_rect[1] + (speed[1] * frame_lag)
    )

    screen.blit(ball, render_position)
    pygame.display.flip()


def loop_naive():
    while True:
        process_input()
        update()
        render()

def loop_limited():
    while True:
        process_input()
        start = time.time()
        update()
        render()
        time.sleep(start + seconds_per_frame - time.time())

def loop_fluid():
    prev = time.time()
    while True:
        current = time.time()
        delta = current - prev
        process_input()
        update(delta)
        render()
        prev = current

def loop_separated(correction = False):
    prev = time.time()
    lag = 0.0

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