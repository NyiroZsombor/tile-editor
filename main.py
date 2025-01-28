import tkinter as tk
from tkinter import ttk

from editor import Editor
# from collision_mask_editor import CollisionMaskEditor

class App(tk.Tk):
    TILE_EDITOR = 0
    COLLISION_MASKS_EDITOR = 1

    # TODO: , width, height, tile_size vvv
    def __init__(self):
        super().__init__()
        
        self.modes = ["tile editor", "collision mask editor"]
        self.current_mode = self.TILE_EDITOR

        self.call("tk", "scaling", 2.0)
        
        self.title("Tile Editor")

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
 
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        sw = 1280
        sh = 720
        self.geometry(
            f"{sw}x{sh}" +
            f"+{self.screen_width // 2 - sw // 2}" +
            f"+{self.screen_height // 2 - sh // 2}"
        )
        self.minsize(1280, 720)

        self.editor = Editor(self)
        self.editor.grid(column=0, row=0, sticky="nesw")

        self.menubar = self.menubar_setup()
        self.update()
        self.editor.create_tile_group_grid()
        self.editor.tile_group_grids["Paths"].pack()

        self.main_loop()


    def menubar_setup(self):
        self.option_add("*tearOff", tk.FALSE)

        menubar = tk.Menu(self)
        self["menu"] = menubar

        file_menu = tk.Menu(menubar)
        edit_menu = tk.Menu(menubar)
        menubar.add_cascade(menu=file_menu, label="File")
        menubar.add_cascade(menu=edit_menu, label="Edit")

        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Save as...")

        return menubar
    

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

        def create_setting(name, step=10):
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

            frame.pack(pady=8)

            return frame
        
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

        create_setting("Width (tiles): ")
        create_setting("Height (tiles): ")
        create_setting("Tile Size (px): ", 8)

        def f():
            self.destroy()
            App().mainloop()

        create_button = tk.Button(
            win, text="Create", command=lambda: f
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
    

    def main_loop(self):
        self.update()
        self.editor.canvas.draw()
        self.after(1000 // 60, self.main_loop)


if __name__ == "__main__":
    App().mainloop()

