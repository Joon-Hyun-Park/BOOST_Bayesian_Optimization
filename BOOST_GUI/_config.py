# _config.py
import json
import os
from tkinter import filedialog, messagebox

class ConfigManager:
    """설정 저장/로드를 담당하는 클래스"""

    def __init__(self):
        pass

    @staticmethod
    def save_config(config):
        filename = filedialog.asksaveasfilename(
            title="Save Parameter Setup",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All Files", "*")],  # ← "*" 로
            initialdir=os.path.expanduser("~"),  # (선택) 사용자 홈에서 시작
        )
        if not filename:
            return False  # 사용자가 취소한 경우

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
                ("All Files", "*"),   # ← "*.*" 말고 "*" 사용
            ],
            initialdir=os.path.expanduser("~"),  # (선택)
        )
        if not filename:
            return None
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading the file:\n{e}")
            return None
