import keyboard
from os import system
from time import sleep

shutdown = False
player_x : int = 1
player_y : int = 1
player_char = '@'
floor_char = '.'
wall_char = '█'
game_w = 10
game_h = 10

grid = []

def start():
    for y in range(game_h):
        grid.append([])
        for x in range(game_w):
            if x == 0 or x == game_w - 1 or y == 0 or y == game_h - 1: # edge
                grid[y].append(wall_char)
            elif x > 3 and x < 6 and y > 3 and y < 6:
                grid[y].append(wall_char)
            else:
                grid[y].append(floor_char)

def render():
    system('clear')
    for y in range(game_h):
        for x in range(game_w):
            if x == player_x and y == player_y:
                print(player_char, end="")
            else:
                print(grid[y][x], end="")
        print()

def move_to(x, y):
    if (grid[y][x] != wall_char):
        # allow move
        global player_x 
        player_x = x
        global player_y
        player_y = y

key_map = {
    'a': lambda : move_to(player_x - 1, player_y),
    'w': lambda : move_to(player_x, player_y - 1),
    's': lambda : move_to(player_x, player_y + 1),
    'd': lambda : move_to(player_x + 1, player_y)
}

def update():
    # you can use keyboard.is_pressed to update player_x and player_y
    for k in key_map:
        if keyboard.is_pressed(k):
            key_map[k]()

def main():
    start()
    while True:
        update()
        render()
        sleep(0.1)

if __name__ == "__main__":
    main()