import tkinter as tk
from io import StringIO
import sys

def evaluate(event, editor):
    if event.keysym == "Return":
        command = editor.command_entry.get().strip()
        editor.command_entry.delete(0, tk.END)
        editor.terminal.insert(tk.END, command + "\n")
        editor.command_history.append(command)
        editor.command_idx = len(editor.command_history)
        
        if command.startswith("py "):
            stdout = sys.stdout
            result = StringIO()
            sys.stdout = result

            command = command.removeprefix("py ")

            try:
                ret = eval(command)
                if not ret is None:
                    print(ret)
            except Exception as e:
                print(e)

            sys.stdout = stdout
            val = result.getvalue().strip("\n")

            if val:
                for v in val.split("\n"):
                    editor.terminal.insert(tk.END, "> " + v + "\n")
            
        else:
            if command == "clear":
                editor.terminal.delete("1.0", tk.END)

        editor.terminal.see(tk.END)

    elif event.keysym in ["Up", "Down"]:
        if len(editor.command_history) == 0:
            return
        
        if event.keysym == "Up":
            editor.command_idx -= 1
        else:
            editor.command_idx += 1

        if editor.command_idx >= len(editor.command_history):
            editor.command_idx = len(editor.command_history) - 1
            editor.command_entry.delete(0, tk.END)
            return
        elif editor.command_idx < 0:
            editor.command_idx = 0

        editor.command_entry.delete(0, tk.END)
        editor.command_entry.insert(
            0, editor.command_history[editor.command_idx]
        )