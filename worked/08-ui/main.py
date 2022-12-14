import pygame, time, sys, math, random
from enum import IntEnum
from pathlib import Path
pygame.init()

size = width, height = (640, 480) # 20 x 15 at 32 x 32 tiles
black = (0, 0, 0)
screen = pygame.display.set_mode(size)
frame_time = 1.0 / 30.0
do_render = False
asset_path = Path("./assets/")
ui_font = pygame.font.Font(None, 24)

class CustomEvent(IntEnum):
    AFTER_UPDATE = pygame.event.custom_type()
    CLICKED_ON = pygame.event.custom_type()

class GameObject:
    animations_dict = {
        "elf_m": ["elf_m_idle_anim", "elf_m_run_anim", "elf_m_hit_anim"],
        "elf_f": ["elf_f_idle_anim", "elf_f_run_anim", "elf_f_hit_anim"],
        "knight_m": ["knight_m_idle_anim", "knight_m_run_anim", "knight_m_hit_anim"],
        "knight_f": ["knight_f_idle_anim", "knight_f_run_anim", "knight_f_hit_anim"],
        "orc_shaman": ["orc_shaman_idle_anim", "orc_shaman_run_anim"],
        "orc_warrior": ["orc_warrior_idle_anim", "orc_warrior_run_anim"],
    }

    def __init__(self, rect : pygame.rect.Rect, obj_type : str, animation_speed : float = 1):
        self.rect = rect
        self.text = None
        self.opacity = 255
        self.animations = None
        if obj_type != None:
            self.animations = GameObject.animations_dict[obj_type]
        self.cur_animation = 0
        self.animation_speed = animation_speed

# never use this - it's a base class
class EventHandler():
    def __init__(self, obj : GameObject):
        self.object = obj

    def on_event(self, ev):
        pass

class DamageUiHandler(EventHandler):
    def __init__(self, obj : GameObject, spawn_frame, travel_distance = 20, time = 1.0):
        self.travel_distance = travel_distance
        self.start_rect = obj.rect
        self.spawn_frame = spawn_frame
        self.time = time # time in seconds to do the travel
        # always goes from 255 to 0 opacity in a smooth lerp
        super().__init__(obj)

    def on_event(self, ev, cur_map):
        if not ev.type == CustomEvent.AFTER_UPDATE:
            return

        # check the current frame of the animation
        cur_frames = (ev.frame - self.spawn_frame)
        # convert the absolute time for the animation to frames using frame_time global
        time_as_frames = self.time / frame_time

        # if animation has finished, delete object (and self, indirectly)
        if cur_frames > time_as_frames:
            cur_map.objects.remove(self.object)
            return

        # calculate the scalar (value between 0-1) used to calculate opacity and position
        scalar = cur_frames / time_as_frames

        # set opacity using scalar
        self.object.opacity = 255 - (255 * scalar)

        # set position using scalar and the travel distance variable
        # move straight up - could be altered in real game to allow juicy damage animations
        self.object.rect = self.start_rect.move(0, -(self.travel_distance * scalar))
        

class OnClickHandler(EventHandler):
    # def __init__(self, obj : GameObject):
    #     self.damage_num = damage_num
    #     super().__init__(obj)

    def on_event(self, ev, cur_map):
        if (not ev.type == CustomEvent.CLICKED_ON) or cur_map.paused:
            return
        
        # create a new gameobject in the same position as object this handler is attached to
        new_obj = GameObject(self.object.rect.copy(), None)
        # make a random value and set the text to it
        new_obj.text = str(random.randint(1000, 10000))
        # add object to map
        cur_map.objects.append(new_obj)
        # create a new handler attached to the object with the appropriate spawn_time, time (to complete), and travel_distance variables
        new_handler = DamageUiHandler(new_obj, ev.frame, time=0.5, travel_distance=25)
        # add the handler to the map handlers
        cur_map.handlers.append(new_handler)

class GraphicsManager:
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
                index_out[split[0]] = {"data_file": split[1], "texture": split[2], "tile_data": {}, "animations": {}}
        return index_out

    def load_tileset_data(self, name):
        data_file = asset_path / self.tile_sets[name]["data_file"]
        with open(data_file, 'r') as f:
            for line in f:
                split = line.split()
                # not a tile or animation, ignore it
                if len(split) != 5 and len(split) != 6:
                    continue
                # otherwise, store this data as a rect and load to animations if needed
                num_tiles = 1
                # note split[0] is immutable, while tile_name shouldn't be
                tile_name = split[0]
                is_anim = False

                if len(split) == 6:
                    is_anim = True
                    num_tiles = int(split[5])
                    self.tile_sets[name]["animations"][split[0]] = []

                r = [int(x) for x in split[1:5]]
                for frame in range(num_tiles):
                    if frame > 0:
                        tile_name = split[0] + f"_{frame}"
                    self.tile_sets[name]["tile_data"][tile_name] = {"rect": pygame.Rect(r)}
                    if is_anim:
                        self.tile_sets[name]["animations"][split[0]].append(tile_name)
                    r[0] += r[2]
                
        self.run_level = 2
        print(f"Loaded data from {name}")
        print(self.tile_sets[name])
    
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
        self.tile_sets[name]["animations"] = {}
        print(f"Deleted data from {name}")
        self.run_level = 1

