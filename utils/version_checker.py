"""
버전 체크 모듈
GitHub Releases를 통한 업데이트 확인
"""
import requests
from packaging import version
from utils.logger import logger


# 현재 버전
CURRENT_VERSION = "1.0.0"

# GitHub 저장소 정보
GITHUB_REPO_OWNER = "nyando376"
GITHUB_REPO_NAME = "Download-Mozang"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"


class VersionChecker:
    """버전 체크 클래스"""

    def __init__(self):
        self.current_version = CURRENT_VERSION
        self.latest_version = None
        self.download_url = None
        self.release_notes = None

    def check_for_updates(self, timeout=5):
        """
        업데이트 확인

        Returns:
            tuple: (업데이트 있음 여부, 최신 버전, 다운로드 URL, 릴리즈 노트)
        """
        try:
            # GitHub API 호출
            response = requests.get(GITHUB_API_URL, timeout=timeout)

            if response.status_code == 200:
                data = response.json()

                # 최신 버전 정보 추출
                self.latest_version = data.get('tag_name', '').lstrip('v')
                self.download_url = data.get('html_url', '')
                self.release_notes = data.get('body', '')

                # 버전 비교
                if self._is_newer_version(self.latest_version):
                    logger.info(f"새 버전 발견: {self.latest_version} (현재: {self.current_version})")
                    return True, self.latest_version, self.download_url, self.release_notes
                else:
                    logger.info(f"최신 버전 사용 중: {self.current_version}")
                    return False, self.current_version, None, None

            elif response.status_code == 404:
                # 저장소가 없거나 릴리즈가 없음
                logger.warning("GitHub 릴리즈를 찾을 수 없습니다")
                return False, self.current_version, None, None

            else:
                logger.error(f"GitHub API 오류: {response.status_code}")
                return False, self.current_version, None, None

        except requests.exceptions.Timeout:
            logger.warning("버전 체크 타임아웃 (네트워크 느림)")
            return False, self.current_version, None, None

        except requests.exceptions.ConnectionError:
            logger.warning("버전 체크 실패 (인터넷 연결 확인)")
            return False, self.current_version, None, None

        except Exception as e:
            logger.error(f"버전 체크 오류: {e}")
            return False, self.current_version, None, None

    def _is_newer_version(self, latest_version_str):
        """
        버전 비교

        Args:
            latest_version_str: 최신 버전 문자열

        Returns:
            bool: 최신 버전이 현재 버전보다 새로운지 여부
        """
        try:
            latest = version.parse(latest_version_str)
            current = version.parse(self.current_version)
            return latest > current
        except Exception as e:
            logger.error(f"버전 비교 오류: {e}")
            return False

    def check_for_updates_simple(self):
        """
        간단한 버전 체크 (테스트용)
        실제 GitHub 저장소가 없을 때 사용

        Returns:
            tuple: (업데이트 있음 여부, 최신 버전, 다운로드 URL, 릴리즈 노트)
        """
        # TODO: 실제 배포 시 이 부분을 삭제하고 check_for_updates 사용

        # 테스트용: 업데이트가 있는 것처럼 시뮬레이션
        # 실제 사용 시에는 아래 주석을 해제하고 위 코드 삭제
        test_update = False  # True로 변경하면 업데이트 알림 테스트

        if test_update:
            return (
                True,
                "1.1.0",  # 가짜 최신 버전
                "https://github.com/your-repo/releases",  # 다운로드 URL
                "• 새로운 기능 추가\n• 버그 수정\n• 성능 개선"  # 릴리즈 노트
            )

        # 일반적으로는 업데이트 없음 반환
        return False, self.current_version, None, None


def get_current_version():
    """현재 버전 반환"""
    return CURRENT_VERSION
