import tkinter as tk
from tkinter import ttk

from editor import Editor
# from collision_mask_editor import CollisionMaskEditor

class App(tk.Tk):
    TILE_EDITOR = 0
    COLLISION_MASKS_EDITOR = 1

    def __init__(self):
        super().__init__()
        
        self.modes = ["tile editor", "collision mask editor"]
        self.current_mode = self.TILE_EDITOR
        
        self.title("Tile editor")
 
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.minsize(1280, 720)

        self.editor = Editor(self)
        self.editor.grid(column=0, row=0, sticky="nesw")

        self.menubar = self.menubar_setup()

        self.main_loop()


    def menubar_setup(self):
        self.option_add("*tearOff", tk.FALSE)

        menubar = tk.Menu(self)
        self["menu"] = menubar

        file_menu = tk.Menu(menubar)
        edit_menu = tk.Menu(menubar)
        menubar.add_cascade(menu=file_menu, label="File")
        menubar.add_cascade(menu=edit_menu, label="Edit")

        file_menu.add_command(label="New")
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Save as...")

        return menubar
    

    def main_loop(self):
        self.update()
        self.editor.canvas.draw()
        self.after(1000 // 60, self.main_loop)


if __name__ == "__main__":
    App().mainloop()

