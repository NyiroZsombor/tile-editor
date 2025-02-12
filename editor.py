import tkinter as tk
import os
from tkinter import ttk
from tkinter import messagebox as msg
from tile_groups import TileGroups
from canvas import Canvas

class Editor(tk.Frame):
    src_path = "src"
    out_path = "out"
    assets_path = "assets"
    file_manager_path = os.getcwd()

    def __init__(self, master, width_tile, height_tile, tile_size):
        super().__init__(master)

        self.width_tile = width_tile
        self.height_tile = height_tile
        self.tile_size = tile_size
        self.selected_tile = None
        self.tiles_path = self.master.settings["tiles_path"]

        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=3)
        
        self.rowconfigure(0, weight=1)

        self.grid(sticky="nsew")

        self.icons_setup()

        # self.editor_selection_frame = self.editor_selection_frame_setup()
        self.main_editor_frame = self.main_editor_frame_setup()
        self.tile_groups = TileGroups(self, self.tile_size, bg="blue")


    def icons_setup(self):
        self.icons = {}
        for icon_ext in os.listdir(self.assets_path):
            icon_path = os.path.join(os.getcwd(), self.assets_path, icon_ext)
            icon_name = os.path.splitext(icon_ext)[0]

            self.icons[icon_name] = tk.PhotoImage(file=icon_path)


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
        def grid_btn_clicked():
            self.canvas.display_grid = not self.canvas.display_grid

            if self.canvas.display_grid:
                img = "grid_enabled"
            else:
                img = "grid_disabled"

            grid_btn.configure(image=self.icons[img])

        def ruler_btn_clicked():
            self.canvas.display_ruler = not self.canvas.display_ruler

            if self.canvas.display_ruler:
                img = "ruler_enabled"
            else:
                img = "ruler_disabled"

            ruler_btn.configure(image=self.icons[img])

        def zoom_in_btn_clicked():
            self.canvas.change_zoom(2)

        def zoom_out_btn_clicked():
            self.canvas.change_zoom(0.5)
        
        main_editor = tk.Frame(self, bg="yellow")
        main_editor.grid(
            column=0, row=0, sticky="nsew"
        )

        # canvas
        self.canvas = Canvas(
            main_editor, self.width_tile, self.height_tile,
            self.tile_size, width=100, height=100, bg="lightblue"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        icons_frame = tk.Frame(
            self.canvas, highlightbackground="darkgray",
            highlightthickness=4, padx=4
        )

        icons_pack = {"side": tk.LEFT, "anchor": tk.S, "padx": 4, "pady": 16}

        # grid
        grid_btn = tk.Button(
            icons_frame, image=self.icons["grid_enabled"],
            command=grid_btn_clicked
        )
        grid_btn.pack(**icons_pack)

        # ruler
        ruler_btn = tk.Button(
            icons_frame, image=self.icons["ruler_enabled"],
            command=ruler_btn_clicked
        )
        ruler_btn.pack(**icons_pack)

        # zoom in
        zoom_in_btn = tk.Button(
            icons_frame, image=self.icons["zoom_in"],
            command=zoom_in_btn_clicked
        )
        zoom_in_btn.pack(**icons_pack)

        # zoom out
        zoom_out_btn = tk.Button(
            icons_frame, image=self.icons["zoom_out"],
            command=zoom_out_btn_clicked
        )
        zoom_out_btn.pack(**icons_pack)

        icons_frame.pack(side=tk.LEFT, anchor=tk.S, padx=16, pady=16)

        return main_editor


    def show_warnings(self):
        if not self.master.settings["startup_warnings"]: return

        if self.tile_groups.exception_occured:
            self.tile_groups.exception_occured = False
            msg.showwarning(
                "Exception while loading resources!",
                "Warning! An exception has occured while loading images."
            )
        
        if self.tile_groups.transparency_warning:
            self.tile_groups.transparency_warning = False
            msg.showwarning(
                "Images with partial transparency detected!",
                "Warning! The editor is not meant to be used with images " +
                "with partial transparency. You may experience lag."
            )
        