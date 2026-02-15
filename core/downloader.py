"""
다운로드 엔진
yt-dlp를 사용한 비디오 다운로드 로직
"""
import os
import threading
import queue
from datetime import datetime
import yt_dlp
from utils.logger import logger


class DownloadTask:
    """다운로드 작업 클래스"""

    def __init__(self, vod_url, title, quality='best', output_path='downloads'):
        self.vod_url = vod_url
        self.title = title
        self.quality = quality
        self.output_path = output_path
        self.status = 'pending'  # pending, downloading, completed, failed, paused, cancelled
        self.progress = 0.0
        self.speed = ''
        self.eta = ''
        self.downloaded_bytes = 0
        self.total_bytes = 0
        self.error_message = ''
        self.output_file = ''
        self.cancel_flag = False  # 중지 플래그

    def to_dict(self):
        """딕셔너리로 변환"""
        return {
            'vod_url': self.vod_url,
            'title': self.title,
            'quality': self.quality,
            'status': self.status,
            'progress': self.progress,
            'speed': self.speed,
            'eta': self.eta,
            'error_message': self.error_message,
            'output_file': self.output_file,
        }


class Downloader:
    """다운로더 클래스"""

    def __init__(self, max_concurrent=3):
        self.max_concurrent = max_concurrent
        self.download_queue = queue.Queue()
        self.active_downloads = {}
        self.completed_downloads = []
        self.is_running = False
        self.worker_threads = []
        self.progress_callbacks = []

    def add_download(self, task):
        """다운로드 작업 추가"""
        self.download_queue.put(task)
        logger.info(f"다운로드 추가: {task.title}")

    def start(self):
        """다운로드 시작"""
        if self.is_running:
            logger.warning("다운로더가 이미 실행 중입니다")
            return

        self.is_running = True

        # 워커 스레드 시작
        for i in range(self.max_concurrent):
            thread = threading.Thread(target=self._worker, daemon=True)
            thread.start()
            self.worker_threads.append(thread)
            logger.info(f"워커 스레드 {i+1} 시작")

    def stop(self):
        """다운로드 중지"""
        self.is_running = False
        logger.info("다운로더 중지")

    def _worker(self):
        """워커 스레드"""
        while self.is_running:
            try:
                # 큐에서 작업 가져오기 (타임아웃 1초)
                task = self.download_queue.get(timeout=1)

                # 다운로드 실행
                self._download_video(task)

                # 작업 완료
                self.download_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"워커 오류: {e}")

    def _download_video(self, task):
        """비디오 다운로드"""
        try:
            # 취소된 작업은 건너뛰기
            if task.cancel_flag:
                logger.info(f"취소된 다운로드 건너뛰기: {task.title}")
                return

            task.status = 'downloading'
            self.active_downloads[task.vod_url] = task
            logger.info(f"다운로드 시작: {task.title}")

            # 출력 파일명 생성
            safe_title = self._sanitize_filename(task.title)
            output_template = os.path.join(task.output_path, f'{safe_title}.%(ext)s')

            # yt-dlp 옵션
            ydl_opts = {
                'format': self._get_format_selector(task.quality),
                'outtmpl': output_template,
                'progress_hooks': [lambda d: self._progress_hook(d, task)],
                'quiet': True,
                'no_warnings': True,
            }

            # 다운로드 실행
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 주기적으로 취소 플래그 확인
                if task.cancel_flag:
                    raise Exception("사용자가 다운로드를 중지했습니다")

                info = ydl.extract_info(task.vod_url, download=True)
                task.output_file = ydl.prepare_filename(info)

            # 취소 확인
            if task.cancel_flag:
                raise Exception("사용자가 다운로드를 중지했습니다")

            # 완료 처리
            task.status = 'completed'
            task.progress = 100.0
            self.completed_downloads.append(task)
            if task.vod_url in self.active_downloads:
                del self.active_downloads[task.vod_url]

            logger.info(f"다운로드 완료: {task.title}")
            self._notify_progress(task)

        except Exception as e:
            # 취소된 경우
            if task.cancel_flag or "중지" in str(e):
                task.status = 'cancelled'
                logger.info(f"다운로드 중지됨: {task.title}")
            else:
                task.status = 'failed'
                task.error_message = str(e)
                logger.error(f"다운로드 실패: {task.title} - {e}")

            if task.vod_url in self.active_downloads:
                del self.active_downloads[task.vod_url]

            self._notify_progress(task)

    def _progress_hook(self, d, task):
        """진행률 콜백"""
        if d['status'] == 'downloading':
            # 진행률 계산
            if d.get('total_bytes'):
                task.total_bytes = d['total_bytes']
                task.downloaded_bytes = d['downloaded_bytes']
                task.progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif d.get('total_bytes_estimate'):
                task.total_bytes = d['total_bytes_estimate']
                task.downloaded_bytes = d['downloaded_bytes']
                task.progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100

            # 속도 및 남은 시간
            task.speed = d.get('_speed_str', '')
            task.eta = d.get('_eta_str', '')

            # 콜백 호출
            self._notify_progress(task)

        elif d['status'] == 'finished':
            logger.info(f"파일 다운로드 완료, 후처리 중: {task.title}")

    def _notify_progress(self, task):
        """진행률 콜백 알림"""
        for callback in self.progress_callbacks:
            try:
                callback(task)
            except Exception as e:
                logger.error(f"콜백 오류: {e}")

    def add_progress_callback(self, callback):
        """진행률 콜백 추가"""
        self.progress_callbacks.append(callback)

    def _get_format_selector(self, quality):
        """화질 선택자 생성"""
        quality_map = {
            'best': 'bestvideo+bestaudio/best',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
        }
        return quality_map.get(quality, 'best')

    def _sanitize_filename(self, filename):
        """파일명에서 특수문자 제거"""
        # Windows에서 허용되지 않는 문자 제거
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    def get_active_downloads(self):
        """진행 중인 다운로드 목록"""
        return list(self.active_downloads.values())

    def get_queue_size(self):
        """대기 중인 작업 수"""
        return self.download_queue.qsize()

    def cancel_download(self, vod_url):
        """다운로드 중지"""
        # 활성 다운로드 중지
        if vod_url in self.active_downloads:
            task = self.active_downloads[vod_url]
            task.cancel_flag = True
            task.status = 'cancelled'
            logger.info(f"다운로드 중지: {task.title}")
            return True

        # 대기 중인 작업 중지 (큐에서 제거는 어려우므로 플래그만 설정)
        # 큐를 순회하며 해당 작업 찾기
        temp_queue = queue.Queue()
        found = False
        while not self.download_queue.empty():
            try:
                task = self.download_queue.get_nowait()
                if task.vod_url == vod_url:
                    task.cancel_flag = True
                    task.status = 'cancelled'
                    logger.info(f"대기 중인 다운로드 중지: {task.title}")
                    found = True
                temp_queue.put(task)
            except queue.Empty:
                break

        # 큐 복원
        while not temp_queue.empty():
            self.download_queue.put(temp_queue.get())

        return found

    def remove_download(self, vod_url):
        """다운로드 항목 제거 (완료/실패한 항목)"""
        # 완료된 다운로드에서 제거
        self.completed_downloads = [
            task for task in self.completed_downloads
            if task.vod_url != vod_url
        ]

        # 활성 다운로드면 먼저 중지
        if vod_url in self.active_downloads:
            self.cancel_download(vod_url)

        logger.info(f"다운로드 항목 제거: {vod_url}")
        return True