class Map:
    def __init__(self, tileset, grid_scale):
        self.tileset = tileset
        self.tile_data = []
        self.handlers = []
        self.objects : list[GameObject] = []
        self.grid_scale = grid_scale
        self.paused = False

    def load_data(self, map_file):
        with open(asset_path / map_file, "r") as f:
            for line in f:
                split = line.split()
                if len(split) == 3:
                    print(split)
                    obj_rect = pygame.rect.Rect(int(split[1]), int(split[2]), 32, 32)
                    cur_obj = GameObject(obj_rect, split[0], 0.5)
                    cur_handler = OnClickHandler(cur_obj)
                    self.objects.append(cur_obj)
                    self.handlers.append(cur_handler)
                    
                elif len(split) == 5:
                    self.tile_data.append({"tile": split[0], "pos": (int(split[1]), int(split[2])), "size": (int(split[3]), int(split[4])) })
                
    def check_click(self, point, frames):
        print("Check click on map")
        for handler in self.handlers:
            if handler.object.rect.collidepoint(point[0], point[1]):
                handler.on_event(pygame.event.Event(CustomEvent.CLICKED_ON,{"frame": frames}), self)

    def render(self, tile_manager, cur_frame):
        for r in self.tile_data:
            start_x = r["pos"][0] * self.grid_scale[0]
            start_y = r["pos"][1] * self.grid_scale[1]
            width = r["size"][0]
            height = r["size"][1]
            sprite = tile_manager.tile_sets[self.tileset]["tile_data"][r["tile"]]["surface"]
            for x in range(width):
                for y in range(height):
                    screen.blit(sprite, (start_x + (x * self.grid_scale[0]), start_y + (y * self.grid_scale[1])))
        for obj in self.objects:
            sprite = None

            if obj.animations != None:
                cur_animation_frames = tile_manager.tile_sets[self.tileset]["animations"][obj.animations[obj.cur_animation]]
                # loop the animation
                cur_frame_tile = cur_animation_frames[math.floor(cur_frame * obj.animation_speed) % len(cur_animation_frames)]
                # get the actual sprite for the animation
                sprite : pygame.surface.Surface = tile_manager.tile_sets[self.tileset]["tile_data"][cur_frame_tile]["surface"]
            text_surface = None
            
            if obj.text != None:
                text_surface = ui_font.render(obj.text, True, (255,255,255))
                text_surface.set_alpha(obj.opacity)

            if obj.opacity < 255 and sprite != None:
                # used for animations, so it should be okay to spawn new surfaces even though this is generally suboptimal
                sprite = sprite.copy()
                sprite.set_alpha(obj.opacity)
            
            if sprite != None:
                screen.blit(sprite, obj.rect)
    
            if text_surface != None:
                screen.blit(text_surface, obj.rect)

def process_input(manager : GraphicsManager, my_map : Map, frames: int):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            for tileset in manager.tile_sets:
                manager.unload_tileset_sprite(tileset)
                manager.unload_tileset_data(tileset)
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            my_map.check_click(pygame.mouse.get_pos(), frames)
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

def render(manager, my_map, frames):
    screen.fill(black)
    if do_render:
        my_map.render(manager, frames)
    pygame.display.flip()

def update(cur_map, frames):
    for handler in cur_map.handlers:
        handler.on_event(pygame.event.Event(CustomEvent.AFTER_UPDATE,{"frame": frames}), cur_map)

    # remove any handlers whose objects have been deleted
    # required to clean up after objects are destroyed
    new_handlers = []
    for handler in cur_map.handlers:
        if handler.object not in cur_map.objects:
            continue
        new_handlers.append(handler)
    cur_map.handlers = new_handlers
        

def main():
    manager = GraphicsManager(asset_path / "index")
    # manager.load_tileset_data("dungeon")
    # manager.load_tileset_sprite("dungeon", 2)

    frames = 0
    my_map = Map("dungeon", (32, 32))
    my_map.load_data("map")

    while (True):
        start = time.time()
        process_input(manager, my_map,frames)
        update(my_map, frames)
        render(manager, my_map, frames)
        sleep_time = start + frame_time - time.time()
        if sleep_time < 0:
            sleep_time = 0
        time.sleep(sleep_time)
        frames += 1

if __name__ == "__main__":
    main()