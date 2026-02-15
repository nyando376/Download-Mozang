"""
업데이트 알림 다이얼로그
"""
import customtkinter as ctk
import webbrowser
from utils.logger import logger


class UpdateDialog(ctk.CTkToplevel):
    """업데이트 알림 다이얼로그"""

    def __init__(self, parent, latest_version, download_url, release_notes):
        super().__init__(parent)

        self.latest_version = latest_version
        self.download_url = download_url
        self.release_notes = release_notes

        # 윈도우 설정
        self.title("업데이트 알림")
        self.geometry("500x400")
        self.resizable(False, False)

        # 모달 윈도우로 설정
        self.transient(parent)
        self.grab_set()

        # 중앙 정렬
        self.center_window()

        # UI 구성
        self._setup_ui()

    def center_window(self):
        """윈도우를 화면 중앙에 배치"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 아이콘/제목
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎉 새로운 업데이트가 있습니다!",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # 버전 정보
        version_label = ctk.CTkLabel(
            main_frame,
            text=f"최신 버전: v{self.latest_version}",
            font=ctk.CTkFont(size=16)
        )
        version_label.pack(pady=(0, 20))

        # 릴리즈 노트 (있는 경우)
        if self.release_notes:
            notes_label = ctk.CTkLabel(
                main_frame,
                text="업데이트 내용:",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            notes_label.pack(pady=(0, 5))

            # 릴리즈 노트 텍스트박스
            notes_textbox = ctk.CTkTextbox(
                main_frame,
                height=150,
                wrap="word"
            )
            notes_textbox.pack(fill="both", expand=True, pady=(0, 20))
            notes_textbox.insert("1.0", self.release_notes)
            notes_textbox.configure(state="disabled")

        # 버튼 프레임
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        # 다운로드 버튼
        download_button = ctk.CTkButton(
            button_frame,
            text="지금 다운로드",
            command=self._on_download,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        download_button.pack(side="left", padx=(0, 10), expand=True)

        # 나중에 버튼
        later_button = ctk.CTkButton(
            button_frame,
            text="나중에",
            command=self._on_later,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray",
            hover_color="darkgray"
        )
        later_button.pack(side="left", expand=True)

    def _on_download(self):
        """다운로드 버튼 클릭"""
        if self.download_url:
            logger.info(f"업데이트 다운로드 페이지 열기: {self.download_url}")
            webbrowser.open(self.download_url)
        self.destroy()

    def _on_later(self):
        """나중에 버튼 클릭"""
        logger.info("업데이트 나중에 하기")
        self.destroy()
