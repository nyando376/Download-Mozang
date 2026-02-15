"""
검색 프레임
"""
import customtkinter as ctk
from utils.logger import logger


class SearchFrame(ctk.CTkFrame):
    """검색 프레임 클래스"""

    def __init__(self, master, search_callback):
        super().__init__(master)

        self.search_callback = search_callback

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        self.grid_columnconfigure(1, weight=1)

        # 검색 라벨
        search_label = ctk.CTkLabel(
            self,
            text="검색:",
            font=ctk.CTkFont(size=14)
        )
        search_label.grid(row=0, column=0, padx=(10, 5), pady=10)

        # 검색 입력 필드
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="VOD 제목 검색..."
        )
        self.search_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.search_entry.bind("<Return>", self._on_search)

        # 검색 버튼
        search_button = ctk.CTkButton(
            self,
            text="검색",
            command=self._on_search,
            width=80
        )
        search_button.grid(row=0, column=2, padx=(5, 10), pady=10)

    def _on_search(self, event=None):
        """검색 실행"""
        keyword = self.search_entry.get().strip()

        if not keyword:
            logger.warning("검색어가 비어있습니다")
            return

        if self.search_callback:
            self.search_callback(keyword)
