import json
from PIL import Image

class TileMap:

    def __init__(self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tiles = [None] * self.width * self.height


    def save(self): pass
    def load(self): pass


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
            "tiles": self.tiles
        }

        # for i in range(self.height):
        #     row = self.tiles[i * self.width:(i + 1) * self.width]
        #     tile_map["grid"].append(row)

        with open(path, "w+") as file:
            json.dump(tile_map, file)


    def save_image(self, path, images):
        size = (self.width * self.tile_size, self.height * self.tile_size)
        img = Image.new("RGB", size)

        for i in range(self.width):
            for j in range(self.height):
                tile = self.tiles[i + j * self.width]
                if tile is None: continue

                tile_img = images[tile["group"]][tile["name"]]["image"]
                pos = (j * self.tile_size, i * self.tile_size)
                box = (*pos,
                    pos[0] + tile_img.size[0],
                    pos[1] + tile_img.size[1]
                )
                img.paste(tile_img, box)

        img.save(path)
    

    def load_json(self, tiles):
        self.tiles = tiles

    # TODO
    def save_binary(self, path):
        pass