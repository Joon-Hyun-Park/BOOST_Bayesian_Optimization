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
    """실행 및 결과 탭 (grid 레이아웃, 중앙 폰트 제어, 버튼 하단 배치)"""

    def __init__(self, parent_notebook, main_app):
        super().__init__()
        self.main_app = main_app
        self.bg_color_2 = main_app.bg_color_2
        self.last_suggested_points = None  # 마지막 추천 포인트 저장
        self.last_param_info = None        # 마지막 파라미터 정보 저장

        # 탭 프레임 생성 (영문 제목)
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="Run & Results")

        self.setup_ui()

    def setup_ui(self):
        # ----- grid 베이스 레이아웃 -----
        # row 0: 결과 텍스트 영역(스크롤)  [확장]
        # row 1: 제안 라벨                [내용 크기만]
        # row 2: 버튼 바(실행/추가)        [고정, 하단]
        self.frame.rowconfigure(0, weight=1)   # 텍스트 영역 확장
        self.frame.rowconfigure(1, weight=0)
        self.frame.rowconfigure(2, weight=0, minsize=60)
        self.frame.columnconfigure(0, weight=1)

        # ----- 결과 표시 영역 (Text + Scrollbar) -----
        result_display_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        result_display_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(15, 5))

        result_display_frame.rowconfigure(0, weight=0)  # "Current Data:" 라벨
        result_display_frame.rowconfigure(1, weight=1)  # Text 확장
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

        # ----- 제안 라벨 -----
        self.suggestion_label = tk.Label(
            self.frame,
            text="",
            font=self.main_app.label_font,
            bg=self.bg_color_2
        )
        self.suggestion_label.grid(row=1, column=0, sticky="", padx=20, pady=(5, 5))

        # ----- 버튼 바 (하단) -----
        button_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        button_frame.grid(row=2, column=0, sticky="", pady=(5, 15))

        # 실행 버튼
        run_btn = tk.Button(
            button_frame,
            text="Suggest Next Points",
            command=self.run_optimization,
            font=self.main_app.button_font,
            bg=self.bg_color_2,
            takefocus=False
        )
        run_btn.grid(row=0, column=0, padx=7, pady=2)

        # 구분선
        sep = tk.Frame(button_frame, width=2, height=20, bg='gray')
        sep.grid(row=0, column=1, padx=10, pady=2)

        # 추천 포인트 추가 버튼 (초기 비활성화)
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
            # 데이터 추출
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
                # 데이터가 부족할 때: LHS 샘플링
                param_config = self.main_app.param_tab.get_param_config()
                param_info = param_config["parameters"]

                # 결과 표시
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

                # LHS 샘플링 실행
                dim = len(param_info)
                next_points = self._generate_lhs_samples(dim, n_samples, param_info=param_info)

                # 추천 포인트와 파라미터 정보 저장
                self.last_suggested_points = next_points
                self.last_param_info = param_info
                self.add_points_button.config(state="normal")  # 버튼 활성화

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

            # Parameter 정보 추출
            param_config = self.main_app.param_tab.get_param_config()
            param_info = param_config["parameters"]
            is_maximization = param_config.get("objective", "maximize") == "maximize"

            # 결과 표시
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

            # GUI 데이터에서 X, Y 추출
            train_x_list, train_y_list = [], []
            for _, row in df.iterrows():
                x_values = [row.iloc[i] for i in range(len(param_info))]
                train_x_list.append(x_values)
                y_value = row.iloc[-1]
                train_y_list.append(y_value)

            # torch tensor로 변환
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            train_x = torch.tensor(train_x_list, dtype=torch.double, device=device)
            train_y = torch.tensor(train_y_list, dtype=torch.double, device=device)

            # 최대화 문제면 부호 변경 (내부 최소화 형태로)
            if is_maximization:
                train_y = -train_y
                self.result_text.insert(tk.END, f"\n\nObjective: maximize {param_config['y_name']}\n")
            else:
                self.result_text.insert(tk.END, f"\n\nObjective: minimize {param_config['y_name']}\n")

            # candidate points 생성 (grid)
            candidate_points = []
            for d, param in enumerate(param_info):
                grid = []
                current = param['min']
                while current <= param['max']:
                    grid.append(current)
                    current = round(current + param['step'], 10)
                candidate_points.append(torch.tensor(grid, dtype=torch.double, device=device))


            # ── 💡 후보점 개수 및 메모리 사용량 체크 ─────────────────────────────
            num_candidates = 1
            for grid in candidate_points:
                num_candidates *= len(grid)

            dim = len(candidate_points)
            expected_mem = num_candidates * dim * 8  # GB 단위 (float64 기준)
            mem = psutil.virtual_memory()

            print(expected_mem/ (1024**3))
            print(mem.total/ (1024**3))

            used_ratio = expected_mem / mem.total  # 전체 RAM 대비 예상 비율

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

            # 이미 평가된 점들 제거
            mask = ~torch.any(torch.cdist(candidate_x, train_x) < 1e-5, dim=1)
            filtered_candidate_x = candidate_x[mask]

            # 데이터 수 체크
            if len(train_x) < 6:
                messagebox.showwarning("Insufficient Data", "At least 6 data points are required to use BOOST.")
                return

            if len(filtered_candidate_x) == 0:
                messagebox.showinfo("Optimization Complete", "All possible combinations have already been evaluated!")
                return

            # 진행 상황 출력
            self.result_text.insert(tk.END, "\nRunning Bayesian Optimization...\n")
            self.result_text.insert(tk.END, "Searching for the best kernel–acquisition pair...\n")
            self.result_text.update()  # UI 즉시 업데이트

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

            # 최대화 원복
            if is_maximization:
                prediction_mean = -prediction_mean

            # 67% 신뢰구간
            lower_bound = prediction_mean - prediction_std
            upper_bound = prediction_mean + prediction_std

            # next_point 변환
            next_point_cpu = next_point.cpu().numpy().flatten()
            next_point_list = [round(float(val), 4) for val in next_point_cpu]

            # 결과 표시
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

            # 단일 포인트도 리스트로 저장
            self.last_suggested_points = [next_point_list]
            self.last_param_info = param_info
            self.add_points_button.config(state="normal")

        except Exception as e:
            messagebox.showerror("Execution Error", str(e))

    def add_suggested_points_to_data(self):
        """추천된 포인트들을 데이터 탭에 추가"""
        if self.last_suggested_points and self.last_param_info:
            self.main_app.data_tab.add_suggested_points(self.last_suggested_points, self.last_param_info)
            self.add_points_button.config(state="disabled")  # 추가 후 비활성화
        else:
            messagebox.showwarning("Warning", "There are no recommended points to add.")

    def _generate_lhs_samples(self, dim, n_samples, param_info=None):
        """LHS for discrete grid points."""
        import numpy as np
        from itertools import product
        import torch
        import random

        # 기존 평가된 점들 확인
        evaluated_set = set()
        df = self.main_app.data_tab.extract_data_only()
        if not df.empty:
            for _, row in df.iterrows():
                point = tuple(np.round([row.iloc[i] for i in range(dim)], 6))
                evaluated_set.add(point)

        generated_samples = set()

        # 각 차원별 grid point 개수
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

            # 조합 수가 적어서 LHS가 무의미한 경우 → 가능한 조합에서 랜덤 샘플
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
