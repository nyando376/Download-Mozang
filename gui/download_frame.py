"""
다운로드 상태 프레임
"""
import customtkinter as ctk
from utils.logger import logger


class DownloadItem(ctk.CTkFrame):
    """개별 다운로드 항목"""

    def __init__(self, master, task, on_cancel=None, on_remove=None):
        super().__init__(master)

        self.task = task
        self.on_cancel = on_cancel
        self.on_remove = on_remove

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        # 제목 및 버튼 프레임
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(padx=10, pady=(10, 5), fill="x")

        # 제목
        title_text = self.task.title[:30] + "..." if len(self.task.title) > 30 else self.task.title
        self.title_label = ctk.CTkLabel(
            title_frame,
            text=title_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True)

        # 버튼 프레임
        button_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        button_frame.pack(side="right")

        # 중지 버튼
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="⏸",
            width=30,
            height=25,
            command=self._on_cancel_click,
            fg_color="orange",
            hover_color="darkorange"
        )
        self.cancel_button.pack(side="left", padx=2)

        # 삭제 버튼
        self.remove_button = ctk.CTkButton(
            button_frame,
            text="✕",
            width=30,
            height=25,
            command=self._on_remove_click,
            fg_color="red",
            hover_color="darkred"
        )
        self.remove_button.pack(side="left", padx=2)

        # 진행률 바
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(padx=10, pady=5, fill="x")
        self.progress_bar.set(0)

        # 상태 텍스트
        self.status_label = ctk.CTkLabel(
            self,
            text=f"상태: {self.task.status}",
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        self.status_label.pack(padx=10, pady=(5, 10), fill="x")

    def _on_cancel_click(self):
        """중지 버튼 클릭"""
        if self.on_cancel:
            self.on_cancel(self.task)

    def _on_remove_click(self):
        """삭제 버튼 클릭"""
        if self.on_remove:
            self.on_remove(self.task)

    def update(self, task):
        """작업 상태 업데이트"""
        self.task = task

        # 진행률 바 업데이트
        progress = task.progress / 100.0
        self.progress_bar.set(progress)

        # 상태 텍스트 업데이트
        if task.status == 'downloading':
            status_text = f"다운로드 중: {task.progress:.1f}% | 속도: {task.speed} | 남은 시간: {task.eta}"
            self.cancel_button.configure(state="normal")  # 중지 버튼 활성화
        elif task.status == 'completed':
            status_text = "완료"
            self.cancel_button.configure(state="disabled")  # 중지 버튼 비활성화
        elif task.status == 'cancelled':
            status_text = "중지됨"
            self.cancel_button.configure(state="disabled")
        elif task.status == 'failed':
            status_text = f"실패: {task.error_message}"
            self.cancel_button.configure(state="disabled")
        else:
            status_text = f"상태: {task.status}"

        self.status_label.configure(text=status_text)


class DownloadFrame(ctk.CTkScrollableFrame):
    """다운로드 프레임 클래스"""

    def __init__(self, master, on_cancel=None, on_remove=None, **kwargs):
        super().__init__(master, **kwargs)

        self.download_items = {}  # vod_url -> DownloadItem
        self.on_cancel = on_cancel
        self.on_remove = on_remove

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        # 제목
        title_label = ctk.CTkLabel(
            self,
            text="다운로드 상태",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(padx=10, pady=10)

        # 초기 메시지
        self.empty_label = ctk.CTkLabel(
            self,
            text="다운로드 중인 항목이 없습니다.",
            font=ctk.CTkFont(size=12)
        )
        self.empty_label.pack(pady=20)

    def add_task(self, task):
        """다운로드 작업 추가"""
        # 빈 메시지 제거
        if self.empty_label:
            self.empty_label.destroy()
            self.empty_label = None

        # 다운로드 항목 생성
        download_item = DownloadItem(
            self, task,
            on_cancel=self.on_cancel,
            on_remove=self._on_remove_item
        )
        download_item.pack(fill="x", padx=5, pady=5)

        self.download_items[task.vod_url] = download_item

        logger.info(f"다운로드 항목 추가: {task.title}")

    def _on_remove_item(self, task):
        """항목 제거 (UI에서)"""
        if self.on_remove:
            self.on_remove(task)

        # UI에서 제거
        if task.vod_url in self.download_items:
            item = self.download_items[task.vod_url]
            item.destroy()
            del self.download_items[task.vod_url]

        # 항목이 없으면 빈 메시지 표시
        if not self.download_items and not self.empty_label:
            self.empty_label = ctk.CTkLabel(
                self,
                text="다운로드 중인 항목이 없습니다.",
                font=ctk.CTkFont(size=12)
            )
            self.empty_label.pack(pady=20)

    def update_task(self, task):
        """다운로드 작업 업데이트"""
        if task.vod_url in self.download_items:
            self.download_items[task.vod_url].update(task)
