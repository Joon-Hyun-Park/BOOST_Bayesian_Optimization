import platform
import tkinter as tk
from tkinter import ttk

from _config import ConfigManager
from _data_tab import DataTab
from _parameter_tab import ParameterTab
from _result_tab import ResultTab


class BOMainApp:
    """Main Application Class"""

    def __init__(self, root):
        self.root = root
        self.root.title("BOOST GUI")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)

        # Style setup
        self.bg_color_1 = "#F3F3F3"
        self.bg_color_2 = "#ECEAE5"
        self.setup_styles()
        self.num_vars = 4


        self.button_font = ("Arial", 11)
        self.label_font = ("Arial", 11, "bold")

        # Initialize variables
        self.var_count_var = tk.IntVar(value=self.num_vars)

        # Create config manager
        self.config_manager = ConfigManager()

        # Create notebook widget
        self.notebook = ttk.Notebook(root, takefocus=False)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create each tab
        self.setup_tabs()

        # Load initial settings
        self.load_initial_config()
        self.scroll_num = 1 if platform.system() == "Darwin" else 120
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def setup_styles(self):
        """Style setup"""
        self.root.configure(bg=self.bg_color_1)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.bg_color_2)
        style.configure("TNotebook", background=self.bg_color_1)
        style.configure("TNotebook.Tab", background=self.bg_color_2)
        style.configure("TLabel", background=self.bg_color_2)
        style.configure("TButton", background=self.bg_color_2)

    def setup_tabs(self):
        """Create each tab"""
        self.param_tab = ParameterTab(self.notebook, self)
        self.data_tab = DataTab(self.notebook, self)
        self.result_tab = ResultTab(self.notebook, self)

    def load_initial_config(self):
        self.data_tab.update_data_info()

    def on_tab_changed(self, event):
        """Called when tab changes to clear initial focus of all tabs"""
        try:
            # Get the widget path of the currently selected tab frame.
            selected_frame_path = self.notebook.select()

            # If widget path is not empty, convert to actual widget object.
            if selected_frame_path:
                selected_frame = self.root.nametowidget(selected_frame_path)

                # Set focus to the frame to prevent auto-focusing on internal entry widgets.
                selected_frame.focus_set()
        except tk.TclError:
            # Exception handling for cases where widgets are not fully created at startup
            pass



if __name__ == "__main__":
    root = tk.Tk()
    app = BOMainApp(root)
    root.mainloop()