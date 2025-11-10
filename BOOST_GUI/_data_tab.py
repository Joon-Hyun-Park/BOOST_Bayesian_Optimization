import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pandas as pd
import numpy as np

MAX_DATA_ROWS = 20


class DataTab:
    """데이터 입력 탭을 담당하는 클래스"""

    def __init__(self, parent_notebook, main_app):
        self.main_app = main_app
        self.bg_color_2 = main_app.bg_color_2
        self.data_entries = []
        self.data_headers = []

        # 탭 프레임 생성
        self.frame = ttk.Frame(parent_notebook)
        parent_notebook.add(self.frame, text="Data Manager")

        self.setup_ui()

    def setup_ui(self):
        # 행(row) 속성 설정
        self.frame.rowconfigure(0, weight=1)  # 스크롤 테이블 (확장)
        self.frame.rowconfigure(1, weight=0, minsize=40)  # 상단 정보
        self.frame.rowconfigure(2, weight=0, minsize=50)  # 버튼들

        self.frame.columnconfigure(0, weight=1)

        # 상단 정보
        self.setup_info_section()
        # 스크롤 가능한 데이터 테이블
        self.setup_scrollable_table()
        # 버튼들
        self.setup_buttons()
        # 초기 테이블 생성
        self.create_data_table()

    def setup_info_section(self):
        info_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        info_frame.grid(row=1, column=0, sticky="ew", pady=5)

        # 정보 프레임 열 설정
        info_frame.columnconfigure(0, weight=1)

        self.data_info_label = tk.Label(info_frame, text="", bg=self.bg_color_2,
                                        font=self.main_app.label_font)
        self.data_info_label.grid(row=0, column=0, pady=5)

    def setup_scrollable_table(self):
        canvas_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        canvas_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # ── grid 기초 레이아웃 ────────────────────────────────────────
        # (0,0) canvas(확장), (0,1) vbar, (0,2) buttons
        # (1,0) hbar(가로),  (1,1) 코너(옵션), (1,2) 버튼 아래 빈칸
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.rowconfigure(1, weight=0, minsize=16)  # hbar 높이(보일 때)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.columnconfigure(1, weight=0, minsize=16)  # vbar 폭(보일 때)

        # Canvas 생성
        self.data_canvas = tk.Canvas(
            canvas_frame,
            bg=self.bg_color_2,
            highlightthickness=0, bd=0
        )
        vbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.data_canvas.yview)
        hbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.data_canvas.xview)
        self.data_canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        # 배치
        self.data_canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")

        self.scrollable_frame = ttk.Frame(self.data_canvas)
        self.data_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # ── 토글 유틸: 보이기/숨기기 + minsize 조정 + hbar columnspan 관리 ──
        def _show_vbar(show: bool):
            # 보일 때: vbar grid, column1 minsize=16
            # 숨김  때: vbar grid_remove, column1 minsize=0
            canvas_frame.columnconfigure(1, minsize=16)
            if show:
                vbar.grid()
            else:
                vbar.grid_remove()

        def _show_hbar(show: bool):
            # 보일 때: row1 minsize=16, hbar grid
            # 숨김  때: row1 minsize=0,  hbar grid_remove
            canvas_frame.rowconfigure(1, minsize=16)
            if show:
                hbar.grid()
            else:
                hbar.grid_remove()

        # ── 스크롤 영역/토글 갱신 ──
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

            # 항상 최신 scrollregion 유지
            self.data_canvas.configure(scrollregion=region)

        # 내용이 변할 때도 갱신해야 함 (scrollable_frame에 바인딩)
        self.scrollable_frame.bind("<Configure>", lambda e: update_scrollbars())
        # 창/캔버스 크기 변할 때도 갱신
        self.data_canvas.bind("<Configure>", lambda e: update_scrollbars())

        # 마우스 휠 스크롤 이벤트 바인딩 추가
        def _on_mousewheel(event):
            region = self.data_canvas.bbox("all")
            if region and region[3] > self.data_canvas.winfo_height():
                self.data_canvas.yview_scroll(int(-1 * (event.delta / self.main_app.scroll_num)), "units")

        def _on_shift_mousewheel(event):
            self.data_canvas.xview_scroll(int(-1 * (event.delta / self.main_app.scroll_num)), "units")

        self.data_canvas.bind("<Enter>", lambda e: self.data_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.data_canvas.bind("<Leave>", lambda e: self.data_canvas.unbind_all("<MouseWheel>"))
        self.data_canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)

        # 처음에도 한 번 계산
        canvas_frame.after(0, update_scrollbars)

    def setup_buttons(self):
        data_button_frame = tk.Frame(self.frame, bg=self.bg_color_2)
        data_button_frame.grid(row=2, column=0, sticky="", pady=10)  # sticky="" = 가운데 정렬

        # 버튼들을 grid로 배치
        btn_col = 0

        # Row 관련 버튼들
        add_btn = tk.Button(data_button_frame, text="   Add Row   ", command=self.add_data_row,
                            font=self.main_app.button_font)
        add_btn.grid(row=0, column=btn_col, padx=7, pady=2)
        btn_col += 1

        remove_btn = tk.Button(data_button_frame, text="Remove Last Row", command=self.remove_data_row,
                               font=self.main_app.button_font)
        remove_btn.grid(row=0, column=btn_col, padx=7, pady=2)
        btn_col += 1

        # 구분선
        separator = tk.Frame(data_button_frame, width=2, height=20, bg='gray')
        separator.grid(row=0, column=btn_col, padx=10, pady=2)
        btn_col += 1

        # File 관련 버튼들
        save_btn = tk.Button(data_button_frame, text="  Save File  ", command=self.save_file,
                            font=self.main_app.button_font)
        save_btn.grid(row=0, column=btn_col, padx=7, pady=2)
        btn_col += 1

        load_btn = tk.Button(data_button_frame, text="  Load File  ", command=self.load_file,
                             font=self.main_app.button_font)
        load_btn.grid(row=0, column=btn_col, padx=7, pady=2)
        btn_col += 1

        # 구분선
        separator2 = tk.Frame(data_button_frame, width=2, height=20, bg='gray')
        separator2.grid(row=0, column=btn_col, padx=10, pady=2)
        btn_col += 1

        # Reset 버튼
        reset_btn = tk.Button(data_button_frame, text="    Reset    ", command=self.clear_data,
                              font=self.main_app.button_font)
        reset_btn.grid(row=0, column=btn_col, padx=7, pady=2)

    def create_data_table(self):
        global MAX_DATA_ROWS

        # 기존 테이블 제거
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        num_vars = self.main_app.var_count_var.get()

        # 파라미터 이름을 가져와서 헤더로 사용
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

        # Y 컬럼 이름 추가
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
            headers.append("Y")  # 이름까지 비어 있으면 기본값)

        # 각 컬럼의 너비 계산
        entry_widths = [self.calculate_entry_width(header) for header in headers]

        # "Data" 헤더 라벨 (첫 번째 컬럼)
        data_header_label = tk.Label(self.scrollable_frame, text=" ",
                                     font=self.main_app.label_font, bg=self.bg_color_2)
        data_header_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # 파라미터 헤더 레이블들을 저장
        self.data_headers = []
        for j, header in enumerate(headers):
            label = tk.Label(self.scrollable_frame, text=header,
                             font=self.main_app.label_font, bg=self.bg_color_2)
            label.grid(row=0, column=j + 1, padx=5, pady=5, sticky="ew")
            self.data_headers.append(label)

        # 데이터 행들 생성
        self.data_entries = []
        for i in range(MAX_DATA_ROWS):
            row_entries = []

            # 왼쪽에 Data 번호 라벨 추가
            data_label = tk.Label(self.scrollable_frame, text=f"Data {i + 1}",
                                  font=self.main_app.label_font, bg=self.bg_color_2)
            data_label.grid(row=i + 1, column=0, padx=2, pady=1)

            # 각 파라미터와 Y값에 대한 Entry 생성
            for j in range(num_vars + 1):
                entry = tk.Entry(self.scrollable_frame, width=entry_widths[j],
                                 font=self.main_app.button_font, justify="center")
                entry.grid(row=i + 1, column=j + 1, padx=2, pady=1)
                row_entries.append(entry)

            self.data_entries.append(row_entries)

    def calculate_entry_width(self, text):
        """텍스트 길이에 따라 Entry 위젯의 적절한 너비를 계산"""
        min_width = 8
        max_width = 20
        return max(min_width, min(max_width, len(text) + 3))

    def update_data_headers(self):
        """데이터 탭의 헤더만 업데이트"""
        if not hasattr(self.main_app, 'param_tab'):
            return

        num_vars = self.main_app.var_count_var.get()

        # 새로운 헤더 이름들 가져오기 (단위 포함)
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

        # Y 컬럼 이름 추가 (단위 포함)
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

        # 파라미터 이름을 가져와서 표시 (단위 포함)
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
        """사용자가 수동으로 행을 추가할 때"""
        self.add_single_row()

    def remove_data_row(self):
        global MAX_DATA_ROWS
        if MAX_DATA_ROWS > 1 and len(self.data_entries) > 0:
            # 마지막 행의 위젯들 제거
            last_row_idx = len(self.data_entries) - 1

            # 마지막 행의 모든 위젯 찾아서 삭제
            for widget in self.scrollable_frame.grid_slaves(row=last_row_idx + 1):
                widget.destroy()

            # data_entries에서 마지막 행 제거
            self.data_entries.pop()

            MAX_DATA_ROWS -= 1

            # 스크롤 영역 업데이트
            self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all"))

    def clear_data(self, with_warning=True):
        if with_warning:
            # 확인 문구 표시
            result = messagebox.askyesno(
                "Reset Confirmation",
                "Are you sure you want to reset all data?\n\nThis will:\n• Reset all data\n\nThis action cannot be undone."
            )

            if not result:  # 사용자가 'No' 또는 창을 닫은 경우
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

            # 파일 확장자에 따라 다른 방식으로 읽기
            file_ext = filename.lower().split('.')[-1]

            if file_ext in ['xlsx', 'xls']:
                # Excel 파일 읽기
                try:
                    # 첫 번째 시트 읽기
                    df = pd.read_excel(filename, sheet_name=0)
                except Exception as e:
                    # 여러 시트가 있는 경우 사용자에게 선택하도록 할 수도 있음
                    messagebox.showerror("Excel Read Error", f"An error occurred while reading the Excel file:\n{str(e)}")
                    return


            elif file_ext in ['csv', 'txt', 'tsv']:
                # CSV / TXT / TSV : 인코딩 자동 시도 + 구분자 자동 감지
                encodings_to_try = ['utf-8', 'euc-kr', 'cp949', 'latin1']
                df = None
                for enc in encodings_to_try:
                    try:
                        # sep=None + engine='python' → 쉼표/탭/세미콜론 등 자동 감지
                        df = pd.read_csv(filename, sep=None, engine='python', encoding=enc)
                        # print(f"Loaded with encoding: {enc}")  # 필요시 로그
                        break
                    except (UnicodeDecodeError, AttributeError, ValueError):
                        continue
                    except Exception:
                        # 구분자 자동 감지가 애매한 경우를 대비해 공백 구분 시도
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

            # 데이터가 비어있는지 확인
            if df.empty:
                messagebox.showwarning("Empty File", "The file contains no data.")
                return

            new_headers = list(df.columns)  # 파일 컬럼 헤더들
            file_var_count = max(0, len(new_headers) - 1)  # Y 제외 X 개수
            num_vars = self.main_app.var_count_var.get()

            # ─────────────────────────────────────────────────────────
            # 1) (가장 먼저) 변수 개수 불일치 처리 → 구조부터 확정
            # ─────────────────────────────────────────────────────────
            num_vars = self.main_app.var_count_var.get()
            if file_var_count != num_vars:
                if messagebox.askyesno(
                        "Adjust Variable Count",
                        f"The number of variables in the file ({file_var_count}) does not match the current setting ({num_vars}).\n"
                        f"Do you want to adjust the variable count to {file_var_count}?"
                ):
                    self.main_app.var_count_var.set(file_var_count)
                    # 변수 개수가 바뀌었으므로 모든 테이블 구조를 새로고침
                    self.main_app.param_tab.create_param_table()
                    self.preserve_and_rebuild_table()
                    self.update_data_info()

            # 최신 변수 개수를 다시 가져옴
            current_num_vars = self.main_app.var_count_var.get()

            # ─────────────────────────────────────────────────────────
            # 2) (구조 확정 후) 헤더 교체 여부 처리 → 내용 채우기
            # ─────────────────────────────────────────────────────────
            if messagebox.askyesno(
                    "Header Detected",
                    "A header row has been detected.\nDo you want to replace the existing parameter names with this header?"
            ):
                # Y 이름/단위 (항상 마지막 열)
                if len(new_headers) > 0:
                    y_full = new_headers[-1]
                    y_match = re.match(r"(.*?)\s*\((.*?)\)", y_full)
                    if y_match:
                        y_name, y_unit = y_match.group(1).strip(), y_match.group(2).strip()
                    # ... (기존 Y 이름 파싱 로직과 동일) ...
                    else:
                        y_name, y_unit = y_full.strip(), ""
                    self.main_app.param_tab.y_name_entry.delete(0, tk.END)
                    self.main_app.param_tab.y_name_entry.insert(0, y_name)
                    self.main_app.param_tab.y_unit_entry.delete(0, tk.END)
                    self.main_app.param_tab.y_unit_entry.insert(0, y_unit)

                # X 이름/단위 (현재 변수 개수만큼 정확히 반영)
                for i in range(min(current_num_vars, len(new_headers) - 1)):
                    header = new_headers[i]
                    m = re.match(r"(.*?)\s*\((.*?)\)", header)
                    if m:
                        name, unit = m.group(1).strip(), m.group(2).strip()
                    # ... (기존 X 이름 파싱 로직과 동일) ...
                    else:
                        name, unit = header.strip(), ""
                    if i < len(self.main_app.param_tab.param_entries):
                        self.main_app.param_tab.param_entries[i][0].delete(0, tk.END)
                        self.main_app.param_tab.param_entries[i][0].insert(0, name)
                        self.main_app.param_tab.param_entries[i][1].delete(0, tk.END)
                        self.main_app.param_tab.param_entries[i][1].insert(0, unit)

                # 헤더를 바꿨으니 표시 갱신
                self.update_data_headers()
                self.update_data_info()

            # ─────────────────────────────────────────────────────────
            # 3) (공통) 행 개수 확보 + 기존 데이터 클리어 + 데이터 삽입
            # ─────────────────────────────────────────────────────────
            required_rows = len(df)
            while len(self.data_entries) < required_rows:
                self.add_single_row()

            self.clear_data(with_warning=False)

            # 데이터 삽입 (최신 변수 개수 기준)
            for i, row in df.iterrows():
                if i < len(self.data_entries):
                    # X 값 입력 (앞쪽 current_num_vars 개)
                    for j in range(min(current_num_vars, len(row) - 1)):
                        value = row.iloc[j]
                        self.data_entries[i][j].insert(0, "" if pd.isna(value) else str(value))

                    # Y 값 입력 (항상 마지막 컬럼)
                    y_value = row.iloc[-1]
                    # Y값이 들어갈 Entry의 인덱스는 current_num_vars
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

            # 🔁 안전한 기호로 정규화 (℃→°C, ℉→°F 등)
            df_to_save = data.copy()
            try:
                for col in df_to_save.columns:
                    if df_to_save[col].dtype == "object":
                        s = df_to_save[col].astype(str)
                        s = s.str.replace("\u2103", "°C", regex=False)  # ℃ → °C
                        s = s.str.replace("\u2109", "°F", regex=False)  # ℉ → °F
                        df_to_save[col] = s
            except Exception:
                pass  # 문자열 변환 중 문제 있으면 그냥 무시하고 진행

            file_ext = filename.lower().split('.')[-1]

            if file_ext in ('xlsx', 'xls'):
                # Excel은 유니코드 안전함 (openpyxl가 처리)
                try:
                    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                        df_to_save.to_excel(writer, sheet_name='Data', index=False)

                        # (선택) 헤더 스타일 + 자동열폭
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
                # ✅ UTF-8 with BOM로 저장 → 엑셀/메모장 호환 좋음
                df_to_save.to_csv(filename, sep='\t', index=False, encoding='utf-8-sig')

            elif file_ext == 'csv':
                # ✅ UTF-8 with BOM
                df_to_save.to_csv(filename, index=False, encoding='utf-8-sig')

            else:
                # 확장자 모호하면 CSV로 저장 (UTF-8 BOM)
                if not filename.lower().endswith('.csv'):
                    filename = filename + ".csv"
                df_to_save.to_csv(filename, index=False, encoding='utf-8-sig')

            messagebox.showinfo("Save Complete", f"Data has been saved to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving the file:\n{str(e)}")

    def extract_data_only(self):
        """데이터만 추출"""
        try:
            if not hasattr(self.main_app, 'param_tab'):
                return pd.DataFrame()

            num_vars = self.main_app.var_count_var.get()

            # 파라미터 이름을 가져와서 사용 (단위 포함)
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
                    if val:  # 값이 비어있지 않으면
                        try:
                            row.append(float(val))
                        except ValueError:
                            # 숫자로 변환할 수 없는 값이면 NaN 처리
                            row.append(np.nan)
                    else:  # 값이 비어있으면
                        row.append(np.nan)  # NaN(Not a Number)으로 추가

                if len(row) == num_vars + 1:
                    rows.append(row)
                elif len(row) > 0:
                    break

            if rows:
                # Y 컬럼 이름도 단위 포함
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

    # _data_tab.py에 추가
    def add_suggested_points(self, points, param_info):
        """추천된 포인트들을 데이터 테이블 맨 뒤에 추가"""
        global MAX_DATA_ROWS

        # 현재 데이터가 있는 마지막 행 찾기
        last_row_with_data = -1
        for i, row_entries in enumerate(self.data_entries):
            has_data = any(entry.get().strip() for entry in row_entries)
            if has_data:
                last_row_with_data = i

        start_row = last_row_with_data + 1
        needed_rows = start_row + len(points)

        # 필요한 만큼 행 자동 추가
        while len(self.data_entries) < needed_rows:
            self.add_single_row()  # 새로운 헬퍼 함수

        # 포인트들 추가
        for i, point in enumerate(points):
            row_idx = start_row + i
            if row_idx < len(self.data_entries):
                for j, value in enumerate(point):
                    if j < len(self.data_entries[row_idx]):
                        # 기존 값이 있으면 지우고 새 값 입력
                        self.data_entries[row_idx][j].delete(0, tk.END)
                        self.data_entries[row_idx][j].insert(0, str(value))

        messagebox.showinfo("Points Added", f"{len(points)} recommended points have been added to the data table.")

    def add_single_row(self):
        """단일 행을 동적으로 추가하는 헬퍼 함수"""
        global MAX_DATA_ROWS

        num_vars = self.main_app.var_count_var.get()

        # 헤더 정보 가져오기
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

        # Y 컬럼 이름 추가
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

        # 새 행 추가
        new_row_idx = len(self.data_entries)
        row_entries = []

        # 행 번호 라벨
        data_label = tk.Label(self.scrollable_frame, text=f"Data {new_row_idx + 1}",
                              font=self.main_app.label_font, bg=self.bg_color_2)
        data_label.grid(row=new_row_idx + 1, column=0, padx=2, pady=1)

        # Entry 위젯들 추가
        for j in range(num_vars + 1):
            entry = tk.Entry(self.scrollable_frame, width=entry_widths[j],
                             font=self.main_app.button_font, justify="center")
            entry.grid(row=new_row_idx + 1, column=j + 1, padx=2, pady=1)
            row_entries.append(entry)

        self.data_entries.append(row_entries)
        MAX_DATA_ROWS += 1

        # 스크롤 영역 업데이트
        self.scrollable_frame.update_idletasks()
        self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all"))

    # _data_tab.py에 추가할 함수들

    def remove_last_parameter_column(self):
        """마지막 파라미터 컬럼만 제거 (Y 컬럼은 유지)"""
        # 현재 데이터 백업
        current_data = []
        for row_entries in self.data_entries:
            row_data = []
            # Y값 앞까지의 파라미터들 (마지막 파라미터 제외)
            for j in range(len(row_entries) - 2):  # 마지막에서 2번째까지 (제거할 파라미터 제외)
                row_data.append(row_entries[j].get())
            # Y 컬럼 값 추가 (항상 마지막)
            if len(row_entries) > 0:
                row_data.append(row_entries[-1].get())  # Y 컬럼
            current_data.append(row_data)

        # 테이블 재생성
        self.create_data_table()

        # 데이터 복원
        num_vars = self.main_app.var_count_var.get()
        for i, row_data in enumerate(current_data):
            if i < len(self.data_entries):
                # 파라미터들 복원
                for j in range(len(row_data) - 1):  # Y값 제외한 파라미터들
                    if j < len(self.data_entries[i]):
                        self.data_entries[i][j].insert(0, row_data[j])
                # Y 값 복원 (항상 마지막 컬럼)
                if len(row_data) > 0 and len(self.data_entries[i]) > num_vars:
                    self.data_entries[i][num_vars].insert(0, row_data[-1])

    def preserve_and_rebuild_table(self):
        """기존 데이터를 보존하면서 테이블을 재생성 (파라미터 추가 시 Y값 앞에 빈 컬럼 삽입)"""
        # 현재 데이터 백업
        current_data = []
        for row_entries in self.data_entries:
            row_data = [entry.get() for entry in row_entries]
            current_data.append(row_data)

        # 테이블 재생성
        self.create_data_table()

        # 데이터 복원
        old_num_vars = len(current_data[0]) - 1 if current_data and current_data[0] else 0  # Y 제외한 이전 파라미터 개수
        new_num_vars = self.main_app.var_count_var.get()

        for i, row_data in enumerate(current_data):
            if i < len(self.data_entries) and row_data:
                # 기존 파라미터들 복원
                for j in range(min(old_num_vars, new_num_vars)):
                    if j < len(self.data_entries[i]):
                        self.data_entries[i][j].insert(0, row_data[j])

                # Y값 복원 (항상 마지막 컬럼)
                if len(row_data) > old_num_vars and new_num_vars < len(self.data_entries[i]):
                    self.data_entries[i][new_num_vars].insert(0, row_data[-1])

                # 새로 추가된 파라미터 컬럼들은 자동으로 빈칸으로 남음