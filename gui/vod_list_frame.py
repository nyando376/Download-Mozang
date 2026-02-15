"""
VOD 목록 프레임
"""
import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
from utils.logger import logger


class VODItem(ctk.CTkFrame):
    """개별 VOD 항목"""

    def __init__(self, master, vod_info, download_callback):
        super().__init__(master)

        self.vod_info = vod_info
        self.download_callback = download_callback

        self._setup_ui()

    def _setup_ui(self):
        """UI 구성"""
        self.grid_columnconfigure(1, weight=1)

        # 썸네일 (나중에 로드)
        self.thumbnail_label = ctk.CTkLabel(self, text="", width=160, height=90)
        self.thumbnail_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

        # 썸네일 로드 (백그라운드)
        thumbnail_url = self.vod_info.get('thumbnailImageUrl', '')
        if thumbnail_url:
            threading.Thread(
                target=self._load_thumbnail,
                args=(thumbnail_url,),
                daemon=True
            ).start()

        # 제목
        title = self.vod_info.get('videoTitle', 'Unknown')
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="w")

        # 정보 (길이, 날짜)
        duration = self._format_duration(self.vod_info.get('duration', 0))
        publish_date = self.vod_info.get('publishDate', '')[:10]  # YYYY-MM-DD
        info_text = f"길이: {duration} | 업로드: {publish_date}"

        info_label = ctk.CTkLabel(
            self,
            text=info_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        info_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # 다운로드 버튼
        download_button = ctk.CTkButton(
            self,
            text="다운로드",
            command=self._on_download_click,
            width=100
        )
        download_button.grid(row=0, column=2, rowspan=2, padx=10, pady=10)

    def _load_thumbnail(self, url):
        """썸네일 이미지 로드"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img = img.resize((160, 90), Image.Resampling.LANCZOS)

                # UI 업데이트 (메인 스레드)
                self.after(0, lambda: self._set_thumbnail(img))

        except Exception as e:
            logger.error(f"썸네일 로드 실패: {e}")

    def _set_thumbnail(self, img):
        """썸네일 설정"""
        try:
            photo = ImageTk.PhotoImage(img)
            self.thumbnail_label.configure(image=photo, text="")
            self.thumbnail_label.image = photo  # 참조 유지
        except Exception as e:
            logger.error(f"썸네일 설정 실패: {e}")

    def _format_duration(self, seconds):
        """초를 시:분:초 형식으로 변환"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

    def _on_download_click(self):
        """다운로드 버튼 클릭"""
        if self.download_callback:
            self.download_callback(self.vod_info)


class VODListFrame(ctk.CTkScrollableFrame):
    """VOD 목록 프레임"""

    def __init__(self, master, download_callback):
        super().__init__(master)

        self.download_callback = download_callback
        self.vod_items = []

        # 초기 메시지
        self.empty_label = ctk.CTkLabel(
            self,
            text="채널 URL을 입력하고 'VOD 목록 로드'를 클릭하세요.",
            font=ctk.CTkFont(size=14)
        )
        self.empty_label.pack(pady=50)

    def display_vods(self, vod_list):
        """VOD 목록 표시"""
        # 기존 항목 제거
        self.clear()

        if not vod_list:
            self.empty_label = ctk.CTkLabel(
                self,
                text="VOD가 없습니다.",
                font=ctk.CTkFont(size=14)
            )
            self.empty_label.pack(pady=50)
            return

        # VOD 항목 생성
        for vod_info in vod_list:
            vod_item = VODItem(self, vod_info, self.download_callback)
            vod_item.pack(fill="x", padx=10, pady=5)
            self.vod_items.append(vod_item)

        logger.info(f"VOD 목록 표시 완료: {len(vod_list)}개")

    def clear(self):
        """모든 항목 제거"""
        for widget in self.winfo_children():
            widget.destroy()
        self.vod_items.clear()
