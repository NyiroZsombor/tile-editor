import os
import tkinter as tk
from PIL import Image, ImageTk

class TileGroups(tk.Frame):

    def __init__(self, master, tile_size, **kwargs):
        super().__init__(master, **kwargs)

        self.config_grid = True
        self.tile_size = tile_size
        self.selected_group: str | None = None
        self.selected_tile: dict | None = None
        self.bottom_frame_sizes: dict[str, tuple] = {}
        self.group_grids: dict[str, tk.Frame] = {}
        self.groups: dict[str, list] = {}
        self.exception_occured = False
        self.transparency_warning = False

        self.grid(column=2, row=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)

        # self.tile_groups = {}
        # self.create_tile_group_images()

        self.top_frame = self.top_frame_setup()
        self.bottom_frame = tk.Frame(self)

        self.bottom_frame.grid(column=0, row=1, sticky="nsew")


    def top_frame_setup(self):
        top_frame = tk.Frame(self)
        top_frame.grid(column=0, row=0, sticky="nsew")

        label = tk.Label(
            top_frame, text="Tile Groups", pady=2,
            anchor=tk.W, font=("Helvetica", 11, "bold")
        )
        label.pack(side=tk.TOP, fill=tk.X)

        return top_frame


    def load_image(self, path, name):
        img = Image.open(path)
        tiles = []

        for i in range(img.size[1] // self.tile_size):
            for j in range(img.size[0] // self.tile_size):
                x = j * self.tile_size
                y = i * self.tile_size
                box = (x, y, x + self.tile_size, y + self.tile_size)
                tile_img = img.crop(box)

                try:
                    tile_img = self.check_image(tile_img)
                    if tile_img is None: continue

                    icon = tile_img.resize((48, 48))
                    
                    tiles.append({
                        "icon": ImageTk.PhotoImage(icon),
                        "scaled": ImageTk.PhotoImage(tile_img),
                        "image": tile_img
                    })

                except Exception as e:
                    self.exception_occured = True
                    print(e)

        self.groups[name] = tiles


    def load_folders(self, path):
        groups = os.listdir(path)
        groups.sort()

        for group in groups:
            items = os.listdir(os.path.join(path, group))
            self.groups[group] = []

            for item in items:
                if os.path.isdir(os.path.join(path, item)): continue

                try:
                    image = Image.open(os.path.join(path, group, item))
                    self.try_adding_image(image, group)
                except Image.UnidentifiedImageError:
                    print("failed to open image")
                except IsADirectoryError:
                    print("failed to open image")


    def check_image(self, image: Image.Image):
        MIN = 0
        MAX = 1
        ALPHA = -1

        # print(image.getextrema())

        if image.mode == "RGBA":
            if image.getextrema()[ALPHA][MIN] < 255:
                self.transparency_warning = True
            if image.getextrema()[ALPHA][MAX] == 0:
                return None

        if (image.size[0] != self.tile_size
        or image.size[1] != self.tile_size):
            return None
        
        return image


    def try_adding_image(self, image, group):
        try:
            image = self.check_image(image)

            self.groups[group].append({
                "icon": ImageTk.PhotoImage(image),
                "scaled": ImageTk.PhotoImage(image),
                "image": image
            })

        except Exception as e:
            self.exception_occured = True
            print(e)

    # TODO tile groups is too wide
    def create_tile_group_grid(self, group: str):
        def clicked(event):
            self.selected_tile = event.widget.tile
        
        pad = 2
        width = self.bottom_frame.winfo_width()
        height = self.bottom_frame.winfo_height()
        tile_width = width // (self.tile_size + pad * 2)
        tile_height = int(height / (self.tile_size + pad * 2))

        self.bottom_frame_sizes[group] = (tile_width, tile_height)
        frame = tk.Frame(self.bottom_frame)
        frame.grid_propagate(False)

        current_group = self.groups[group]

        for i in range(len(current_group)):
            tile = current_group[i]

            label = tk.Label(
                frame, image=tile["icon"],
                bg="darkgray" if (i + i // tile_width) % 2 == 0 else "lightgray"
            )
            label.grid(
                column=i % tile_width, row=i // tile_width, sticky="nsew",
                padx=pad, pady=pad
            )

            label.tile = tile
            label.bind("<Button-1>", clicked)

        self.group_grids[group] = frame


    def create_tile_group_lists(self):
        def on_select(event):
            # if self.selected_group is None: return
            curselection = tile_group_list.curselection()
            if not curselection: return

            idx = curselection[0]
            self.select_group(tile_group_list.get(idx))


        tile_group_list = tk.Listbox(
            self.top_frame, selectmode=tk.BROWSE, justify=tk.CENTER
        )

        for group in self.groups.keys():
            tile_group_list.insert(tk.END, group)
        tile_group_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = tk.Scrollbar(
            tile_group_list, command=tile_group_list.yview,
            cursor="arrow", width=20
        )
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tile_group_list.configure(yscrollcommand=scroll.set)
        tile_group_list.bind("<<ListboxSelect>>", on_select)


    def select_group(self, group: str):
        if self.selected_group is not None:
            self.group_grids[self.selected_group].grid_forget()

        self.group_grids[group].grid_propagate(False)
        self.group_grids[group].grid(sticky="nsew", padx=0)
        self.selected_group = group
        
        self.config_grid = False
        self.bottom_frame.grid_columnconfigure(
            tk.ALL, minsize=self.tile_size, weight=1
        )

        self.bottom_frame.grid_rowconfigure(
            tk.ALL, minsize=self.tile_size, weight=1
        )