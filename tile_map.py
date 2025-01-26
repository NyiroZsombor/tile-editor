class TileMap:

    def __init__(self, width, height):
        self.width = width
        self.height = height
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