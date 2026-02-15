"""
설정 관리 모듈
"""
import json
import os
from utils.logger import logger


class ConfigManager:
    """설정 파일 관리 클래스"""

    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"설정 파일 로드 성공: {self.config_file}")
                    return config
            else:
                logger.warning(f"설정 파일이 없습니다. 기본 설정 사용: {self.config_file}")
                return self.get_default_config()
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            return self.get_default_config()

    def save_config(self):
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"설정 파일 저장 성공: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")
            return False

    def get(self, key, default=None):
        """설정 값 가져오기"""
        return self.config.get(key, default)

    def set(self, key, value):
        """설정 값 설정"""
        self.config[key] = value
        self.save_config()

    def get_default_config(self):
        """기본 설정 반환"""
        return {
            "channel_url": "https://chzzk.naver.com/23d5909c6b808d80ee28a9a2d509fecc",
            "download_path": "downloads",
            "max_concurrent_downloads": 3,
            "default_quality": "best",
            "theme": "dark",
            "language": "ko",
            "auto_start_download": False,
            "notification_enabled": True
        }

    def ensure_download_path(self):
        """다운로드 경로가 존재하는지 확인하고 없으면 생성"""
        download_path = self.get('download_path', 'downloads')
        if not os.path.exists(download_path):
            try:
                os.makedirs(download_path)
                logger.info(f"다운로드 디렉토리 생성: {download_path}")
            except Exception as e:
                logger.error(f"다운로드 디렉토리 생성 실패: {e}")
