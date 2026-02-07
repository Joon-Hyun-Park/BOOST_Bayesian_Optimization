import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pandas as pd
import numpy as np

MAX_DATA_ROWS = 20


class DataTab:
    """Class responsible for the data input tab"""

    def __init__(self, parent_notebook, main_app):
        self.main_app = main_app
        self.bg_color_2 = main_app.bg_color_2
        self.data_entries = []
        self.data_headers = []

        # create tab frame
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="Data Manager")

        self.setup_ui()

    def setup_ui(self):
        # Configure row properties
        self.frame.rowconfigure(0, weight=1)  # scrollable table (expand)
        self.frame.rowconfigure(1, weight=0, minsize=40)  # top info
        self.frame.rowconfigure(2, weight=0, minsize=50)  # buttons

        self.frame.columnconfigure(0, weight=1)

        # top info
        self.setup_info_section()
        # scrollable data table
        self.setup_scrollable_table()
        # buttons
        self.setup_buttons()
        # create initial table
        self.create_data_table()

    def setup_info_section(self):
        info_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        info_frame.grid(row=1, column=0, sticky="ew", pady=5)

        # configure info frame columns
        info_frame.columnconfigure(0, weight=1)

        self.data_info_label = tk.Label(info_frame, text="", bg=self.bg_color_2,
                                        font=self.main_app.label_font)
        self.data_info_label.grid(row=0, column=0, pady=5)

    def setup_scrollable_table(self):
        canvas_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        canvas_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # grid base layout
        # (0,0) canvas (expand), (0,1) vbar, (0,2) buttons
        # (1,0) hbar (horizontal), (1,1) corner (optional), (1,2) empty under buttons
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.rowconfigure(1, weight=0, minsize=16)  # hbar height (when visible)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.columnconfigure(1, weight=0, minsize=16)  # vbar width (when visible)

        # Create Canvas
        self.data_canvas = tk.Canvas(
            canvas_frame,
            bg=self.bg_color_2,
            highlightthickness=0, bd=0
        )
        vbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.data_canvas.yview)
        hbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.data_canvas.xview)
        self.data_canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        # layout
        self.data_canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")

        self.scrollable_frame = ttk.Frame(self.data_canvas)
        self.data_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Toggle utilities: show/hide + minsize adjustments + manage hbar columnspan
        def _show_vbar(show: bool):
            # When showing: vbar grid, column1 minsize=16
            # When hiding: vbar grid_remove, column1 minsize=0
            canvas_frame.columnconfigure(1, minsize=16)
            if show:
                vbar.grid()
            else:
                vbar.grid_remove()

        def _show_hbar(show: bool):
            # When showing: row1 minsize=16, hbar grid
            # When hiding: row1 minsize=0, hbar grid_remove
            canvas_frame.rowconfigure(1, minsize=16)
            if show:
                hbar.grid()
            else:
                hbar.grid_remove()

        # Update scrollbars and toggles
        def update_scrollbars():
            region = self.data_canvas.bbox("all")  # (x1,y1,x2,y2) or None
            if not region:
                _show_vbar(False);
                _show_hbar(False)
                return
            x1, y1, x2, y2 = region
            content_w = x2 - x1
            content_h = y2 - y1
            visible_w = max(1, self.data_canvas.winfo_width())
            visible_h = max(1, self.data_canvas.winfo_height())

            need_h = content_w > visible_w
            need_v = content_h > visible_h

            _show_hbar(need_h)
            _show_vbar(need_v)

            # Keep scrollregion up to date
            self.data_canvas.configure(scrollregion=region)

        # update when content changes (bind to scrollable_frame)
        self.scrollable_frame.bind("<Configure>", lambda e: update_scrollbars())
        # update on window/canvas resize
        self.data_canvas.bind("<Configure>", lambda e: update_scrollbars())

        # add mouse wheel scroll bindings
        def _on_mousewheel(event):
            region = self.data_canvas.bbox("all")
            if region and region[3] > self.data_canvas.winfo_height():
                self.data_canvas.yview_scroll(int(-1 * (event.delta / self.main_app.scroll_num)), "units")

        def _on_shift_mousewheel(event):
            self.data_canvas.xview_scroll(int(-1 * (event.delta / self.main_app.scroll_num)), "units")

        self.data_canvas.bind("<Enter>", lambda e: self.data_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.data_canvas.bind("<Leave>", lambda e: self.data_canvas.unbind_all("<MouseWheel>"))
        self.data_canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)

        # initial calculation
        canvas_frame.after(0, update_scrollbars)

    def setup_buttons(self):
        data_button_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        data_button_frame.grid(row=2, column=0, sticky="", pady=10)  # sticky="" = center alignment

        # place buttons using grid
        btn_col = 0

        # Row-related buttons
        add_btn = tk.Button(data_button_frame, text="   Add Row   ", command=self.add_data_row,
                            font=self.main_app.button_font)
        add_btn.grid(row=0, column=btn_col, padx=7, pady=2)
        btn_col += 1

        remove_btn = tk.Button(data_button_frame, text="Remove Last Row", command=self.remove_data_row,
                               font=self.main_app.button_font)
        remove_btn.grid(row=0, column=btn_col, padx=7, pady=2)
        btn_col += 1

        # separator
        separator = tk.Frame(data_button_frame, width=2, height=20, bg='gray')
        separator.grid(row=0, column=btn_col, padx=10, pady=2)
        btn_col += 1

        # File-related buttons
        save_btn = tk.Button(data_button_frame, text="  Save File  ", command=self.save_file,
                            font=self.main_app.button_font)
        save_btn.grid(row=0, column=btn_col, padx=7, pady=2)
        btn_col += 1

        load_btn = tk.Button(data_button_frame, text="  Load File  ", command=self.load_file,
                             font=self.main_app.button_font)
        load_btn.grid(row=0, column=btn_col, padx=7, pady=2)
        btn_col += 1

        # separator
        separator2 = tk.Frame(data_button_frame, width=2, height=20, bg='gray')
        separator2.grid(row=0, column=btn_col, padx=10, pady=2)
        btn_col += 1

        # Reset button
        reset_btn = tk.Button(data_button_frame, text="    Reset    ", command=self.clear_data,
                              font=self.main_app.button_font)
        reset_btn.grid(row=0, column=btn_col, padx=7, pady=2)

    def create_data_table(self):
        global MAX_DATA_ROWS

        # Remove existing table
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        num_vars = self.main_app.var_count_var.get()

        # Get parameter names to use as headers
        headers = []
        for i in range(num_vars):
            if (hasattr(self.main_app, 'param_tab') and
                    i < len(self.main_app.param_tab.param_entries) and
                    len(self.main_app.param_tab.param_entries[i]) > 0):
                param_name = self.main_app.param_tab.param_entries[i][0].get().strip()
                unit_name = self.main_app.param_tab.param_entries[i][1].get().strip()
                if param_name:
                    if unit_name:
                        headers.append(f"{param_name} ({unit_name})")
                    else:
                        headers.append(param_name)
                else:
                    headers.append(f"x{i + 1}")
            else:
                headers.append(f"x{i + 1}")

        # Add Y column name
        if hasattr(self.main_app, 'param_tab'):
            y_name = self.main_app.param_tab.get_y_name().strip()
            y_unit = self.main_app.param_tab.get_y_unit().strip()
        else:
            y_name = "Y"
            y_unit = ""

        if y_name:
            if y_unit:
                headers.append(f"{y_name} ({y_unit})")
            else:
                headers.append(y_name)
        else:
            headers.append("Y")  # Default if name is also empty)

        # Compute widths for each column
        entry_widths = [self.calculate_entry_width(header) for header in headers]

        # "Data" header label (first column)
        data_header_label = tk.Label(self.scrollable_frame, text=" ",
                                     font=self.main_app.label_font, bg=self.bg_color_2)
        data_header_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Store parameter header labels
        self.data_headers = []
        for j, header in enumerate(headers):
            label = tk.Label(self.scrollable_frame, text=header,
                             font=self.main_app.label_font, bg=self.bg_color_2)
            label.grid(row=0, column=j + 1, padx=5, pady=5, sticky="ew")
            self.data_headers.append(label)

        # Create data rows
        self.data_entries = []
        for i in range(MAX_DATA_ROWS):
            row_entries = []

            # Add Data number label at left
            data_label = tk.Label(self.scrollable_frame, text=f"Data {i + 1}",
                                  font=self.main_app.label_font, bg=self.bg_color_2)
            data_label.grid(row=i + 1, column=0, padx=2, pady=1)

            # Create Entry widgets for each parameter and Y value
            for j in range(num_vars + 1):
                entry = tk.Entry(self.scrollable_frame, width=entry_widths[j],
                                 font=self.main_app.button_font, justify="center")
                entry.grid(row=i + 1, column=j + 1, padx=2, pady=1)
                row_entries.append(entry)

            self.data_entries.append(row_entries)

    def calculate_entry_width(self, text):
        """Calculate an appropriate Entry widget width based on text length"""
        min_width = 8
        max_width = 20
        return max(min_width, min(max_width, len(text) + 3))

    def update_data_headers(self):
        """Update only the headers in the data tab"""
        if not hasattr(self.main_app, 'param_tab'):
            return

        num_vars = self.main_app.var_count_var.get()

        # Get new header names (including units)
        new_headers = []
        for i in range(num_vars):
            if (i < len(self.main_app.param_tab.param_entries) and
                    len(self.main_app.param_tab.param_entries[i]) > 0):
                param_name = self.main_app.param_tab.param_entries[i][0].get().strip()
                unit_name = self.main_app.param_tab.param_entries[i][1].get().strip()

                if param_name:
                    if unit_name:
                        new_headers.append(f"{param_name} ({unit_name})")
                    else:
                        new_headers.append(param_name)
                else:
                    new_headers.append(f"x{i + 1}")
            else:
                new_headers.append(f"x{i + 1}")

        # Add Y column name (including unit)
        y_name = self.main_app.param_tab.get_y_name()
        y_unit = self.main_app.param_tab.get_y_unit()
        if y_name:
            if y_unit:
                new_headers.append(f"{y_name} ({y_unit})")
            else:
                new_headers.append(y_name)
        else:
            new_headers.append("Y")

        self.preserve_and_rebuild_table()

    def update_data_info(self):
        if not hasattr(self.main_app, 'param_tab'):
            return

        num_vars = self.main_app.var_count_var.get()

        # Get and display parameter names (including units)
        var_names = []
        for i in range(num_vars):
            if (i < len(self.main_app.param_tab.param_entries) and
                    len(self.main_app.param_tab.param_entries[i]) > 0):
                param_name = self.main_app.param_tab.param_entries[i][0].get().strip()
                unit_name = self.main_app.param_tab.param_entries[i][1].get().strip()

                if param_name:
                    if unit_name:
                        var_names.append(f"{param_name} ({unit_name})")
                    else:
                        var_names.append(param_name)
                else:
                    var_names.append(f"x{i + 1}")
            else:
                var_names.append(f"x{i + 1}")

        y_name = self.main_app.param_tab.get_y_name()
        y_unit = self.main_app.param_tab.get_y_unit()
        objective = self.main_app.param_tab.get_objective_type()
        if y_unit:
            y_display = f"{y_name} ({y_unit})"
        else:
            y_display = y_name

        objective_text = "Maximization" if objective == "maximize" else "Minimization"

        self.data_info_label.config(
            text=f"Input Parameters: {', '.join(var_names)} → Target: {y_display}     [{objective_text}]"
        )

    def add_data_row(self):
        """Called when the user manually adds a row"""
        self.add_single_row()

    def remove_data_row(self):
        global MAX_DATA_ROWS
        if MAX_DATA_ROWS > 1 and len(self.data_entries) > 0:
            # remove widgets of the last row
            last_row_idx = len(self.data_entries) - 1

            # destroy all widgets in the last row
            for widget in self.scrollable_frame.grid_slaves(row=last_row_idx + 1):
                widget.destroy()

            # remove last row from data_entries
            self.data_entries.pop()


            MAX_DATA_ROWS -= 1

            # update scroll region
            self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all"))

    def clear_data(self, with_warning=True):
        if with_warning:
            # show confirmation dialog
            result = messagebox.askyesno(
                "Reset Confirmation",
                "Are you sure you want to reset all data?\n\nThis will:\n• Reset all data\n\nThis action cannot be undone."
            )

            if not result:  # user chose 'No' or closed dialog
                return

        for row in self.data_entries:
            for entry in row:
                entry.delete(0, tk.END)

    def load_file(self):
        filetypes = [
            ("All Supported Files", ("*.csv", "*.xlsx", "*.xls", "*.txt", "*.tsv")),
            ("CSV files", "*.csv"),
            ("Excel files", ("*.xlsx", "*.xls")),
            ("Text files", ("*.txt", "*.tsv")),
            ("All Files", "*"),
        ]

        try:
            filename = filedialog.askopenfilename(
                title="Select Data File",
                filetypes=filetypes,
            )
            if not filename:
                return

            # Read file according to its extension
            file_ext = filename.lower().split('.')[-1]

            if file_ext in ['xlsx', 'xls']:
                # Read Excel file
                try:
                    # read the first sheet
                    df = pd.read_excel(filename, sheet_name=0)
                except Exception as e:
                    # could prompt the user to choose if multiple sheets exist
                    messagebox.showerror("Excel Read Error", f"An error occurred while reading the Excel file:\n{str(e)}")
                    return


            elif file_ext in ['csv', 'txt', 'tsv']:
                # CSV / TXT / TSV: try multiple encodings + auto-detect delimiter
                encodings_to_try = ['utf-8', 'euc-kr', 'cp949', 'latin1']
                df = None
                for enc in encodings_to_try:
                    try:
                        # sep=None + engine='python' -> auto-detect delimiter (comma/tab/semicolon, etc.)
                        df = pd.read_csv(filename, sep=None, engine='python', encoding=enc)
                        # print(f"Loaded with encoding: {enc}")  # optional log
                        break
                    except (UnicodeDecodeError, AttributeError, ValueError):
                        continue
                    except Exception:
                        # if auto-detect fails, try whitespace delimiter as a fallback
                        try:
                            df = pd.read_csv(filename, delim_whitespace=True, encoding=enc)
                            break
                        except Exception:
                            continue

                if df is None:
                    messagebox.showerror(
                        "File Read Error",
                        "Could not read the file with any of the supported encodings "
                        "(utf-8, euc-kr, cp949, latin1)."
                    )
                    return
            else:
                messagebox.showerror("Unsupported Format",
                                     f"The file type '{file_ext}' is not supported.")
                return

            # Check whether the dataframe is empty
            if df.empty:
                messagebox.showwarning("Empty File", "The file contains no data.")
                return

            new_headers = list(df.columns)  # file column headers
            file_var_count = max(0, len(new_headers) - 1)  # number of X (excluding Y)
            num_vars = self.main_app.var_count_var.get()

            # ─────────────────────────────────────────────────────────
            # 1) (First) Handle variable count mismatch -> Fix structure
            # ─────────────────────────────────────────────────────────
            num_vars = self.main_app.var_count_var.get()
            if file_var_count != num_vars:
                if messagebox.askyesno(
                        "Adjust Variable Count",
                        f"The number of variables in the file ({file_var_count}) does not match the current setting ({num_vars}).\n"
                        f"Do you want to adjust the variable count to {file_var_count}?"
                ):
                    self.main_app.var_count_var.set(file_var_count)
                    # Variable count changed, refresh all table structures
                    self.main_app.param_tab.create_param_table()
                    self.preserve_and_rebuild_table()
                    self.update_data_info()

            # fetch the updated variable count
            current_num_vars = self.main_app.var_count_var.get()

            # ─────────────────────────────────────────────────────────
            # 2) (After structure fix) Handle header replacement -> Fill content
            # ─────────────────────────────────────────────────────────
            if messagebox.askyesno(
                    "Header Detected",
                    "A header row has been detected.\nDo you want to replace the existing parameter names with this header?"
            ):
                # Y name/unit (always last column)
                if len(new_headers) > 0:
                    y_full = new_headers[-1]
                    y_match = re.match(r"(.*?)\s*\((.*?)\)", y_full)
                    if y_match:
                        y_name, y_unit = y_match.group(1).strip(), y_match.group(2).strip()
                    # ... (existing Y name parsing logic remains) ...
                    else:
                        y_name, y_unit = y_full.strip(), ""
                    self.main_app.param_tab.y_name_entry.delete(0, tk.END)
                    self.main_app.param_tab.y_name_entry.insert(0, y_name)
                    self.main_app.param_tab.y_unit_entry.delete(0, tk.END)
                    self.main_app.param_tab.y_unit_entry.insert(0, y_unit)

                # X name/unit (apply exactly for current variable count)
                for i in range(min(current_num_vars, len(new_headers) - 1)):
                    header = new_headers[i]
                    m = re.match(r"(.*?)\s*\((.*?)\)", header)
                    if m:
                        name, unit = m.group(1).strip(), m.group(2).strip()
                    # ... (Same as existing X name parsing logic) ...
                    else:
                        name, unit = header.strip(), ""
                    if i < len(self.main_app.param_tab.param_entries):
                        self.main_app.param_tab.param_entries[i][0].delete(0, tk.END)
                        self.main_app.param_tab.param_entries[i][0].insert(0, name)
                        self.main_app.param_tab.param_entries[i][1].delete(0, tk.END)
                        self.main_app.param_tab.param_entries[i][1].insert(0, unit)

                # header changed; update display
                self.update_data_headers()
                self.update_data_info()

            # 3) Ensure enough rows + clear existing data + insert new data
            required_rows = len(df)
            while len(self.data_entries) < required_rows:
                self.add_single_row()

            self.clear_data(with_warning=False)

            # Insert data (based on latest variable count)
            for i, row in df.iterrows():
                if i < len(self.data_entries):
                    # Insert X values (first current_num_vars columns)
                    for j in range(min(current_num_vars, len(row) - 1)):
                        value = row.iloc[j]
                        self.data_entries[i][j].insert(0, "" if pd.isna(value) else str(value))

                    # Insert Y value (always last column)
                    y_value = row.iloc[-1]
                    # Index for Y value Entry is current_num_vars
                    if current_num_vars < len(self.data_entries[i]):
                        self.data_entries[i][current_num_vars].insert(
                            0, "" if pd.isna(y_value) else str(y_value)
                        )

            messagebox.showinfo("Load Complete", f"{len(df)} rows have been successfully loaded.")

        except Exception as e:
            messagebox.showerror("File Load Error", f"An error occurred while reading the file:\n{str(e)}")

    def save_file(self):
        try:
            data = self.extract_data_only()
            if data.empty:
                messagebox.showwarning("Warning", "No data available to save.")
                return

            filetypes = [
                ("All Supported Files", ("*.csv", "*.xlsx", "*.xls", "*.txt", "*.tsv")),
                ("CSV files", "*.csv"),
                ("Excel files", ("*.xlsx", "*.xls")),
                ("Text files", ("*.txt", "*.tsv")),
                ("All Files", "*"),
            ]

            filename = filedialog.asksaveasfilename(
                title="Save Data File",
                defaultextension=".csv",
                filetypes=filetypes
            )
            if not filename:
                return

            # 🔁 Normalize to safe symbols (℃→°C, ℉→°F, etc.)
            df_to_save = data.copy()
            try:
                for col in df_to_save.columns:
                    if df_to_save[col].dtype == "object":
                        s = df_to_save[col].astype(str)
                        s = s.str.replace("\u2103", "°C", regex=False)  # ℃ → °C
                        s = s.str.replace("\u2109", "°F", regex=False)  # ℉ → °F
                        df_to_save[col] = s
            except Exception:
                pass  # Ignore if issues occur during string conversion

            file_ext = filename.lower().split('.')[-1]

            if file_ext in ('xlsx', 'xls'):
                # Excel is unicode safe (handled by openpyxl)
                try:
                    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                        df_to_save.to_excel(writer, sheet_name='Data', index=False)

                        # (Optional) Header style + Auto column width
                        try:
                            workbook = writer.book
                            worksheet = writer.sheets['Data']
                            from openpyxl.styles import Font, PatternFill
                            header_font = Font(bold=True)
                            header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                            for cell in worksheet[1]:
                                cell.font = header_font
                                cell.fill = header_fill
                            for column in worksheet.columns:
                                max_len = 0
                                col_letter = column[0].column_letter
                                for cell in column:
                                    val = "" if cell.value is None else str(cell.value)
                                    max_len = max(max_len, len(val))
                                worksheet.column_dimensions[col_letter].width = min(max_len + 2, 20)
                        except Exception:
                            pass
                except ImportError:
                    messagebox.showerror(
                        "Library Error",
                        "The 'openpyxl' library is required for saving Excel files.\n"
                        "Please install it with: pip install openpyxl"
                    )
                    return
                except Exception as e:
                    messagebox.showerror("Excel Save Error",
                                         f"An error occurred while saving the Excel file:\n{str(e)}")
                    return

            elif file_ext in ('tsv', 'txt'):
                # ✅ Save as UTF-8 with BOM -> Good compatibility with Excel/Notepad
                df_to_save.to_csv(filename, sep='\t', index=False, encoding='utf-8-sig')

            elif file_ext == 'csv':
                # ✅ UTF-8 with BOM
                df_to_save.to_csv(filename, index=False, encoding='utf-8-sig')

            else:
                # If extension is ambiguous, save as CSV (UTF-8 BOM)
                if not filename.lower().endswith('.csv'):
                    filename = filename + ".csv"
                df_to_save.to_csv(filename, index=False, encoding='utf-8-sig')

            messagebox.showinfo("Save Complete", f"Data has been saved to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving the file:\n{str(e)}")

    def extract_data_only(self):
        """Extract data only"""
        try:
            if not hasattr(self.main_app, 'param_tab'):
                return pd.DataFrame()

            num_vars = self.main_app.var_count_var.get()

            # Get and use parameter names (including units)
            var_names = []
            for i in range(num_vars):
                if (i < len(self.main_app.param_tab.param_entries) and
                        len(self.main_app.param_tab.param_entries[i]) > 0):
                    param_name = self.main_app.param_tab.param_entries[i][0].get().strip()
                    unit_name = self.main_app.param_tab.param_entries[i][1].get().strip()

                    if param_name:
                        if unit_name:
                            var_names.append(f"{param_name} ({unit_name})")
                        else:
                            var_names.append(param_name)
                    else:
                        var_names.append(f"x{i + 1}")
                else:
                    var_names.append(f"x{i + 1}")

            rows = []
            for row_entries in self.data_entries:
                row = []
                for j in range(num_vars + 1):
                    val = row_entries[j].get().strip()
                    if val:  # If value is not empty
                        try:
                            row.append(float(val))
                        except ValueError:
                            # Treat as NaN if value cannot be converted to number
                            row.append(np.nan)
                    else:  # If value is empty
                        row.append(np.nan)  # Add as NaN (Not a Number)

                if len(row) == num_vars + 1:
                    rows.append(row)
                elif len(row) > 0:
                    break

            if rows:
                # Y column name also includes unit
                y_name = self.main_app.param_tab.get_y_name()
                y_unit = self.main_app.param_tab.get_y_unit()

                if y_name:
                    if y_unit:
                        y_column = f"{y_name} ({y_unit})"
                    else:
                        y_column = y_name
                else:
                    y_column = "Y"

                return pd.DataFrame(rows, columns=var_names + [y_column])
            else:
                return pd.DataFrame()
        except Exception:
            return pd.DataFrame()

    # Added to _data_tab.py
    def add_suggested_points(self, points, param_info):
        """Add recommended points to the end of the data table"""
        global MAX_DATA_ROWS

        # Find the last row with data
        last_row_with_data = -1
        for i, row_entries in enumerate(self.data_entries):
            has_data = any(entry.get().strip() for entry in row_entries)
            if has_data:
                last_row_with_data = i

        start_row = last_row_with_data + 1
        needed_rows = start_row + len(points)

        # Automatically add rows as needed
        while len(self.data_entries) < needed_rows:
            self.add_single_row()

        # Add points
        for i, point in enumerate(points):
            row_idx = start_row + i
            if row_idx < len(self.data_entries):
                for j, value in enumerate(point):
                    if j < len(self.data_entries[row_idx]):
                        # If existing value exists, clear and insert new value
                        self.data_entries[row_idx][j].delete(0, tk.END)
                        self.data_entries[row_idx][j].insert(0, str(value))

        messagebox.showinfo("Points Added", f"{len(points)} recommended points have been added to the data table.")

    def add_single_row(self):
        """Helper function to dynamically add a single row"""
        global MAX_DATA_ROWS

        num_vars = self.main_app.var_count_var.get()

        # Get header info
        headers = []
        for i in range(num_vars):
            if (hasattr(self.main_app, 'param_tab') and
                    i < len(self.main_app.param_tab.param_entries) and
                    len(self.main_app.param_tab.param_entries[i]) > 0):
                param_name = self.main_app.param_tab.param_entries[i][0].get().strip()
                unit_name = self.main_app.param_tab.param_entries[i][1].get().strip()
                if param_name:
                    if unit_name:
                        headers.append(f"{param_name} ({unit_name})")
                    else:
                        headers.append(param_name)
                else:
                    headers.append(f"x{i + 1}")
            else:
                headers.append(f"x{i + 1}")

        # Add Y column name
        if hasattr(self.main_app, 'param_tab'):
            y_name = self.main_app.param_tab.get_y_name().strip()
            y_unit = self.main_app.param_tab.get_y_unit().strip()
            if y_name:
                if y_unit:
                    headers.append(f"{y_name} ({y_unit})")
                else:
                    headers.append(y_name)
            else:
                headers.append("Y")

        entry_widths = [self.calculate_entry_width(header) for header in headers]

        # Add new row
        new_row_idx = len(self.data_entries)
        row_entries = []

        # Row number label
        data_label = tk.Label(self.scrollable_frame, text=f"Data {new_row_idx + 1}",
                              font=self.main_app.label_font, bg=self.bg_color_2)
        data_label.grid(row=new_row_idx + 1, column=0, padx=2, pady=1)

        # Add Entry widgets
        for j in range(num_vars + 1):
            entry = tk.Entry(self.scrollable_frame, width=entry_widths[j],
                             font=self.main_app.button_font, justify="center")
            entry.grid(row=new_row_idx + 1, column=j + 1, padx=2, pady=1)
            row_entries.append(entry)

        self.data_entries.append(row_entries)
        MAX_DATA_ROWS += 1

        # Update scroll region
        self.scrollable_frame.update_idletasks()
        self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all"))

    # Functions to add to _data_tab.py

    def remove_last_parameter_column(self):
        """Remove only the last parameter column (Keep Y column)"""
        # Backup current data
        current_data = []
        for row_entries in self.data_entries:
            row_data = []
            # Parameters before Y value (excluding last parameter)
            for j in range(len(row_entries) - 2):  # Up to second to last (excluding parameter to remove)
                row_data.append(row_entries[j].get())
            # Add Y column value (always last)
            if len(row_entries) > 0:
                row_data.append(row_entries[-1].get())
            current_data.append(row_data)

        # Rebuild table
        self.create_data_table()

        # Restore data
        num_vars = self.main_app.var_count_var.get()
        for i, row_data in enumerate(current_data):
            if i < len(self.data_entries):
                # Restore parameters
                for j in range(len(row_data) - 1):  # Parameters excluding Y value
                    if j < len(self.data_entries[i]):
                        self.data_entries[i][j].insert(0, row_data[j])
                # Restore Y value (always last column)
                if len(row_data) > 0 and len(self.data_entries[i]) > num_vars:
                    self.data_entries[i][num_vars].insert(0, row_data[-1])

    def preserve_and_rebuild_table(self):
        """Rebuild table while preserving existing data (Insert empty column before Y value when adding parameter)"""
        # Backup current data
        current_data = []
        for row_entries in self.data_entries:
            row_data = [entry.get() for entry in row_entries]
            current_data.append(row_data)

        # Rebuild table
        self.create_data_table()

        # Restore data
        old_num_vars = len(current_data[0]) - 1 if current_data and current_data[0] else 0  # Number of previous parameters excluding Y
        new_num_vars = self.main_app.var_count_var.get()

        for i, row_data in enumerate(current_data):
            if i < len(self.data_entries) and row_data:
                # Restore existing parameters
                for j in range(min(old_num_vars, new_num_vars)):
                    if j < len(self.data_entries[i]):
                        self.data_entries[i][j].insert(0, row_data[j])

                # Restore Y value (always last column)
                if len(row_data) > old_num_vars and new_num_vars < len(self.data_entries[i]):
                    self.data_entries[i][new_num_vars].insert(0, row_data[-1])

                # Newly added parameter columns remain empty automatically