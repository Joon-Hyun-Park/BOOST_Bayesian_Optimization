import os
import tkinter as tk
from tkinter import ttk, messagebox

os.environ['OMP_NUM_THREADS'] = '1'

import numpy as np
import torch
import psutil

from BOOST import BOOST
from BayesianOptimization import BayesianOptimizer


class ResultTab(BayesianOptimizer):
    """Run and Results tab (grid layout, central font control, buttons at bottom)"""

    def __init__(self, parent_notebook, main_app):
        super().__init__()
        self.main_app = main_app
        self.bg_color_2 = main_app.bg_color_2
        self.last_suggested_points = None  # store last suggested points
        self.last_param_info = None        # store last parameter info

        # create tab frame (English title)
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="Run & Results")

        self.setup_ui()

    def setup_ui(self):
        # ----- grid base layout -----
        # row 0: result text area (scrollable)  [expand]
        # row 1: suggestion label                [size to content]
        # row 2: button bar (run/add)            [fixed, bottom]
        self.frame.rowconfigure(0, weight=1)   # expand text area
        self.frame.rowconfigure(1, weight=0)
        self.frame.rowconfigure(2, weight=0, minsize=60)
        self.frame.columnconfigure(0, weight=1)

        # ----- Result Display Area (Text + Scrollbar) -----
        result_display_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        result_display_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(15, 5))

        result_display_frame.rowconfigure(0, weight=0)  # "Current Data:" label
        result_display_frame.rowconfigure(1, weight=1)  # Text expands
        result_display_frame.columnconfigure(0, weight=1)
        result_display_frame.columnconfigure(1, weight=0)

        title_lbl = tk.Label(
            result_display_frame,
            text="Current Data:",
            font=self.main_app.label_font,
            bg=self.bg_color_2
        )
        title_lbl.grid(row=0, column=0, sticky="w")

        self.result_text = tk.Text(
            result_display_frame,
            height=15, width=70,
            font=self.main_app.button_font
        )
        result_scrollbar = ttk.Scrollbar(
            result_display_frame, orient="vertical", command=self.result_text.yview
        )
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

        self.result_text.grid(row=1, column=0, sticky="nsew")
        result_scrollbar.grid(row=1, column=1, sticky="ns")

        # ----- suggestion label -----
        self.suggestion_label = tk.Label(
            self.frame,
            text="",
            font=self.main_app.label_font,
            bg=self.bg_color_2
        )
        self.suggestion_label.grid(row=1, column=0, sticky="", padx=20, pady=(5, 5))

        # ----- button bar (bottom) -----
        button_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        button_frame.grid(row=2, column=0, sticky="", pady=(5, 15))

        # Run button
        run_btn = tk.Button(
            button_frame,
            text="Suggest Next Points",
            command=self.run_optimization,
            font=self.main_app.button_font,
            bg=self.bg_color_2,
            takefocus=False
        )
        run_btn.grid(row=0, column=0, padx=7, pady=2)

        # separator
        sep = tk.Frame(button_frame, width=2, height=20, bg='gray')
        sep.grid(row=0, column=1, padx=10, pady=2)

        # Add recommended points button (initially disabled)
        self.add_points_button = tk.Button(
            button_frame,
            text="Add Recommended Points",
            command=self.add_suggested_points_to_data,
            font=self.main_app.button_font,
            bg=self.bg_color_2,
            state="disabled",
            takefocus=False
        )
        self.add_points_button.grid(row=0, column=2, padx=7, pady=2)


    def run_optimization(self):
        try:
            # extract data
            df = self.main_app.data_tab.extract_data_only()
            partially_filled = df[df.notna().any(axis=1) & df.isna().any(axis=1)]
            if len(partially_filled) > 0:
                missing_indices = [i + 1 for i in partially_filled.index]

                messagebox.showwarning(
                    "Incomplete Data Detected",
                    f"{len(partially_filled)} row(s) are partially filled and must be completed:\n"
                    f"Rows: {', '.join(map(str, missing_indices[:10]))}"
                    f"{'...' if len(missing_indices) > 10 else ''}\n\n"
                    "Please fill in all values or delete these rows before running optimization."
                )
                return
            df = df.dropna()

            if df.empty or len(df) < 6:
                # If insufficient data: use LHS sampling
                param_config = self.main_app.param_tab.get_param_config()
                param_info = param_config["parameters"]

                # display results
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "Parameter Settings:\n")
                for param in param_info:
                    self.result_text.insert(
                        tk.END,
                        f"  {param['name']}: [{param['min']}, {param['max']}], step={param['step']}\n"
                    )

                self.result_text.insert(tk.END, f"Target Variable: {param_config['y_name']}\n")

                if df.empty:
                    self.result_text.insert(tk.END, "\nNo data found. Running LHS sampling for initial exploration.\n")
                    n_samples = 10
                else:
                    self.result_text.insert(tk.END, f"\nCurrent Data ({len(df)} rows):\n", )
                    self.result_text.insert(tk.END, df.to_string(index=False))
                    self.result_text.insert(tk.END, "\n\nData is insufficient. Running LHS sampling.\n")
                    n_samples = 10 - len(df)

                # Run LHS sampling
                dim = len(param_info)
                next_points = self._generate_lhs_samples(dim, n_samples, param_info=param_info)

                # store recommended points and parameter info
                self.last_suggested_points = next_points
                self.last_param_info = param_info
                self.add_points_button.config(state="normal")  # enable button

                suggestion_text = (
                    f"LHS recommended points ({len(next_points)}):\n" +
                    "\n".join([
                        "Point {idx}: ".format(idx=i + 1) +
                        ", ".join([f"{param_info[j]['name']}={point[j]}" for j in range(len(point))])
                        for i, point in enumerate(next_points)
                    ])
                )
                self.suggestion_label.config(text=suggestion_text)
                return

            # Extract parameter info
            param_config = self.main_app.param_tab.get_param_config()
            param_info = param_config["parameters"]
            is_maximization = param_config.get("objective", "maximize") == "maximize"

            # display results
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Parameter Settings:\n")
            for param in param_info:
                self.result_text.insert(
                    tk.END,
                    f"  {param['name']}: [{param['min']}, {param['max']}], step={param['step']}\n"
                )

            self.result_text.insert(tk.END, f"Target Variable: {param_config['y_name']}\n")
            self.result_text.insert(tk.END, f"\nCurrent Data ({len(df)} rows):\n")
            self.result_text.insert(tk.END, df.to_string(index=False))

            # extract X, Y from GUI data
            train_x_list, train_y_list = [], []
            for _, row in df.iterrows():
                x_values = [row.iloc[i] for i in range(len(param_info))]
                train_x_list.append(x_values)
                y_value = row.iloc[-1]
                train_y_list.append(y_value)

            # convert to torch tensors
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            train_x = torch.tensor(train_x_list, dtype=torch.double, device=device)
            train_y = torch.tensor(train_y_list, dtype=torch.double, device=device)

            # if maximization, invert sign (internal minimization)
            if is_maximization:
                train_y = -train_y
                self.result_text.insert(tk.END, f"\n\nObjective: maximize {param_config['y_name']}\n")
            else:
                self.result_text.insert(tk.END, f"\n\nObjective: minimize {param_config['y_name']}\n")

            # generate candidate points (grid)
            candidate_points = []
            for d, param in enumerate(param_info):
                grid = []
                current = param['min']
                while current <= param['max']:
                    grid.append(current)
                    current = round(current + param['step'], 10)
                candidate_points.append(torch.tensor(grid, dtype=torch.double, device=device))


            # Check number of candidate points and memory usage
            num_candidates = 1
            for grid in candidate_points:
                num_candidates *= len(grid)

            dim = len(candidate_points)
            expected_mem = num_candidates * dim * 8  # GB unit (based on float64)
            mem = psutil.virtual_memory()

            print(expected_mem/ (1024**3))
            print(mem.total/ (1024**3))

            used_ratio = expected_mem / mem.total  # expected ratio of total RAM

            if used_ratio >= 0.2:
                messagebox.showwarning(
                    "Memory Warning",
                    f"Candidate points may require ~{expected_mem:.2f} GB "
                    f"({used_ratio * 100:.1f}% of total RAM).\n\n"
                    "This could slow down or freeze the program. "
                    "Consider reducing parameter ranges or step size."
                )
                return
            # ────────────────────────────────────────────────────────────────

            candidate_x = torch.cartesian_prod(*candidate_points).to(device)

            # remove already evaluated points
            mask = ~torch.any(torch.cdist(candidate_x, train_x) < 1e-5, dim=1)
            filtered_candidate_x = candidate_x[mask]

            # check data count
            if len(train_x) < 6:
                messagebox.showwarning("Insufficient Data", "At least 6 data points are required to use BOOST.")
                return

            if len(filtered_candidate_x) == 0:
                messagebox.showinfo("Optimization Complete", "All possible combinations have already been evaluated!")
                return

            # show progress
            self.result_text.insert(tk.END, "\nRunning Bayesian Optimization...\n")
            self.result_text.insert(tk.END, "Searching for the best kernel–acquisition pair...\n")
            self.result_text.update()  # Update UI immediately

            boost = BOOST(device=device)
            kernel_type, acquisition_type = boost.get_kernel_acq(train_x=train_x, train_y=train_y)

            self.result_text.insert(tk.END, f"Selected kernel: {kernel_type.value}\n")
            self.result_text.insert(tk.END, f"Selected acquisition: {acquisition_type.value}\n")

            next_point, _, prediction_mean, prediction_var = self.get_next_point(
                train_x=train_x,
                train_y=train_y,
                filtered_candidate_x=filtered_candidate_x,
                kernel_type=kernel_type,
                acquisition_type=acquisition_type
            )

            prediction_std = np.sqrt(prediction_var)

            # revert maximization
            if is_maximization:
                prediction_mean = -prediction_mean

            # 67% confidence interval
            lower_bound = prediction_mean - prediction_std
            upper_bound = prediction_mean + prediction_std

            # convert next_point
            next_point_cpu = next_point.cpu().numpy().flatten()
            next_point_list = [round(float(val), 4) for val in next_point_cpu]

            # display results
            self.result_text.insert(tk.END, "\n=== Prediction ===\n")
            point_str = ", ".join([f"{param_info[i]['name']}={next_point_list[i]}"
                                   for i in range(len(next_point_list))])
            self.result_text.insert(tk.END, f"Recommended Point: {point_str}\n")
            self.result_text.insert(tk.END, f"Predicted {param_config['y_name']}: {prediction_mean:.4f}\n")
            self.result_text.insert(tk.END, f"67% CI: [{lower_bound:.4f}, {upper_bound:.4f}]\n")
            self.result_text.insert(tk.END, f"Std. (±1σ): {prediction_std:.4f}\n")

            suggestion_text = (
                "Suggested Point: " +
                point_str +
                f"\nPredicted {param_config['y_name']}: [{lower_bound:.4f}, {upper_bound:.4f}]"
            )
            self.suggestion_label.config(text=suggestion_text)

            # store single point as a list
            self.last_suggested_points = [next_point_list]
            self.last_param_info = param_info
            self.add_points_button.config(state="normal")

        except Exception as e:
            messagebox.showerror("Execution Error", str(e))

    def add_suggested_points_to_data(self):
        """Add recommended points to the data tab"""
        if self.last_suggested_points and self.last_param_info:
            self.main_app.data_tab.add_suggested_points(self.last_suggested_points, self.last_param_info)
            self.add_points_button.config(state="disabled")  # Disable after adding
        else:
            messagebox.showwarning("Warning", "There are no recommended points to add.")

    def _generate_lhs_samples(self, dim, n_samples, param_info=None):
        """LHS for discrete grid points."""
        import numpy as np
        from itertools import product
        import torch
        import random

        # Check existing evaluated points
        evaluated_set = set()
        df = self.main_app.data_tab.extract_data_only()
        if not df.empty:
            for _, row in df.iterrows():
                point = tuple(np.round([row.iloc[i] for i in range(dim)], 6))
                evaluated_set.add(point)

        generated_samples = set()

        # Number of grid points per dimension
        dim_grid_sizes = []
        for d in range(dim):
            param = param_info[d] if param_info else None
            grid_size = int(round((param['max'] - param['min']) / param['step'], 6)) + 1
            dim_grid_sizes.append(grid_size)

        max_possible_samples = min(dim_grid_sizes)
        actual_n_samples = min(n_samples, max_possible_samples)
        n_samples = max(min(n_samples, max_possible_samples), 6)

        while len(generated_samples) < n_samples:
            # LHS candidate in each dim
            lhs_points = []
            for d in range(dim):
                param = param_info[d] if param_info else None
                grid_points = []
                current = param['min']
                while current <= param['max']:
                    grid_points.append(current)
                    current = round(current + param['step'], 10)
                grid_points = torch.tensor(grid_points, dtype=torch.double)

                n_grid_actual = len(grid_points)
                lhs_step = max(1, (n_grid_actual - 1) // (actual_n_samples - 1))
                lhs_start = ((n_grid_actual - 1) - lhs_step * (actual_n_samples - 1)) // 2
                dim_points = [grid_points[lhs_start + i * lhs_step].item() for i in range(actual_n_samples)]
                random.shuffle(dim_points)
                lhs_points.append(dim_points)

            # If combinations are too few for LHS -> Random sample from possible combinations
            if n_samples >= max_possible_samples ** d:
                grid_lists = []
                for param in param_info:
                    grid = []
                    current = param['min']
                    while current <= param['max']:
                        grid.append(round(current, 6))
                        current = round(current + param['step'], 10)
                    grid_lists.append(grid)

                all_combinations = list(product(*grid_lists))
                all_combinations = [p for p in all_combinations if tuple(np.round(p, 6)) not in evaluated_set]

                available = len(all_combinations)
                if available < n_samples:
                    messagebox.showwarning(
                        "Insufficient Samples",
                        f"Requested {n_samples} samples, but only {available} combinations are available.\n"
                        f"Only {available} will be generated."
                    )
                else:
                    messagebox.showinfo(
                        "LHS Fallback",
                        "LHS is not suitable here; random sampling from all available combinations will be used."
                    )

                random.shuffle(all_combinations)
                return [list(p) for p in all_combinations[:n_samples]]

            else:
                # add to generated_samples
                new_points = list(zip(*lhs_points))
                for point in new_points:
                    point_tuple = tuple(np.round(point, 6))
                    if (point_tuple not in evaluated_set) and (point_tuple not in generated_samples):
                        generated_samples.add(point_tuple)
                    if len(generated_samples) >= n_samples:
                        break

        return [list(point) for point in list(generated_samples)]
