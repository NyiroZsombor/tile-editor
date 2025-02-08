import os
import json
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msg
import tkinter.filedialog as fd
from ttkthemes import ThemedStyle
from editor import Editor
from tile_map import TileMap
from preferences import Preferences

class App(tk.Tk):

    def __init__(self, width_tile=16, height_tile=16, tile_size=48):
        super().__init__()

        self.settings = self.open_json_file(
            "settings", self.create_settings_json)
        self.keybinds = self.open_json_file(
            "keybinds", self.create_keybinds_json)

        self.call("tk", "scaling", 2.0)

        style = ThemedStyle(self)
        self.op_sys = self.tk.call("tk", "windowingsystem")

        if "plastik" in style.theme_names():
            style.set_theme("plastik")
        else:
            print("unable to set theme")

        style.configure("Treeview", rowheight=24)
        
        self.title("Tile Editor")

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
 
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        if self.op_sys == "x11":
            self.attributes("-zoomed", True)
        else:
            self.state("zoomed")
        self.minsize(1280, 720)

        self.preferences = None
        self.editor = Editor(self, width_tile, height_tile, tile_size)
        self.editor.grid(column=0, row=0, sticky="nesw")

        self.is_saved = False
        self.file_name = ""
        self.menubar = self.menubar_setup()
        self.update()
        self.editor.create_tile_group_grid()
        self.editor.selected_group = "Default"
        self.editor.tile_group_grids["Default"].pack()

        self.keybinds_setup()

        self.editor.show_warnings()
        if self.settings["startup_open"]:
            self.open_file()
        self.main_loop()


    def open_json_file(self, filename, fallback_function):
        try:
            with open(filename + ".json", "r") as file:
                json_file = json.load(file)
        except FileNotFoundError:
            json_file = fallback_function()

        return json_file


    def menubar_setup(self):
        
        self.option_add("*tearOff", tk.FALSE)

        menubar = tk.Menu(self)
        self["menu"] = menubar

        file_menu = tk.Menu(menubar)
        menubar.add_cascade(menu=file_menu, label="File")

        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save as...", command=self.save_file_as)
        file_menu.add_command(label="Open...", command=self.open_file)

        edit_menu = tk.Menu(menubar)
        menubar.add_cascade(menu=edit_menu, label="Edit")

        edit_menu.add_command(label="Clear All", command=self.clear_all)        
        edit_menu.add_command(label="Preferences", command=self.open_preferences)   

        return menubar
    

    def open_preferences(self):
        if self.preferences is not None:
            self.preferences.destroy()

        self.preferences = Preferences()
    

    def clear_all(self):
        if msg.askquestion("Clear All Tiles", "Are you sure?") != "yes":
            return
        tm = self.editor.canvas.tile_map
        w = tm.width
        h = tm.height
        self.editor.canvas.tile_map = TileMap(w, h, tm.tile_size)

    
    def new_file(self):
        def change_entry(entry, amount):
            val = entry.get()
            if not val.isdigit(): return
            num = int(val) + amount
            if num < 1: return
            entry.delete(0, tk.END)
            entry.insert(0, str(num))

        def confirm_entry(entry):
            val = entry.get()
            i = 0
            while not val.isdigit():
                if val[i].isdigit():
                    i += 1
                    continue

                val = val.replace(val[i], "", 1)
                
            entry.delete(0, tk.END)
            entry.insert(0, val)

        def create_setting(name, step):
            def get_value():
                confirm_entry(frame.entry)
                return int(frame.entry.get())

            frame = tk.Frame(win)

            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(2, weight=1)
            frame.columnconfigure(3, weight=1)

            frame.rowconfigure(0, weight=1)

            frame.label = tk.Label(frame, text=name, anchor=tk.W)
            frame.entry = tk.Entry(frame)
            frame.entry.insert(0, str(step * 4))

            frame.minus_button = tk.Button(
                frame, text=f"- {step}",
                command=lambda: change_entry(frame.entry, -step)
            )
            frame.plus_button = tk.Button(
                frame, text=f"+ {step}",
                command=lambda: change_entry(frame.entry, +step)
            )

            frame.entry.bind("<Return>", lambda _: confirm_entry(frame.entry))

            frame.label.grid(column=0, row=0, sticky="nsew")
            frame.minus_button.grid(column=1, row=0, sticky="nsew")
            frame.entry.grid(column=2, row=0, sticky="nsew")
            frame.plus_button.grid(column=3, row=0, sticky="nsew")

            frame.get_value = get_value
            frame.pack(pady=8)

            return frame

        def new_editor():
            w = width_frame.get_value()
            h = height_frame.get_value()
            t = tile_size_frame.get_value()
            self.new_editor(w, h, t).mainloop()

        win = tk.Toplevel()
        sw = 500
        sh = 350
        win.geometry(
            f"{sw}x{sh}" +
            f"+{self.screen_width // 2 - sw // 2}" +
            f"+{self.screen_height // 2 - sh // 2}"
        )

        win.resizable(False, False)
        win.title("New File")

        width_frame = create_setting("Width (tiles): ", 8)
        height_frame = create_setting("Height (tiles): ", 8)
        tile_size_frame = create_setting("Tile Size (px): ", 8)

        create_button = tk.Button(
            win, text="Create", command=new_editor
        )
        cancel_button = tk.Button(
            win, text="Cancel", command=win.destroy
        )

        create_button.pack(
            side=tk.RIGHT, padx=24, pady=48,
            anchor=tk.N, expand=True, fill=tk.X
        )
        cancel_button.pack(
            side=tk.LEFT, padx=24, pady=48,
            anchor=tk.N, expand=True, fill=tk.X
        )


    def new_editor(self, width, height, tile_size):
        self.after_cancel(self.after_id)
        self.destroy()
        return App(width, height, tile_size)


    def save_file(self):
        self.is_saved = True
        if not self.file_name: return self.save_file_as()

        self.editor.canvas.tile_map.save_json(self.file_name)


    def save_file_as(self):
        self.is_saved = True
        filetypes = (("JSON file", "*.json"), ("PNG image", "*.png"))
        file_name = fd.asksaveasfilename(
            defaultextension=".json", filetypes=filetypes
        )
        if not file_name: return
        self.file_name = file_name
        ext = os.path.splitext(self.file_name)[1]

        if ext == ".json":
            self.editor.canvas.tile_map.save_json(self.file_name)
        elif ext == ".png":
            self.editor.canvas.tile_map.save_image(
                self.file_name,
                self.editor.group_images
            )
        else: print("invalid filetype", ext)


    def open_file(self):
        filename = fd.askopenfilename(
            title="Open File", 
            filetypes=(("JSON file", "*.json"), ("Binary file", "*.bin"))
        )

        if filename:
            ext = os.path.splitext(filename)[-1]

            if ext == ".json":
                with open(filename, "r") as file:
                    tile_map = json.load(file)
                
                new_app = self.new_editor(
                    tile_map["width"], 
                    tile_map["height"],
                    tile_map["tile_size"]
                )
                new_app.editor.canvas.tile_map.load_json(tile_map["tiles"])


    def create_settings_json(self):
        default_settings = {
            "startup_warnings": 1,
            "startup_open": 0,
            "background_color": "AADDEE",
            "file_manager_path": os.getcwd(),
            "tiles_path": os.path.join(os.getcwd(), "tiles")
        }
        with open("settings.json", "x") as file:
            json.dump(default_settings, file, indent=4)

        return default_settings
    

    def create_keybinds_json(self):
        default_keybinds = {
            "Control-d": "clear-all",
            "Control-p": "open-preferences",
            "Control-n": "new-file",
            "Control-s": "save-file",
            "Control-o": "open-file"
        }

        with open("keybinds.json", "x") as file:
            json.dump(default_keybinds, file, indent=4)

        return default_keybinds


    def keybinds_setup(self):
        def get_func(function_name):
            match function_name:
                case "clear-all": return self.clear_all
                case "open-preferences": return self.open_preferences
                case "new-file": return self.new_file
                case "save-file": return self.save_file
                case "open-file": return self.open_file
        
        for bind in self.keybinds.keys():
            func = get_func(self.keybinds[bind])
            self.bind("<" + bind + ">", lambda _, func=func: func())


    def main_loop(self):
        self.update()
        self.editor.canvas.draw()
        self.after_id = self.after(1000 // 60, self.main_loop)


if __name__ == "__main__":
    App().mainloop()

