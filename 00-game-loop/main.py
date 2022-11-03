import keyboard

shutdown = False
player_x = 1
player_y = 1
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
            if x == 0 or x == game_w - 1 or y == 0 or y == game_h - 1:
                grid[y].append(wall_char)
            else:
                grid[y].append(floor_char)

def render():
    for y in range(game_h):
        for x in range(game_w):
            if x == player_x and y == player_y:
                print(player_char, end="")
            else:
                print(grid[y][x], end="")
        print()

def update():
    # you can use keyboard.is_pressed to update player_x and player_y
    pass

def main():
    start()
    render()

if __name__ == "__main__":
    main()