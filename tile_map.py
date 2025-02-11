import os
import json
from PIL import Image

class TileMap:

    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tiles: list[dict[str, Image.Image]] = [None] * self.width * self.height


    def get_idx(self, x, y):
        return x + y * self.width
    

    def get_tile(self, x, y):
        if not 0 <= x < self.width:
            return None
        if not 0 <= y < self.height:
            return None
        
        return self.tiles[self.get_idx(x, y)]
    

    def set_tile(self, x, y, tile):
        self.tiles[self.get_idx(x, y)] = tile


    def is_tile_in_bounds(self, x, y):
        return (0 <= x < self.width and
        0 <= y < self.height)
    

    def save_json(self, path):
        tile_map = {
            "width": self.width,
            "height": self.height,
            "tile_size": self.tile_size,
            "tiles": [tile["id"] if tile is not None else None for tile in self.tiles]
        }

        # for i in range(self.height):
        #     row = self.tiles[i * self.width:(i + 1) * self.width]
        #     tile_map["grid"].append(row)

        with open(path, "w+") as file:
            json.dump(tile_map, file)


    def save_image(self, path):
        size = (self.width * self.tile_size, self.height * self.tile_size)
        img = Image.new("RGBA", size, color=255)

        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[x + y * self.width]
                if tile is None: continue

                pos = (x * self.tile_size, y * self.tile_size)
                box = (*pos,
                    pos[0] + tile["image"].size[0],
                    pos[1] + tile["image"].size[1]
                )
                img.paste(tile["image"], box)

        img.save(path)
    

    def load_json(self, tiles):
        self.tiles = tiles


    def save(self, path, tile_set_images: dict[str, Image.Image]):
        self.create_path(path)
        self.create_path(os.path.join(path, "tile_sets"))

        self.save_image(self.get_file_with_ext(path, ".png"))
        self.save_json(self.get_file_with_ext(path, ".json"))
        
        if not os.path.exists(path) or not os.path.isdir(path):
            os.mkdir(path)

        for group in tile_set_images.keys():
            img_path = os.path.join(path, "tile_sets", group + ".png")
            tile_set_images[group].save(img_path)


    @staticmethod
    def create_path(path):
       if not os.path.exists(path) or not os.path.isdir(path):
            os.mkdir(path) 


    def load(self, path, groups: dict[str, list[Image.Image]]):
        try:
            json_path = self.get_file_with_ext(path, ".json")
            with open(json_path) as file:
                tile_map = json.load(file)
                self.width = tile_map["width"]
                self.height = tile_map["height"]

                for idx, tile_id in enumerate(tile_map["tiles"]):
                    if tile_id is None: continue
                    group, tile_idx = tile_id.split("_")
                    tile = groups[group][int(tile_idx)]
                    self.tiles[idx] = tile

        except Exception as e:
            print(e)

    @staticmethod
    def get_file_with_ext(path, ext, file_name=None) -> str:
        file_name = file_name or os.path.split(path)[1]
        return os.path.join(path, file_name + ext) 


    # TODO
    def save_binary(self, path):
        pass