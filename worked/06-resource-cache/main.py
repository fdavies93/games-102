import pygame, time, sys
from pathlib import Path
pygame.init()

size = width, height = (640, 480) # 20 x 15 at 32 x 32 tiles
black = (0, 0, 0)
screen = pygame.display.set_mode(size)
frame_time = 1.0 / 60.0
do_render = False
asset_path = Path("./assets/")

class TileManager:
    def __init__(self, meta_index):
        # includes only name and filename of index {"dungeon": "index"}
        self.run_level = 0
        self.tile_sets = self.load_index(meta_index)
        self.run_level = 1

    def load_index(self, index):
        index_out = {}
        with open(index, "r") as f:
            for line in f:
                split = line.split()
                index_out[split[0]] = {"data_file": split[1], "texture": split[2], "tile_data": {}}
        return index_out

    def load_tileset_data(self, name):
        data_file = asset_path / self.tile_sets[name]["data_file"]
        with open(data_file, 'r') as f:
            for line in f:
                split = line.split()
                # not a tile, ignore it
                if len(split) != 5:
                    continue
                # otherwise, store this data as a rect
                r = [int(x) for x in split[1:5]]
                self.tile_sets[name]["tile_data"][split[0]] = {"rect": pygame.Rect(r)}
        self.run_level = 2
        print(f"Loaded data from {name}")
    
    def load_tileset_sprite(self, ts, zoom_level = 1):
        # it's already loaded
        if "sprite" in self.tile_sets[ts]:
            return
        image_path = asset_path / self.tile_sets[ts]["texture"]
        tileset_sprite = pygame.image.load(image_path).convert_alpha()
        tileset_sprite = pygame.transform.scale(tileset_sprite, (tileset_sprite.get_width() * zoom_level, tileset_sprite.get_height() * zoom_level))
        self.tile_sets[ts]["sprite"] = tileset_sprite
        for tile in self.tile_sets[ts]["tile_data"].values():
            r : pygame.Rect = tile["rect"]
            scaled_rect = pygame.Rect(r.left * zoom_level, r.top * zoom_level, r.width * zoom_level, r.height * zoom_level)
            tile["surface"] = tileset_sprite.subsurface(scaled_rect)
        self.run_level = 3
        print(f"Loaded sprites from {ts}")


    def unload_tileset_sprite(self, name):
        for tile in self.tile_sets[name]["tile_data"].values():
            del tile["surface"]
        del self.tile_sets[name]["sprite"]
        print(f"Deleted sprites from {name}")
        self.run_level = 2

    def unload_tileset_data(self, name):
        # just wipe everything
        self.tile_sets[name]["tile_data"] = {}
        print(f"Deleted data from {name}")
        self.run_level = 1

class Map:
    def __init__(self, tileset, grid_scale):
        self.tileset = tileset
        self.tile_data = []
        self.grid_scale = grid_scale

    def load_data(self, map_file):
        with open(asset_path / map_file, "r") as f:
            for line in f:
                split = line.split()
                if len(split) != 5:
                    continue
                self.tile_data.append({"tile": split[0], "pos": (int(split[1]), int(split[2])), "size": (int(split[3]), int(split[4])) })

    def render(self, tile_manager):
        for r in self.tile_data:
            start_x = r["pos"][0] * self.grid_scale[0]
            start_y = r["pos"][1] * self.grid_scale[1]
            width = r["size"][0]
            height = r["size"][1]
            sprite = tile_manager.tile_sets[self.tileset]["tile_data"][r["tile"]]["surface"]
            for x in range(width):
                for y in range(height):
                    screen.blit(sprite, (start_x + (x * self.grid_scale[0]), start_y + (y * self.grid_scale[1])))

def process_input(manager : TileManager):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            for tileset in manager.tile_sets:
                manager.unload_tileset_sprite(tileset)
                manager.unload_tileset_data(tileset)
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            if key_name not in ["1", "2", "3"]:
                return

            unload_sprites = False
            unload_data = False
            load_sprites = False
            load_data = False
            new_render = True
            
            if key_name == "1":
                # meta index only, no render
                if manager.run_level > 2:
                    unload_sprites = True
                if manager.run_level > 1:
                    unload_data = True
                new_render = False
            if key_name == "2":
                # data loaded but no sprites; no render
                if manager.run_level > 2:
                    unload_sprites = True
                if manager.run_level < 2:
                    load_data = True
                new_render = False
            if key_name == "3":
                # everything is loaded; render
                if manager.run_level < 2:
                    load_data = True
                if manager.run_level < 3:
                    load_sprites = True
                new_render = True

            for tileset in manager.tile_sets:
                if load_data:
                    manager.load_tileset_data(tileset)
                if load_sprites:
                    manager.load_tileset_sprite(tileset, 2)
                if unload_sprites:
                    manager.unload_tileset_sprite(tileset)
                if unload_data:
                    manager.unload_tileset_data(tileset)
            
            global do_render
            do_render = new_render

def render(manager, my_map):
    screen.fill(black)
    if do_render:
        my_map.render(manager)
    pygame.display.flip()    

def main():
    manager = TileManager(asset_path / "index")
    # manager.load_tileset_data("dungeon")
    # manager.load_tileset_sprite("dungeon", 2)

    my_map = Map("dungeon", (32, 32))
    my_map.load_data("map")

    while (True):
        start = time.time()
        process_input(manager)
        render(manager, my_map)
        sleep_time = start + frame_time - time.time()
        if sleep_time < 0:
            sleep_time = 0
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()