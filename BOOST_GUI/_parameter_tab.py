import tkinter as tk
from tkinter import ttk, messagebox


class ParameterTab:
    """Class responsible for the parameter setup tab"""

    def __init__(self, parent_notebook, main_app):
        self.main_app = main_app
        self.bg_color_2 = main_app.bg_color_2
        self.param_entries = []

        # Create tab frame
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="Parameter Setup")

        self.setup_ui()

    def setup_ui(self):

        # Configure row properties of self.frame
        # Row 0 (Table): Occupies remaining space when window expands (weight=1)
        self.frame.rowconfigure(0, weight=1)
        # Row 1 (Y variable setup): Ensures min height 40px, does not expand (weight=0)
        self.frame.rowconfigure(1, minsize=40)
        # Row 2 (Buttons): Ensures min height 50px, does not expand (weight=0)
        self.frame.rowconfigure(2, minsize=50)

        # Configure column properties of self.frame
        # Column 0: Occupies full window width (weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.setup_scrollable_table()  # X parameter input table
        self.setup_y_name_section()  # Y variable name, unit, objective function selection
        self.setup_buttons()  # Parameter buttons + Save, Load, Reset buttons
        self.create_param_table()  # Place actual Entry and Label widgets

    ##### self.setup_scrollable_table() # X parameter input table
    def setup_scrollable_table(self):
        self.table_outer = tk.Frame(self.frame, bg=self.bg_color_2)
        self.table_outer.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # ── grid layout ──
        self.table_outer.rowconfigure(0, weight=0)  # warning_label
        self.table_outer.rowconfigure(1, weight=1)  # canvas
        self.table_outer.rowconfigure(2, weight=0)  # hbar
        self.table_outer.columnconfigure(0, weight=1)
        self.table_outer.columnconfigure(1, weight=0, minsize=16)

        # ── warning_label ──
        self.warning_label = tk.Label(
            self.table_outer,
            text="",
            bg=self.bg_color_2,
            font=self.main_app.label_font,
            wraplength=500,
        )
        self.warning_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=3)

        # ── canvas/scrollbar ──
        self.param_canvas = tk.Canvas(self.table_outer, bg=self.bg_color_2, highlightthickness=0)
        self.param_vbar = ttk.Scrollbar(self.table_outer, orient="vertical", command=self.param_canvas.yview)
        self.param_hbar = ttk.Scrollbar(self.table_outer, orient="horizontal", command=self.param_canvas.xview)
        self.param_canvas.configure(xscrollcommand=self.param_hbar.set, yscrollcommand=self.param_vbar.set)

        self.param_canvas.grid(row=1, column=0, sticky="nsew")
        self.param_vbar.grid(row=1, column=1, sticky="ns")
        self.param_hbar.grid(row=2, column=0, sticky="ew")

        # Create internal frame
        self.table_frame = tk.Frame(self.param_canvas, bg=self.bg_color_2)
        self.table_id = self.param_canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        # Update warning_frame size when canvas size changes
        def _resize_warning(event):
            self.param_canvas.itemconfig(self.warning_id, width=event.width)

        self.param_canvas.bind("<Configure>", _resize_warning)

        # ── Toggle utils: Show/Hide + minsize adjustment + hbar columnspan management ──
        def _show_vbar(show: bool):
            # When showing: vbar grid, column1 minsize=16
            # When hiding: vbar grid_remove, column1 minsize=0
            self.table_outer.columnconfigure(1, minsize=16)
            if show:
                self.param_vbar.grid()
            else:
                self.param_vbar.grid_remove()

        def _show_hbar(show: bool):
            # When showing: row1 minsize=16, hbar grid
            # When hiding: row1 minsize=0, hbar grid_remove
            self.table_outer.rowconfigure(1, minsize=16)
            if show:
                self.param_hbar.grid()
            else:
                self.param_hbar.grid_remove()

        # ── Update scroll region/toggle ───────────────────────────────────────
        def update_scrollbars():
            region = self.param_canvas.bbox("all")  # (x1,y1,x2,y2) or None
            if not region:
                _show_vbar(False)
                _show_hbar(False)
                return
            content_w = region[2] - region[0]
            content_h = region[3] - region[1]
            # Currently visible area
            visible_w = self.param_canvas.winfo_width()
            visible_h = self.param_canvas.winfo_height()
            need_h = content_w > max(1, visible_w)
            need_v = content_h > max(1, visible_h)
            _show_hbar(need_h)
            _show_vbar(need_v)
            # Always keep scrollregion up to date
            self.param_canvas.configure(scrollregion=region)

        # Update whenever content/canvas size changes
        self.table_frame.bind("<Configure>", lambda e: update_scrollbars())
        self.param_canvas.bind("<Configure>", lambda e: update_scrollbars())

        # ── Mouse Wheel ─────────────────────────────────────────────────
        def _on_mousewheel(event):
            region = self.param_canvas.bbox("all")
            if region and (region[3] - region[1]) > self.param_canvas.winfo_height():
                self.param_canvas.yview_scroll(int(-1 * (event.delta / self.main_app.scroll_num)), "units")

        def _on_shift_mousewheel(event):
            region = self.param_canvas.bbox("all")
            if region and (region[2] - region[0]) > self.param_canvas.winfo_width():
                self.param_canvas.xview_scroll(int(-1 * (event.delta / self.main_app.scroll_num)), "units")

        self.param_canvas.bind("<Enter>", lambda e: self.param_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.param_canvas.bind("<Leave>", lambda e: self.param_canvas.unbind_all("<MouseWheel>"))
        self.param_canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)

        # Calculate once at the beginning
        self.table_outer.after(0, update_scrollbars)

    #######################################################################################################################

    #######################################################################################################################
    ##### self.setup_y_name_section() # Y variable name, unit, objective function selection
    def setup_y_name_section(self):
        y_section_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        y_section_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        tk.Label(y_section_frame, text="Target Variable Name:",
                 font=self.main_app.label_font, bg=self.bg_color_2).pack(side="left", padx=(20, 5))

        self.y_name_entry = tk.Entry(y_section_frame, width=15, justify="center")
        self.y_name_entry.pack(side="left", padx=5)
        self.y_name_entry.insert(0, "Y")

        # 🔽 Add unit input field
        tk.Label(y_section_frame, text="Unit:",
                 font=self.main_app.button_font, bg=self.bg_color_2).pack(side="left", padx=(10, 5))

        self.y_unit_entry = tk.Entry(y_section_frame, width=10, justify="center")
        self.y_unit_entry.pack(side="left", padx=5)
        self.y_unit_entry.insert(0, "")

        # Add Maximize/Minimize selection
        tk.Label(y_section_frame, text="Objective:",
                 font=self.main_app.label_font, bg=self.bg_color_2).pack(side="left", padx=(20, 5))

        self.objective_var = tk.StringVar(value="maximize")

        maximize_rb = tk.Radiobutton(y_section_frame, text="Maximize", variable=self.objective_var,
                                     value="maximize", bg=self.bg_color_2, font=self.main_app.button_font)
        maximize_rb.pack(side="left", padx=2)

        minimize_rb = tk.Radiobutton(y_section_frame, text="Minimize", variable=self.objective_var,
                                     value="minimize", bg=self.bg_color_2, font=self.main_app.button_font)
        minimize_rb.pack(side="left", padx=2)

        # Update when name or unit changes
        for entry in (self.y_name_entry, self.y_unit_entry):
            entry.bind('<KeyRelease>', self.on_y_name_change)  # When key is released
            entry.bind('<FocusOut>', self.on_y_name_change)  # e.g., when clicking a button immediately after pasting
        # Update when objective changes
        self.objective_var.trace('w', lambda *args: self.on_y_name_change())

    #######################################################################################################################

    #######################################################################################################################
    ##### self.setup_buttons() # Parameter buttons + Save, Load, Reset buttons
    def setup_buttons(self):
        button_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        button_frame.grid(row=2, column=0, sticky="", pady=10)

        # Changed to use grid() instead of pack()
        btn_col = 0

        # Buttons to add/remove parameter rows
        tk.Button(button_frame, text="Add Parameter", command=self.add_param_row, font=self.main_app.button_font).grid(
            row=0, column=btn_col, padx=5, pady=2)
        btn_col += 1

        tk.Button(button_frame, text="Remove Parameter", command=self.remove_param_row, font=self.main_app.button_font).grid(
            row=0, column=btn_col, padx=5, pady=2)
        btn_col += 1

        # Separator (optional)
        separator = tk.Frame(button_frame, width=2, height=20, bg='gray')
        separator.grid(row=0, column=btn_col, padx=10, pady=2)
        btn_col += 1

        # Settings Save/Load buttons
        tk.Button(button_frame, text="Save Setup", command=self.save_setup, font=self.main_app.button_font).grid(
            row=0, column=btn_col, padx=7, pady=2)
        btn_col += 1

        tk.Button(button_frame, text="Load Setup", command=self.load_setup, font=self.main_app.button_font).grid(
            row=0, column=btn_col, padx=7, pady=2)
        btn_col += 1

        # Separator
        separator2 = tk.Frame(button_frame, width=2, height=20, bg='gray')
        separator2.grid(row=0, column=btn_col, padx=10, pady=2)
        btn_col += 1

        # Reset button
        tk.Button(button_frame, text="    Reset    ", command=self.reset_params, font=self.main_app.button_font).grid(
            row=0, column=btn_col, padx=7, pady=2)

    def save_setup(self):
        try:
            config = self.get_param_config()  # Leave it to raise ValueError here
        except ValueError as e:
            messagebox.showerror("Invalid value", str(e))  # Prevent app crash + show original message
            return
        if self.main_app.config_manager.save_config(config):
            messagebox.showinfo("Saved", "Parameter setup saved successfully.")

    def load_setup(self):
        config = self.main_app.config_manager.load_config()
        if config:
            self.load_param_config(config)

    def reset_params(self):
        # Show confirmation message
        result = messagebox.askyesno(
            "Reset Confirmation",
            "Are you sure you want to reset all parameter settings?\n\nThis will:\n• Reset all parameter names, units, ranges\n• Reset target variable settings\n• Reset variable count to default\n\nThis action cannot be undone."
        )

        if not result:  # If user selected 'No' or closed the window
            return

        # Perform actual reset
        self.main_app.var_count_var.set(self.main_app.num_vars)
        self.y_name_entry.delete(0, tk.END)
        self.y_name_entry.insert(0, "Y")
        self.y_unit_entry.delete(0, tk.END)
        self.y_unit_entry.insert(0, "")
        self.objective_var.set("maximize")  # Reset objective function as well

        # Set default values for parameter name reset
        self.param_entries = []  # Important: Clear previous values
        self.create_param_table()

        self.main_app.data_tab.create_data_table()
        self.main_app.data_tab.update_data_info()
        self._scroll_to_top_left()

        # Success message
        messagebox.showinfo("Reset Complete", "All parameter settings have been reset to default values.")

    def _scroll_to_top_left(self):
        # Schedule to run immediately after layout/scroll region is applied
        def _do():
            if hasattr(self, "param_canvas") and self.param_canvas.winfo_exists():
                self.param_canvas.yview_moveto(0.0)
                self.param_canvas.xview_moveto(0.0)

        self.table_outer.after_idle(_do)  # or after(0, _do)

    #######################################################################################################################

    #######################################################################################################################
    ##### self.create_param_table()  # Place actual Entry and Label widgets
    def create_param_table(self):
        prev_values = [[e.get() for e in row] for row in self.param_entries]

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = ["Parameter", "Unit", "Min", "Max", "Step"]
        for j, header in enumerate(headers):
            tk.Label(self.table_frame, text=header, font=self.main_app.label_font,
                     bg=self.bg_color_2).grid(row=0, column=j + 1, padx=5, pady=5)

        self.param_entries = []
        num_vars = self.main_app.var_count_var.get()

        for i in range(num_vars):
            row_entries = []

            tk.Label(self.table_frame, text=f"X{i + 1}", font=self.main_app.label_font,
                     bg=self.bg_color_2).grid(row=i + 1, column=0, padx=5, pady=5)

            for j in range(5):
                entry = tk.Entry(self.table_frame, width=10, justify="center", font=self.main_app.button_font)
                entry.grid(row=i + 1, column=j + 1, padx=5, pady=5)

                if j in (0, 1):
                    entry.bind('<KeyRelease>', self.on_param_name_change)
                    entry.bind('<FocusOut>', self.on_param_name_change)

                if i < len(prev_values) and j < len(prev_values[i]):
                    entry.insert(0, prev_values[i][j])
                else:
                    defaults = ["x", "", "0", "1", "0.1"]
                    entry.insert(0, defaults[j] + str(i + 1) if j == 0 else defaults[j])

                row_entries.append(entry)

                if j in (2, 3, 4):  # Min, Max, Step columns
                    entry.bind('<KeyRelease>', self.update_warning_label)
                    entry.bind('<FocusOut>', self.update_warning_label)

            self.param_entries.append(row_entries)
            ################################################################################
            # Calculate candidate points and show warning
            try:
                param_config = self.get_param_config()
                param_info = param_config["parameters"]

                num_candidates = 1
                for param in param_info:
                    grid_size = int((param["max"] - param["min"]) / param["step"]) + 1
                    num_candidates *= grid_size
                dim = len(param_info)
                total_points = num_candidates * dim

                if total_points >= 1e7:
                    warning_text = (
                        f"⚠️ Strongly recommended: reduce grid size.\n"
                        f"(Current: {total_points:,} points)"
                    )
                    self.warning_label.config(text=warning_text, fg="red")
                elif total_points >= 1e6:
                    warning_text = f"⚠️ Large candidate size: {total_points:,}\n"
                    self.warning_label.config(text=warning_text, fg="orange")
                else:
                    warning_text = f"Estimated candidate size: {total_points:,}\n"
                    self.warning_label.config(text=warning_text, fg="green")

            except Exception:
                self.warning_label.config(text="", fg="red")

    #######################################################################################################################

    #######################################################################################################################
    ##### Parameter row add/remove function (Interaction with Data Tab)
    def add_param_row(self):
        """Add parameter row - Preserve existing data"""
        self.main_app.var_count_var.set(self.main_app.var_count_var.get() + 1)
        self.create_param_table()

        # Update Data Tab - Add column while preserving existing data
        self.main_app.data_tab.preserve_and_rebuild_table()
        self.main_app.data_tab.update_data_info()

    def remove_param_row(self):
        """Remove parameter row - Preserve existing data"""
        if self.main_app.var_count_var.get() > 1:
            self.main_app.var_count_var.set(self.main_app.var_count_var.get() - 1)
            self.create_param_table()

            # Remove only the last parameter column in Data Tab and preserve the rest
            self.main_app.data_tab.remove_last_parameter_column()
            self.main_app.data_tab.update_data_info()

    #######################################################################################################################

    #######################################################################################################################
    ##### Update Data Tab when Y variable name/unit changes
    def on_y_name_change(self, event=None):
        self.main_app.data_tab.update_data_headers()
        self.main_app.data_tab.update_data_info()

    #######################################################################################################################

    #######################################################################################################################
    ##### Load/Save settings function
    def load_param_config(self, config):
        self.main_app.var_count_var.set(config["num_vars"])

        if "y_name" in config:
            self.y_name_entry.delete(0, tk.END)
            self.y_name_entry.insert(0, config["y_name"])

        if "y_unit" in config:
            self.y_unit_entry.delete(0, tk.END)
            self.y_unit_entry.insert(0, config["y_unit"])

        # Load objective function
        if "objective" in config:
            self.objective_var.set(config["objective"])

        self.create_param_table()

        for i, param in enumerate(config["parameters"]):
            if i < len(self.param_entries):
                self.param_entries[i][0].delete(0, tk.END)
                self.param_entries[i][0].insert(0, param["name"])
                self.param_entries[i][1].delete(0, tk.END)
                self.param_entries[i][1].insert(0, param["unit"])
                self.param_entries[i][2].delete(0, tk.END)
                self.param_entries[i][2].insert(0, str(param["min"]))
                self.param_entries[i][3].delete(0, tk.END)
                self.param_entries[i][3].insert(0, str(param["max"]))
                self.param_entries[i][4].delete(0, tk.END)
                self.param_entries[i][4].insert(0, str(param["step"]))

        self.main_app.data_tab.update_data_headers()
        self.main_app.data_tab.update_data_info()
        self.update_warning_label()

    #######################################################################################################################

    #######################################################################################################################
    ##### Update Data Tab when parameter name changes
    def on_param_name_change(self, event=None):
        self.main_app.data_tab.update_data_headers()
        self.main_app.data_tab.update_data_info()

    #######################################################################################################################

    #######################################################################################################################
    ##### Information passed to Data Tab
    def get_y_name(self):
        y_name = self.y_name_entry.get().strip()
        return y_name if y_name else "Y"

    def get_y_unit(self):
        return self.y_unit_entry.get().strip()

    #######################################################################################################################

    #######################################################################################################################
    ##### Configuration info passed to Result Tab
    def get_param_config(self):
        config = {
            "num_vars": self.main_app.var_count_var.get(),
            "y_name": self.get_y_name(),
            "y_unit": self.y_unit_entry.get().strip(),
            "objective": self.get_objective_type(),
            "parameters": []
        }

        for i, row in enumerate(self.param_entries, start=1):
            name = (row[0].get() or f"x{i}").strip()
            # Parse numeric fields + Attach row/col info to error
            try:
                vmin = float(row[2].get())
            except ValueError as e:
                raise ValueError(f'Row {i} - "Min" must be a number (got {row[2].get()!r})') from e
            try:
                vmax = float(row[3].get())
            except ValueError as e:
                raise ValueError(f'Row {i} - "Max" must be a number (got {row[3].get()!r})') from e
            try:
                step = float(row[4].get())
            except ValueError as e:
                raise ValueError(f'Row {i} - "Step" must be a number (got {row[4].get()!r})') from e

            if vmax < vmin:
                raise ValueError(f'Row {i} - "Max" must be ≥ "Min"')
            if step <= 0:
                raise ValueError(f'Row {i} - "Step" must be > 0')

            config["parameters"].append({
                "name": name,
                "unit": row[1].get().strip(),
                "min": vmin,
                "max": vmax,
                "step": step
            })
        return config

    def get_objective_type(self):
        """Return objective function type"""
        return self.objective_var.get()

    def update_warning_label(self, event=None):
        try:
            param_config = self.get_param_config()
            param_info = param_config["parameters"]

            num_candidates = 1
            for param in param_info:
                grid_size = int((param["max"] - param["min"]) / param["step"]) + 1
                num_candidates *= grid_size
            dim = len(param_info)
            total_points = num_candidates * dim

            if total_points >= 1e7:
                warning_text = f"⚠️ Strongly recommended: reduce grid size.\n(Current: {total_points:,} points)"
                self.warning_label.config(text=warning_text, fg="red")
            elif total_points >= 1e6:
                warning_text = f"⚠️ Large candidate size: {total_points:,}\n"
                self.warning_label.config(text=warning_text, fg="orange")
            else:
                warning_text = f"Estimated candidate size: {total_points:,}\n"
                self.warning_label.config(text=warning_text, fg="green")

        except Exception:
            self.warning_label.config(text="", fg="red")
