import pygame
pygame.init()

size = width, height = (1280, 960)
black = (0, 0, 0)
screen = pygame.display.set_mode(size)

class TileManager:
    def __init__(self, meta_index):
        # includes only name and filename of index {"dungeon": "index"}
        self.tile_sets = self.load_index(meta_index)

    def load_index(self, index):
        index_out = {}
        with open(index, "r") as f:
            for line in f:
                split = line.split()
                index_out[split[0]] = {"data_file": split[1], "texture": split[2], "tile_data": {}}
        return index_out

    def load_tileset_data(self, name):
        with open('./assets/' + self.tile_sets[name]["data_file"], 'r') as f:
            for line in f:
                split = line.split()
                # not a tile, ignore it
                if len(split) != 5:
                    continue
                # otherwise, store this data as a rect
                r = [int(x) for x in split[1:5]]
                self.tile_sets[name]["tile_data"][split[0]] = {"rect": pygame.Rect(r)}
    
    def load_tileset_sprite(self, ts):
        # it's already loaded
        if "sprite" in self.tile_sets[ts]:
            return
        image_path = "./assets/" + self.tile_sets[ts]["texture"]
        tileset_sprite = pygame.image.load(image_path).convert_alpha()
        self.tile_sets[ts]["sprite"] = tileset_sprite
        for tile in self.tile_sets[ts]["tile_data"].values():
            tile["surface"] = tileset_sprite.subsurface(tile["rect"])


    def unload_tileset(self,name):
        pass


class Map:
    def __init__(self, tileset):
        self.tilemap = tileset
        pass

def main():
    manager = TileManager("./assets/index")
    manager.load_tileset_data("dungeon")
    manager.load_tileset_sprite("dungeon")
    print (manager.tile_sets)

if __name__ == "__main__":
    main()