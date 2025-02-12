import os
import tkinter as tk
import tkinter.filedialog as fd
from PIL import Image, ImageTk

class TileGroups(tk.Frame):

    def __init__(self, master, tile_size, **kwargs):
        super().__init__(master, **kwargs)

        self.config_grid = True
        self.tile_size = tile_size
        self.selected_group: str | None = None
        self.selected_tile: dict | None = None
        self.group_grids: dict[str, tk.Frame] = {}
        self.groups: dict[str, list] = {}
        self.group_sizes: dict[str, tuple[int, int]] = {}
        self.tile_set_images: dict[str, Image.Image] = {}
        self.exception_occured = False
        self.transparency_warning = False

        self.grid(column=1, row=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)

        # self.tile_groups = {}
        # self.create_tile_group_images()

        self.top_frame = self.top_frame_setup()
        self.bottom_frame  = tk.Frame(self)
        self.bottom_frame.grid(column=0, row=1, sticky="nsew")
        self.create_tile_group_list()


    def top_frame_setup(self):
        def on_press():
            file_name = fd.askopenfilename(defaultextension=".png")

            if file_name == "": return
            name, ext = os.path.splitext(os.path.split(file_name)[1])
            if ext != ".png": return

            self.load_image(file_name, name)
            self.create_tile_group_grid(name)
            self.add_tile_group_list_entry(name)
            
        
        top_frame = tk.Frame(self)
        top_frame.grid(column=0, row=0, sticky="nsew")

        label = tk.Label(
            top_frame, text="Tile Groups", pady=2,
            anchor=tk.W, font=("Helvetica", 11, "bold")
        )
        label.pack(side=tk.TOP, fill=tk.X)

        btn = tk.Button(
            top_frame, text="+ Add Tile Group", pady=2,
            anchor=tk.W, command=on_press
        )
        btn.pack(side=tk.TOP, fill=tk.X)

        return top_frame


    def load_images(self, path):
        img_paths = os.listdir(path)

        for img_path in img_paths:
            name = os.path.splitext(os.path.split(img_path)[1])[0]
            self.load_image(os.path.join(path, img_path), name)


    def load_image(self, path, name):
        img = Image.open(path)
        self.tile_set_images[name] = img
        tile_width = img.size[0] // self.tile_size
        tile_height = img.size[1] // self.tile_size
        tiles = []

        for i in range(tile_height):
            for j in range(tile_width):
                x = j * self.tile_size
                y = i * self.tile_size
                box = (x, y, x + self.tile_size, y + self.tile_size)
                tile_img = img.crop(box)

                try:
                    tile_img = self.check_image(tile_img)
                    if tile_img is None: continue

                    icon = tile_img.resize((48, 48))

                    scaled = ImageTk.PhotoImage(tile_img.resize((
                        self.master.canvas.scaled_tile_size,
                        self.master.canvas.scaled_tile_size,
                    ), Image.Resampling.NEAREST))
                    
                    tiles.append({
                        "icon": ImageTk.PhotoImage(icon),
                        "scaled": scaled,
                        "image": tile_img,
                        "id": name + "_" + str(len(tiles))
                    })

                except Exception as e:
                    self.exception_occured = True
                    print(e)

        self.groups[name] = tiles
        self.group_sizes[name] = (tile_width, tile_height)


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


    def create_tile_group_grids(self, groups: list[str]=None):
        groups = groups or self.groups.keys()
        for group in groups:
            self.create_tile_group_grid(group)


    def create_tile_group_grid(self, group: str):
        def clicked(event):
            self.selected_tile = event.widget.tile
        
        pad = 2

        frame = tk.Frame(self.bottom_frame)
        frame.grid_propagate(False)

        current_group = self.groups[group]

        for i in range(len(current_group)):
            tile = current_group[i]
            if (i + i // self.group_sizes[group][0]) % 2 == 0:
                color = "darkgray"
            else:
                color = "lightgray"

            label = tk.Label(frame, image=tile["icon"], bg=color)
            label.grid(
                column=i % self.group_sizes[group][0],  padx=pad, pady=pad,
                row=i // self.group_sizes[group][0], sticky="nsew",
            )

            label.tile = tile
            label.bind("<Button-1>", clicked)

        self.group_grids[group] = frame


    def create_tile_group_list(self):
        def on_select(_):
            curselection = self.tile_group_list.curselection()
            if not curselection: return

            idx = curselection[0]
            self.select_group(self.tile_group_list.get(idx))


        self.tile_group_list = tk.Listbox(
            self.top_frame, selectmode=tk.BROWSE, justify=tk.CENTER
        )

        # for group in self.groups.keys():
        #     self.tile_group_list.insert(tk.END, group)
        # self.tile_group_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = tk.Scrollbar(
            self.tile_group_list, command=self.tile_group_list.yview,
            cursor="arrow", width=20
        )
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tile_group_list.configure(yscrollcommand=scroll.set)
        self.tile_group_list.bind("<<ListboxSelect>>", on_select)


    def add_tile_group_list_entry(self, group):
        self.tile_group_list.insert(tk.END, group)
        self.tile_group_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    def create_tile_group_lists(self):
        def on_select(event):
            # if self.selected_group is None: return
            curselection = self.tile_group_list.curselection()
            if not curselection: return

            idx = curselection[0]
            self.select_group(self.tile_group_list.get(idx))


        self.tile_group_list = tk.Listbox(
            self.top_frame, selectmode=tk.BROWSE, justify=tk.CENTER
        )

        for group in self.groups.keys():
            self.tile_group_list.insert(tk.END, group)
        self.tile_group_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = tk.Scrollbar(
            self.tile_group_list, command=self.tile_group_list.yview,
            cursor="arrow", width=20
        )
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tile_group_list.configure(yscrollcommand=scroll.set)
        self.tile_group_list.bind("<<ListboxSelect>>", on_select)


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