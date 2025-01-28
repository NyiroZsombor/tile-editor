import tkinter as tk
from tile_map import TileMap

class Canvas(tk.Canvas):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.tile_size = 64
        self.display_grid = True

        self.zoom = 1
        self.x = 0
        self.y = 0
        self.grabbed = False
        self.grab_start_x = 0
        self.grab_start_y = 0
        self.tile_map = TileMap(10, 10)

        self.bind("<Button-1>", self.mouse_click)
        self.bind("<ButtonRelease-1>", self.mouse_leave)
        self.bind("<Motion>", self.mouse_move)
        #self.bind("<Leave>", self.mouse_leave)

        self.update()


    def mouse_click(self, event):
        if event.state & 1:
            self.grabbed = True
            self.grab_start_x = event.x
            self.grab_start_y = event.y
        else:
            tile_x = (event.x - self.x) // self.tile_size
            tile_y = (event.y - self.y) // self.tile_size
            item_id = self.master.master.tile_group_tree.focus()
            tile = self.master.master.tile_group_tree.item(item_id)["text"]
            print(tile)

            self.tile_map.set_tile(tile_x, tile_y, tile)


    def mouse_move(self, event):
        if self.grabbed:
            self.x += event.x - self.grab_start_x
            self.y += event.y - self.grab_start_y

            self.grab_start_x = event.x
            self.grab_start_y = event.y


    def mouse_leave(self, event):
        self.grabbed = False


    def changeZoom(self, z):
        self.x *= z
        self.y *= z
        self.tile_size *= z
        self.zoom *= z

        self.x = int(self.x)
        self.y = int(self.y)
        self.tile_size = int(self.tile_size)

        print(self.x, self.y, self.tile_size, self.zoom)


    def draw(self):
        self.delete(tk.ALL)
        self.create_rectangle(
            0, 0, self.winfo_width(), self.winfo_height(), fill="lightblue"
        )
        self.draw_tiles()
        #self.draw_grid()


    def draw_tiles(self):
        width_tiles = self.winfo_width() // self.tile_size
        height_tiles = self.winfo_height() // self.tile_size
        tile_x = self.x // self.tile_size
        tile_y = self.y // self.tile_size

        start_x = max(tile_x, -1)
        start_y = max(tile_y, -1)
        end_x = max(min(width_tiles + 1, self.tile_map.width + tile_x), 0)
        end_y = max(min(height_tiles + 1, self.tile_map.height + tile_y), 0)
        
        for j in range(start_y, end_y):
            for i in range(start_x, end_x):
                tile = self.tile_map.get_tile(i - tile_x, j - tile_y)
                rem_x = self.x % self.tile_size
                rem_y = self.y % self.tile_size

                canvas_x = i * self.tile_size + rem_x
                canvas_y = j * self.tile_size + rem_y

                if self.display_grid: outline = "black"
                else: outline = ""

                if not tile is None:
                    self.create_rectangle(
                        canvas_x,
                        canvas_y,
                        canvas_x + self.tile_size,
                        canvas_y + self.tile_size,
                        fill="purple",
                        outline=outline
                    )
                else:
                    self.create_rectangle(
                        canvas_x,
                        canvas_y,
                        canvas_x + self.tile_size,
                        canvas_y + self.tile_size,
                        fill="lightblue",
                        outline=outline
                    )


    def draw_grid(self):
        if not self.display_grid:
            return
        
        for i in range(self.winfo_width() // self.tile_size + 1):
            self.create_line(
                i * self.tile_size + self.x, 0,
                i * self.tile_size + self.x, self.winfo_height(),
                fill="grey", width=1
            )

        for i in range(self.winfo_height() // self.tile_size + 1):
            self.create_line(
                0, i * self.tile_size + self.y,
                self.winfo_width(), i * self.tile_size + self.y,
                fill="grey", width=1
            )