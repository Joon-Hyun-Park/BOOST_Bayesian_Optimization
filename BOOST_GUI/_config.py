# _config.py
import json
import os
from tkinter import filedialog, messagebox

class ConfigManager:
    """Class responsible for saving/loading configurations"""

    def __init__(self):
        pass

    @staticmethod
    def save_config(config):
        filename = filedialog.asksaveasfilename(
            title="Save Parameter Setup",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All Files", "*")],  # use '*' for all files
            initialdir=os.path.expanduser("~"),  # (optional) start in user's home directory
        )
        if not filename:
            return False  # user cancelled

        try:
            with open(filename, 'w', encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the file:\n{e}")
            return False

    @staticmethod
    def load_config():
        filename = filedialog.askopenfilename(
            title="Load Parameter Setup",
            filetypes=[
                ("JSON files", "*.json"),
                ("All Files", "*"),   # use '*' instead of '*.*'
            ],
            initialdir=os.path.expanduser("~"),  # (optional)
        )
        if not filename:
            return None
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading the file:\n{e}")
            return None
