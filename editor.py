import tkinter as tk
from tkinter import ttk
import os
from canvas import Canvas
from evaluate import evaluate

class Editor(tk.Frame):
    src_path = "src"
    out_path = "out"
    assets_path = "assets"
    tiles_path = os.path.join(src_path, "tiles")

    def __init__(self, master, width_tile, height_tile, tile_size):
        super().__init__(master)

        self.width_tile = width_tile
        self.height_tile = height_tile
        self.tile_size = tile_size

        style = ttk.Style()
        # if self.master.tk.call("tk", "windowingsystem") == "x11":
        style.configure("Treeview", rowheight=24)
    
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=7)
        self.columnconfigure(2, weight=2)
        
        self.rowconfigure(0, weight=7)
        self.rowconfigure(1, weight=4)

        self.grid(sticky="nsew")

        self.image_setup()

        self.editor_selection_frame = self.editor_selection_frame_setup()
        self.main_editor_frame = self.main_editor_frame_setup()
        self.file_manager_frame = self.file_manager_frame_setup()
        self.terminal_frame = self.terminal_frame_setup()
        self.tile_group_frame = self.tile_group_frame_setup()


    def image_setup(self):
        self.images = {}
        for img_ext in os.listdir(self.assets_path):
            img_path = os.path.join(os.getcwd(), self.assets_path, img_ext)
            img_name = os.path.splitext(img_ext)[0]

            self.images[img_name] = tk.PhotoImage(file=img_path)


    def editor_selection_frame_setup(self):
        editor_selection_frame = tk.Frame(self, bg="white")
        editor_selection_frame.grid(column=2, row=1, sticky="nsew")

        label = tk.Label(
            editor_selection_frame, text="Editors", pady=2,
            anchor=tk.W, font=("Helvetica", 11, "bold")
        )
        label.pack(side=tk.TOP, fill=tk.X)

        items = tk.StringVar(value=(
            "Tile Editor", 
            "Collision Mask Editor"
        ))

        listbox = tk.Listbox(
            editor_selection_frame, listvariable=items,
            height=2, selectmode=tk.SINGLE, justify=tk.CENTER
        )
        listbox.pack(fill=tk.BOTH, expand=True)

        return editor_selection_frame


    def main_editor_frame_setup(self):
        def clicked(event):
            self.canvas.display_grid = not self.canvas.display_grid

            if self.canvas.display_grid:
                img = "grid_enabled"
            else:
                img = "grid_disabled"

            btn.configure(image=self.images[img])
            self.canvas.draw()
        
        main_editor = tk.Frame(self, bg="yellow")
        main_editor.grid(column=1, row=0, sticky="nsew")

        self.canvas = Canvas(
            main_editor, self.width_tile, self.height_tile,
            self.tile_size, width=100, height=100, bg="lightblue"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        btn = tk.Button(self.canvas, image=self.images["grid_enabled"])
        btn.pack(side=tk.BOTTOM, anchor=tk.W, padx=4, pady=4)
        btn.bind("<Button-1>", clicked)

        return main_editor


    def file_manager_frame_setup(self):
        def insert_items(iid="", path=os.getcwd()):
            for file in os.listdir(path):
                is_dir = os.path.isdir(os.path.join(path, file))

                if is_dir: idx = 0
                else: idx = tk.END
                next_iid = tree.insert(iid, idx, text=file)

                if is_dir:
                    insert_items(next_iid, os.path.join(path, file))
                    

        file_manager_frame = tk.Frame(self, bg="red")
        file_manager_frame.grid(column=0, row=0, rowspan=2, sticky="nsew")

        tree = ttk.Treeview(file_manager_frame)
        tree.heading("#0", text="File Manager")
        insert_items()
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = tk.Scrollbar(
            file_manager_frame, command=tree.yview,
            cursor="arrow", width=20
        )

        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.config(yscrollcommand=scroll.set)

        return file_manager_frame


    def terminal_frame_setup(self):
        terminal_frame = tk.Frame(self, bg="darkgrey")
        terminal_frame.grid(column=1, row=1, sticky="nsew")

        label = tk.Label(
            terminal_frame, text="Terminal", pady=2,
            anchor=tk.W, font=("Helvetica", 11, "bold")
        )
        label.pack(side=tk.TOP, fill=tk.X)

        self.terminal = tk.Text(terminal_frame)
        self.terminal.bindtags(
            (str(self.terminal), str(terminal_frame), tk.ALL)
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)

        self.command_entry = tk.Entry(terminal_frame)
        self.command_entry.pack(fill=tk.X, padx=2, pady=4)

        scroll = tk.Scrollbar(
            self.terminal, command=self.terminal.yview,
            cursor="arrow", width=20
        )
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal.config(yscrollcommand=scroll.set)

        self.command_history = []
        self.command_idx = 0

        self.command_entry.bind("<KeyPress>", lambda e: evaluate(
            e, self
        ))

        return terminal_frame


    def tile_group_frame_setup(self):
        tile_group_frame = tk.Frame(self, bg="blue")
        tile_group_frame.grid(column=2, row=0, sticky="nsew")
        # tile_group_frame.maxsize(600, -1)
        tile_group_frame.columnconfigure(0, weight=1)
        tile_group_frame.rowconfigure(0, weight=1)
        tile_group_frame.rowconfigure(1, weight=2)

        self.tile_groups = {}
        self.create_tile_groups()

        # self.tile_group_tree = ttk.Treeview(tile_group_frame)
        # self.tile_group_tree.heading("#0", text="Tile Groups")
        # self.create_tile_group_tree()
    
        top_frame = tk.Frame(tile_group_frame)
        top_frame.grid(column=0, row=0, sticky="nsew")

        self.tile_group_list = tk.Listbox(
            top_frame, selectmode=tk.BROWSE, justify=tk.CENTER
        )
        for group in self.tile_groups.keys():
            self.tile_group_list.insert(tk.END, group)

        self.tile_group_list.pack(
            fill=tk.BOTH, expand=True
        )

        self.bottom_frame = tk.Frame(tile_group_frame)

        self.tile_group_grids = {}
        #self.create_tile_group_grid(bottom_frame)
        self.bottom_frame.grid(column=0, row=1, sticky="nsew")
        #self.tile_group_grids["Paths"].pack()

        # self.tile_group_tree.pack(fill=tk.BOTH, expand=True)


    def create_tile_groups(self):
        groups = os.listdir(self.tiles_path)

        for group in groups:
            items = os.listdir(os.path.join(self.tiles_path, group))
            tile_group = []

            for item in items:
                if not os.path.isdir(os.path.join(self.tiles_path, item)):
                    tile_group.append(item)

            self.tile_groups[group] = tile_group


    def create_tile_group_tree(self):
        for group, items in self.tile_groups.items():
            current_group = self.tile_group_tree.insert("", 0, text=group)

            for item in items:
                self.tile_group_tree.insert(
                    current_group, 0, text=item, image=self.images["img"]
                )

    
    def create_tile_group_grid(self):
        width = self.bottom_frame.winfo_width()
        tile_width = width // self.tile_size

        for i in range(tile_width):
            self.bottom_frame.columnconfigure(i, minsize=self.tile_size)

        for group in self.tile_groups:
            frame = tk.Frame(self.bottom_frame)
            i = 0

            for tile in self.tile_groups[group]:
                label = tk.Label(
                    frame, image=self.images["img"], text=tile,
                    bg="red" if (i + i // tile_width) % 2 == 0 else "blue"
                )
                label.grid(column=i % tile_width, row=i // tile_width, sticky="nsew")
                i += 1

            self.tile_group_grids[group] = frame


    def get_selected_tile(self):
        return "whatever"