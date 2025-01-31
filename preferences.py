import tkinter as tk

class Preferences(tk.Toplevel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.editor = self.master.editor
        self.title("Preferences")
        self.geometry("640x720")
        self.minsize(480, 640)

        color_picker_frame = self.colorpicker_frame_setup()


    def create_preference(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, side=tk.TOP)
        
        label = tk.Label(
            main_frame, text="Background Color", pady=8, padx=16,
            bg="#AAA", anchor=tk.W
        )
        label.pack(fill=tk.X)

        frame = tk.Frame(main_frame)
        frame.pack(fill=tk.X, side=tk.TOP)
        main_frame.frame = frame

        return main_frame


    def colorpicker_frame_setup(self):
        def set_color(channel):
            bg = "#" + (
                hex(scales[0].get()).removeprefix("0x").zfill(2) +
                hex(scales[1].get()).removeprefix("0x").zfill(2) +
                hex(scales[2].get()).removeprefix("0x").zfill(2)
            )
            main_frame.frame.configure(bg=bg)
            self.editor.canvas.bg_color = bg

        def get_command(channel):
            return lambda _: set_color(channel)

        main_frame = self.create_preference()
        scale_configs = {
            "master": main_frame.frame, "tickinterval": 255, "to": 255,
            "orient": tk.HORIZONTAL, "showvalue": False, "length": 360
        }
        scales = (
            tk.Scale(**scale_configs, command=get_command(0)),
            tk.Scale(**scale_configs, command=get_command(1)),
            tk.Scale(**scale_configs, command=get_command(2))
        )

        for i in range(3):
            scales[i].set([170, 221, 238][i])

        for i in range(3):
            scales[i].pack(fill=tk.X, padx=32, pady=4)

        return main_frame