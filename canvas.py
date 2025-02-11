import tkinter as tk
from PIL import Image, ImageTk
from tile_map import TileMap

class Canvas(tk.Canvas):

    def __init__(self, master, width_tile, height_tile,
    tile_size, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.editor = self.master.master
        self.tile_size = tile_size
        self.scaled_tile_size = tile_size
        self.display_grid = True
        self.display_ruler = True
        self.bg_color = "#" + self.editor.master.settings["background_color"]

        self.zoom = 1
        self.x = 0
        self.y = 0
        self.grabbed = False
        self.grab_start_x = 0
        self.grab_start_y = 0
        self.tile_map = TileMap(width_tile, height_tile, tile_size)

        self.bind("<Button-1>", self.mouse_click)
        self.bind("<Button-3>", self.mouse_click_b3)
        self.bind("<ButtonRelease-1>", self.mouse_leave)
        self.bind("<B1-Motion>", self.mouse_b1_motion)
        self.bind("<B3-Motion>", self.mouse_b3_motion)
        #self.bind("<Leave>", self.mouse_leave)

        self.update()


    def mouse_click(self, event):
        if event.state & 1:
            self.grabbed = True
            self.grab_start_x = event.x
            self.grab_start_y = event.y
        else:
            self.place_tile(event)


    def mouse_click_b3(self, event):
        self.place_tile(event, True)


    def mouse_b1_motion(self, event):
        if self.grabbed:
            self.x += event.x - self.grab_start_x
            self.y += event.y - self.grab_start_y

            self.grab_start_x = event.x
            self.grab_start_y = event.y
        else:
            self.place_tile(event)


    def mouse_b3_motion(self, event):
        if not self.grabbed:
            self.place_tile(event, True)


    def place_tile(self, event, erase=False):
        if self.editor.tile_groups.selected_tile is None and not erase:
            return

        tile_x = (event.x - self.x) // self.scaled_tile_size
        tile_y = (event.y - self.y) // self.scaled_tile_size

        if not self.tile_map.is_tile_in_bounds(tile_x, tile_y):
            return

        if not erase:
            tile = self.editor.tile_groups.selected_tile
            self.tile_map.set_tile(tile_x, tile_y, tile)
        else:
            self.tile_map.set_tile(tile_x, tile_y, None)


    def mouse_leave(self, event):
        self.grabbed = False


    def change_zoom(self, z):
        if self.zoom * z > 16: return
        if self.zoom * z < 0.0625: return
        self.zoom *= z
        self.scaled_tile_size = int(self.tile_size * self.zoom)

        # self.x = int(self.x * self.zoom + self.zoom * self.winfo_width() / 2)
        # self.y = int(self.y * self.zoom + self.zoom * self.winfo_height() / 2)

        groups = self.editor.tile_groups.groups

        for group in groups.keys():
            for i in range(len(groups[group])):
                img: Image.Image = groups[group][i]["image"]
                scaled = img.resize((
                    self.scaled_tile_size,
                    self.scaled_tile_size,
                ), Image.Resampling.NEAREST)

                self.editor.tile_groups.groups[group][i]["scaled"] = ImageTk.PhotoImage(scaled)


    def draw(self):
        self.delete(tk.ALL)
        self.create_rectangle(
            0, 0, self.winfo_width(), self.winfo_height(), fill="gray"
        )
        self.draw_background()
        self.draw_tiles()
        if self.display_grid:
            self.draw_grid()
        if self.display_ruler:
            self.draw_ruler()


    def draw_background(self):
        x0 = max(self.x, 0)
        y0 = max(self.y, 0)
        x1 = min(
            self.tile_map.width * self.scaled_tile_size + self.x,
            self.winfo_width()
        )
        y1 = min(
            self.tile_map.height * self.scaled_tile_size + self.y,
            self.winfo_height()
        )
        #print(x0, y0, x1, y1)
        self.create_rectangle(x0, y0, x1, y1, fill=self.bg_color)


    def draw_tiles(self):
        width_tiles = self.winfo_width() // self.scaled_tile_size
        height_tiles = self.winfo_height() // self.scaled_tile_size
        tile_x = self.x // self.scaled_tile_size
        tile_y = self.y // self.scaled_tile_size

        start_x = max(tile_x, -1)
        start_y = max(tile_y, -1)
        end_x = max(min(width_tiles + 1, self.tile_map.width + tile_x), 0)
        end_y = max(min(height_tiles + 1, self.tile_map.height + tile_y), 0)
        
        for j in range(start_y, end_y):
            for i in range(start_x, end_x):
                tile = self.tile_map.get_tile(i - tile_x, j - tile_y)
                rem_x = self.x % self.scaled_tile_size
                rem_y = self.y % self.scaled_tile_size

                canvas_x = i * self.scaled_tile_size + rem_x
                canvas_y = j * self.scaled_tile_size + rem_y

                # if self.display_grid: outline = "black"
                # else: outline = ""

                if not tile is None:
                    img = tile["scaled"]
                    self.create_image(
                        canvas_x, canvas_y, anchor=tk.NW, image=img
                    )
                # else:
                #     self.create_rectangle(
                #         canvas_x, canvas_y,
                #         canvas_x + self.tile_size,
                #         canvas_y + self.tile_size,
                #         fill="lightblue",
                #         outline=outline
                #     )


    def draw_grid(self):
        for i in range(self.winfo_width() // self.scaled_tile_size + 1):
            self.create_line(
                i * self.scaled_tile_size + (self.x % self.scaled_tile_size),
                0,
                i * self.scaled_tile_size + (self.x % self.scaled_tile_size),
                self.winfo_height(),
                fill="grey", width=1
            )

        for i in range(self.winfo_height() // self.scaled_tile_size + 1):
            self.create_line(
                0, 
                i * self.scaled_tile_size + (self.y % self.scaled_tile_size),
                self.winfo_width(),
                i * self.scaled_tile_size + (self.y % self.scaled_tile_size),
                fill="grey", width=1
            )


    def draw_ruler(self):
        if self.scaled_tile_size < 24: return
        ruler_width = 18

        self.create_rectangle(
            0, 0, self.winfo_width(),
            ruler_width, fill="white"
        )
        self.create_rectangle(
            self.winfo_width() - ruler_width, 0,
            self.winfo_width(), self.winfo_height(), fill="white"
        )

        for i in range(self.winfo_width() // self.scaled_tile_size + 1):
            x = i * self.scaled_tile_size + (self.x % self.scaled_tile_size)
            y = 0

            self.create_line(x, y, x, y + ruler_width, fill="grey", width=1)

            self.create_text(
                x - self.scaled_tile_size / 2,
                y + ruler_width / 2,
                text=i - self.x // self.scaled_tile_size - 1
            )

        for i in range(self.winfo_height() // self.scaled_tile_size + 2):
            x = self.winfo_width() - ruler_width
            y = i * self.scaled_tile_size + (self.y % self.scaled_tile_size)
            self.create_line(x, y, x + ruler_width, y, fill="grey", width=1)

            self.create_text(
                x + ruler_width / 2,
                y - self.scaled_tile_size / 2,
                text=i - self.y // self.scaled_tile_size - 1, angle=-90
            )

        self.create_rectangle(
            self.winfo_width() - ruler_width, 0,
            self.winfo_width(), ruler_width, fill="white"
        )