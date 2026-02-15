"""
입력 검증 유틸리티
"""
import re
import os


def validate_chzzk_url(url):
    """
    치지직 URL 검증

    지원 형식:
    - https://chzzk.naver.com/[channel_id]
    - https://chzzk.naver.com/live/[channel_id]
    - https://chzzk.naver.com/video/[video_id]
    """
    if not url:
        return False, "URL이 비어있습니다."

    # 치지직 URL 패턴
    patterns = [
        r'https?://chzzk\.naver\.com/([a-zA-Z0-9_-]+)',
        r'https?://chzzk\.naver\.com/live/([a-zA-Z0-9_-]+)',
        r'https?://chzzk\.naver\.com/video/([a-zA-Z0-9_-]+)',
    ]

    for pattern in patterns:
        if re.match(pattern, url):
            return True, "유효한 치지직 URL입니다."

    return False, "유효하지 않은 치지직 URL입니다."


def validate_path(path):
    """파일 경로 검증"""
    if not path:
        return False, "경로가 비어있습니다."

    try:
        # 경로가 존재하는지 확인
        parent_dir = os.path.dirname(path) or '.'
        if not os.path.exists(parent_dir):
            return False, f"상위 디렉토리가 존재하지 않습니다: {parent_dir}"

        # 쓰기 권한 확인
        if not os.access(parent_dir, os.W_OK):
            return False, f"쓰기 권한이 없습니다: {parent_dir}"

        return True, "유효한 경로입니다."
    except Exception as e:
        return False, f"경로 검증 오류: {str(e)}"


def extract_channel_id(url):
    """URL에서 채널 ID 추출"""
    patterns = [
        r'https?://chzzk\.naver\.com/([a-zA-Z0-9_-]+)/?$',
        r'https?://chzzk\.naver\.com/live/([a-zA-Z0-9_-]+)',
    ]

    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)

    return None


def extract_video_id(url):
    """URL에서 비디오 ID 추출"""
    pattern = r'https?://chzzk\.naver\.com/video/([a-zA-Z0-9_-]+)'
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    return None
