import tkinter as tk
import tkinter.filedialog as fd
import json

class Preferences(tk.Toplevel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.editor = self.master.editor
        self.title("Preferences")
        self.geometry("640x720")
        self.minsize(640, 640)

        color_picker_frame = self.colorpicker_frame_setup()
        startup_settings_frame = self.startup_settings_frame_setup()
        file_paths_frame = self.file_paths_frame_setup()


    def create_preference(self, title):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, side=tk.TOP)
        
        label = tk.Label(
            main_frame, text=title, pady=8, padx=16,
            bg="#AAA", anchor=tk.W
        )
        label.pack(fill=tk.X)

        frame = tk.Frame(main_frame, pady=8)
        frame.pack(fill=tk.X, side=tk.TOP)
        main_frame.frame = frame

        return main_frame


    def colorpicker_frame_setup(self):
        def set_color(event):
            bg = "#" + (
                hex(scales[0].get()).removeprefix("0x").zfill(2) +
                hex(scales[1].get()).removeprefix("0x").zfill(2) +
                hex(scales[2].get()).removeprefix("0x").zfill(2)
            )
            main_frame.frame.configure(bg=bg)
            self.editor.canvas.bg_color = bg
            self.master.settings["background_color"] = bg.removeprefix("#")

        def on_press():
            self.master.settings["background_color"] = (
                hex(scales[0].get()).removeprefix("0x").zfill(2) +
                hex(scales[1].get()).removeprefix("0x").zfill(2) +
                hex(scales[2].get()).removeprefix("0x").zfill(2)
            )

            with open("settings.json", "w") as file:
                json.dump(self.master.settings, file)

        main_frame = self.create_preference("Background Color")
        scale_configs = {
            "master": main_frame.frame, "tickinterval": 255, "to": 255,
            "orient": tk.HORIZONTAL, "showvalue": False, "length": 360
        }
        scales = (
            tk.Scale(**scale_configs, command=set_color),
            tk.Scale(**scale_configs, command=set_color),
            tk.Scale(**scale_configs, command=set_color)
        )

        with open("settings.json", "r") as file:
            settings = json.load(file)
        color = (  #ADE
            int(settings["background_color"][0:2], 16),
            int(settings["background_color"][2:4], 16),
            int(settings["background_color"][4:6], 16)
        )

        for i in range(3):
            scales[i].set(color[i])

        for i in range(3):
            scales[i].pack(fill=tk.X, padx=32, pady=4)

        btn = tk.Button(main_frame.frame, text="Save", command=on_press())
        btn.pack()

        return main_frame
    

    def startup_settings_frame_setup(self):
        def btn_switched(btn_state, setting):
            self.master.settings[setting] = btn_state.get()

            with open("settings.json", "w") as file:
                json.dump(self.master.settings, file)

        def create_btn(label, setting):
            btn_state = tk.IntVar()
            btn = tk.Checkbutton(
                main_frame.frame, text=label,
                variable=btn_state
            )

            with open("settings.json", "r") as file:
                settings = json.load(file)

            if settings[setting]:
                btn.select()

            btn.configure(command=lambda: btn_switched(btn_state, setting))
            btn.pack()

        main_frame = self.create_preference("Show Warnings on Startup")
        create_btn("Show Warnings on Startup", "startup_warnings")
        create_btn("Open New File on Startup", "startup_open")


    def file_paths_frame_setup(self):
        def on_click(label):
            directiory = fd.askdirectory(title="dir")
            if not directiory: return
            label.configure(text=label.label + directiory)

        main_frame = self.create_preference("File Paths")

        default_color = "#EEE"
        highlight_color = "#FFF"
        
        file_manager_label = tk.Label(
            main_frame.frame, bg=default_color, padx=4, pady=4, border=2
        )
        file_manager_label.pack(pady=4)
        file_manager_label.label = "File Manager: "
        file_manager_label.configure(text=(
            file_manager_label.label + self.master.settings["file_manager_path"]
        ))

        file_manager_label.bind(
            "<Button-1>", lambda _: on_click(file_manager_label)
        )
        file_manager_label.bind(
            "<Enter>", lambda _: file_manager_label.configure(bg=highlight_color)
        )
        file_manager_label.bind(
            "<Leave>", lambda _: file_manager_label.configure(bg=default_color)
        )

        tiles_label = tk.Label(
            main_frame.frame, text=self.master.settings["tiles_path"],
            bg=default_color, padx=4, pady=4, border=2
        )
        tiles_label.pack(pady=4)
        tiles_label.label = "Tiles: "
        tiles_label.configure(text=(
            tiles_label.label + self.master.settings["tiles_path"]
        ))

        tiles_label.bind(
            "<Button-1>", lambda _: on_click(tiles_label)
        )
        tiles_label.bind(
            "<Enter>", lambda _: tiles_label.configure(bg=highlight_color)
        )
        tiles_label.bind(
            "<Leave>", lambda _: tiles_label.configure(bg=default_color)
        )

        return main_frame