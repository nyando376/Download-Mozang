"""
메인 윈도우
CustomTkinter를 사용한 GUI
"""
import customtkinter as ctk
from core.config_manager import ConfigManager
from core.chzzk_api import ChzzkAPI
from core.downloader import Downloader
from gui.vod_list_frame import VODListFrame
from gui.search_frame import SearchFrame
from gui.download_frame import DownloadFrame
from gui.update_dialog import UpdateDialog
from utils.logger import logger
from utils.validators import validate_chzzk_url
from utils.version_checker import VersionChecker, get_current_version


class MainWindow(ctk.CTk):
    """메인 윈도우 클래스"""

    def __init__(self):
        super().__init__()

        # 설정 로드
        self.config_manager = ConfigManager()
        self.api = ChzzkAPI()
        self.downloader = Downloader(
            max_concurrent=self.config_manager.get('max_concurrent_downloads', 3)
        )

        # 윈도우 설정
        self.title(f"사모장 치지직 다시보기 다운로더 v{get_current_version()}")
        self.geometry("1200x700")

        # 테마 설정
        theme = self.config_manager.get('theme', 'dark')
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")

        # UI 초기화
        self._setup_ui()

        # 다운로더 시작
        self.downloader.start()
        self.downloader.add_progress_callback(self._on_download_progress)

        # 다운로드 디렉토리 확인
        self.config_manager.ensure_download_path()

        logger.info("메인 윈도우 초기화 완료")

        # 버전 체크 (백그라운드)
        self._check_for_updates()

        # 자동으로 VOD 목록 로드
        self._auto_load_vod_list()

    def _setup_ui(self):
        """UI 구성"""
        # 그리드 설정
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 좌측 사이드바
        self._create_sidebar()

        # 중앙 영역 (탭뷰)
        self._create_main_area()

        # 우측 영역 (다운로드 상태)
        self._create_download_panel()

    def _create_sidebar(self):
        """좌측 사이드바 생성"""
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sidebar.grid_rowconfigure(10, weight=1)

        # 로고/제목
        title_label = ctk.CTkLabel(
            sidebar,
            text="치지직\n다운로더",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 채널 URL 입력
        url_label = ctk.CTkLabel(sidebar, text="채널 URL:")
        url_label.grid(row=1, column=0, padx=20, pady=(10, 0))

        self.channel_url_entry = ctk.CTkEntry(
            sidebar,
            placeholder_text="https://chzzk.naver.com/...",
            state="disabled"  # 읽기 전용으로 설정
        )
        self.channel_url_entry.grid(row=2, column=0, padx=20, pady=(5, 0))

        # 저장된 URL 로드
        saved_url = self.config_manager.get('channel_url', '')
        if saved_url:
            self.channel_url_entry.configure(state="normal")  # 임시로 활성화
            self.channel_url_entry.insert(0, saved_url)
            self.channel_url_entry.configure(state="disabled")  # 다시 비활성화

        # 로드 버튼
        load_button = ctk.CTkButton(
            sidebar,
            text="VOD 목록 로드",
            command=self._load_vod_list
        )
        load_button.grid(row=3, column=0, padx=20, pady=10)

        # 설정
        settings_label = ctk.CTkLabel(
            sidebar,
            text="설정",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_label.grid(row=4, column=0, padx=20, pady=(20, 10))

        # 화질 선택
        quality_label = ctk.CTkLabel(sidebar, text="기본 화질:")
        quality_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.quality_var = ctk.StringVar(
            value=self.config_manager.get('default_quality', 'best')
        )
        quality_menu = ctk.CTkOptionMenu(
            sidebar,
            variable=self.quality_var,
            values=['best', '1080p', '720p', '480p', '360p'],
            command=self._on_quality_change
        )
        quality_menu.grid(row=6, column=0, padx=20, pady=(5, 10))

        # 테마 전환
        theme_label = ctk.CTkLabel(sidebar, text="테마:")
        theme_label.grid(row=7, column=0, padx=20, pady=(10, 0))

        self.theme_var = ctk.StringVar(
            value=self.config_manager.get('theme', 'dark')
        )
        theme_menu = ctk.CTkOptionMenu(
            sidebar,
            variable=self.theme_var,
            values=['dark', 'light', 'system'],
            command=self._on_theme_change
        )
        theme_menu.grid(row=8, column=0, padx=20, pady=(5, 10))

    def _create_main_area(self):
        """중앙 영역 생성"""
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # 검색 프레임
        self.search_frame = SearchFrame(main_frame, self._on_search)
        self.search_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        # VOD 목록 프레임
        self.vod_list_frame = VODListFrame(main_frame, self._on_download_click)
        self.vod_list_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")

    def _create_download_panel(self):
        """우측 다운로드 패널 생성"""
        self.download_frame = DownloadFrame(
            self,
            width=300,
            on_cancel=self._on_cancel_download,
            on_remove=self._on_remove_download
        )
        self.download_frame.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="nsew")

    def _auto_load_vod_list(self):
        """자동 VOD 목록 로드 (초기화 시)"""
        saved_url = self.config_manager.get('channel_url', '')
        if saved_url:
            from utils.validators import extract_channel_id
            channel_id = extract_channel_id(saved_url)
            if channel_id:
                logger.info(f"자동 VOD 목록 로드 시작: {channel_id}")
                import threading
                thread = threading.Thread(
                    target=self._load_vod_list_thread,
                    args=(channel_id,),
                    daemon=True
                )
                thread.start()

    def _load_vod_list(self):
        """VOD 목록 로드"""
        url = self.channel_url_entry.get().strip()

        # URL 검증
        is_valid, message = validate_chzzk_url(url)
        if not is_valid:
            self._show_error("URL 오류", message)
            return

        # URL 저장
        self.config_manager.set('channel_url', url)

        # 채널 ID 추출
        from utils.validators import extract_channel_id
        channel_id = extract_channel_id(url)

        if not channel_id:
            self._show_error("오류", "채널 ID를 추출할 수 없습니다.")
            return

        logger.info(f"VOD 목록 로드 시작: {channel_id}")

        # 백그라운드에서 로드
        import threading
        thread = threading.Thread(
            target=self._load_vod_list_thread,
            args=(channel_id,),
            daemon=True
        )
        thread.start()

    def _load_vod_list_thread(self, channel_id):
        """VOD 목록 로드 (백그라운드 스레드)"""
        try:
            # VOD 목록 가져오기
            vod_list = self.api.get_vod_list(channel_id, page=0, size=50)

            # UI 업데이트 (메인 스레드에서)
            self.after(0, lambda: self.vod_list_frame.display_vods(vod_list))

        except Exception as e:
            logger.error(f"VOD 목록 로드 오류: {e}")
            self.after(0, lambda: self._show_error("로드 오류", str(e)))

    def _on_search(self, keyword):
        """검색 콜백"""
        url = self.channel_url_entry.get().strip()
        from utils.validators import extract_channel_id
        channel_id = extract_channel_id(url)

        if not channel_id:
            self._show_error("오류", "채널 URL을 먼저 입력하세요.")
            return

        logger.info(f"검색: {keyword}")

        # 백그라운드에서 검색
        import threading
        thread = threading.Thread(
            target=self._search_vods_thread,
            args=(channel_id, keyword),
            daemon=True
        )
        thread.start()

    def _search_vods_thread(self, channel_id, keyword):
        """VOD 검색 (백그라운드 스레드)"""
        try:
            results = self.api.search_vods(channel_id, keyword)
            self.after(0, lambda: self.vod_list_frame.display_vods(results))
        except Exception as e:
            logger.error(f"검색 오류: {e}")
            self.after(0, lambda: self._show_error("검색 오류", str(e)))

    def _on_download_click(self, vod_info):
        """다운로드 버튼 클릭 콜백"""
        from core.downloader import DownloadTask

        # VOD URL 생성
        vod_id = vod_info.get('videoNo')
        vod_url = f"https://chzzk.naver.com/video/{vod_id}"

        # 다운로드 작업 생성
        task = DownloadTask(
            vod_url=vod_url,
            title=vod_info.get('videoTitle', 'Unknown'),
            quality=self.quality_var.get(),
            output_path=self.config_manager.get('download_path', 'downloads')
        )

        # 다운로더에 추가
        self.downloader.add_download(task)
        self.download_frame.add_task(task)

        logger.info(f"다운로드 추가: {task.title}")

    def _on_download_progress(self, task):
        """다운로드 진행률 콜백"""
        # UI 업데이트
        self.after(0, lambda: self.download_frame.update_task(task))

    def _on_cancel_download(self, task):
        """다운로드 중지 콜백"""
        self.downloader.cancel_download(task.vod_url)
        logger.info(f"다운로드 중지 요청: {task.title}")

    def _on_remove_download(self, task):
        """다운로드 제거 콜백"""
        self.downloader.remove_download(task.vod_url)
        logger.info(f"다운로드 항목 제거: {task.title}")

    def _on_quality_change(self, quality):
        """화질 변경 콜백"""
        self.config_manager.set('default_quality', quality)
        logger.info(f"기본 화질 변경: {quality}")

    def _on_theme_change(self, theme):
        """테마 변경 콜백"""
        ctk.set_appearance_mode(theme)
        self.config_manager.set('theme', theme)
        logger.info(f"테마 변경: {theme}")

    def _show_error(self, title, message):
        """에러 메시지 표시"""
        dialog = ctk.CTkInputDialog(
            text=f"{title}\n\n{message}",
            title=title
        )

    def _check_for_updates(self):
        """업데이트 확인 (백그라운드)"""
        import threading
        thread = threading.Thread(target=self._check_updates_thread, daemon=True)
        thread.start()

    def _check_updates_thread(self):
        """업데이트 확인 스레드"""
        try:
            checker = VersionChecker()
            has_update, latest_version, download_url, release_notes = checker.check_for_updates_simple()

            if has_update:
                # UI 업데이트는 메인 스레드에서
                self.after(0, lambda: self._show_update_dialog(
                    latest_version, download_url, release_notes
                ))
        except Exception as e:
            logger.error(f"업데이트 확인 오류: {e}")

    def _show_update_dialog(self, latest_version, download_url, release_notes):
        """업데이트 다이얼로그 표시"""
        UpdateDialog(self, latest_version, download_url, release_notes)

    def on_closing(self):
        """윈도우 종료 시"""
        logger.info("애플리케이션 종료")
        self.downloader.stop()
        self.destroy()
