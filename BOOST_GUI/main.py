import platform
import tkinter as tk
from tkinter import ttk

from _config import ConfigManager
from _data_tab import DataTab
from _parameter_tab import ParameterTab
from _result_tab import ResultTab


class BOMainApp:
    """메인 애플리케이션 클래스"""

    def __init__(self, root):
        self.root = root
        self.root.title("BOOST GUI (Alpha Version)")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)

        # 스타일 설정
        self.bg_color_1 = "#F3F3F3"
        self.bg_color_2 = "#ECEAE5"
        self.setup_styles()
        self.num_vars = 4


        self.button_font = ("Arial", 11)
        self.label_font = ("Arial", 11, "bold")

        # 변수 초기화
        self.var_count_var = tk.IntVar(value=self.num_vars)

        # 설정 매니저 생성
        self.config_manager = ConfigManager()

        # 노트북 위젯 생성
        self.notebook = ttk.Notebook(root, takefocus=False)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 각 탭 생성
        self.setup_tabs()

        # 초기 설정 로드
        self.load_initial_config()
        self.scroll_num = 1 if platform.system() == "Darwin" else 120
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def setup_styles(self):
        """스타일 설정"""
        self.root.configure(bg=self.bg_color_1)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.bg_color_2)
        style.configure("TNotebook", background=self.bg_color_1)
        style.configure("TNotebook.Tab", background=self.bg_color_2)
        style.configure("TLabel", background=self.bg_color_2)
        style.configure("TButton", background=self.bg_color_2)

    def setup_tabs(self):
        """각 탭 생성"""
        self.param_tab = ParameterTab(self.notebook, self)
        self.data_tab = DataTab(self.notebook, self)
        self.result_tab = ResultTab(self.notebook, self)

    def load_initial_config(self):
        self.data_tab.update_data_info()

    def on_tab_changed(self, event):
        """탭이 변경될 때 호출되어 모든 탭의 초기 포커스를 해제"""
        try:
            # 현재 선택된 탭의 프레임 위젯 경로를 가져옵니다.
            selected_frame_path = self.notebook.select()

            # 위젯 경로가 비어있지 않다면, 실제 위젯 객체로 변환합니다.
            if selected_frame_path:
                selected_frame = self.root.nametowidget(selected_frame_path)

                # 해당 프레임에 포커스를 주어, 내부 입력창들의 자동 포커싱을 막습니다.
                selected_frame.focus_set()
        except tk.TclError:
            # 프로그램 시작 시 간혹 위젯이 완전히 생성되지 않았을 때 오류가 날 수 있어 예외 처리
            pass



if __name__ == "__main__":
    root = tk.Tk()
    app = BOMainApp(root)
    root.mainloop()