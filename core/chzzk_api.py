"""
치지직 API 래퍼
yt-dlp를 사용하여 치지직 VOD 정보 추출
"""
import yt_dlp
import requests
from utils.logger import logger
from utils.validators import extract_channel_id, extract_video_id


class ChzzkAPI:
    """치지직 API 클래스"""

    def __init__(self):
        self.base_url = "https://api.chzzk.naver.com/service/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_channel_info(self, channel_url):
        """
        채널 정보 가져오기

        Returns:
            dict: 채널 정보 (이름, ID, 프로필 이미지 등)
        """
        try:
            channel_id = extract_channel_id(channel_url)
            if not channel_id:
                logger.error("채널 ID 추출 실패")
                return None

            # 치지직 API 엔드포인트
            url = f"{self.base_url}/channels/{channel_id}"
            response = self.session.get(url)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"채널 정보 조회 성공: {channel_id}")
                return data.get('content', {})
            else:
                logger.error(f"채널 정보 조회 실패: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"채널 정보 조회 오류: {e}")
            return None

    def get_vod_list(self, channel_id, page=0, size=30):
        """
        VOD 목록 가져오기

        Args:
            channel_id: 채널 ID
            page: 페이지 번호
            size: 페이지당 항목 수

        Returns:
            list: VOD 목록
        """
        try:
            url = f"{self.base_url}/channels/{channel_id}/videos"
            params = {
                'page': page,
                'size': size,
                'sortType': 'LATEST'
            }

            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                vod_list = data.get('content', {}).get('data', [])
                logger.info(f"VOD 목록 조회 성공: {len(vod_list)}개")
                return vod_list
            else:
                logger.error(f"VOD 목록 조회 실패: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"VOD 목록 조회 오류: {e}")
            return []

    def get_vod_info_with_ytdlp(self, vod_url):
        """
        yt-dlp를 사용하여 VOD 정보 가져오기

        Args:
            vod_url: VOD URL

        Returns:
            dict: VOD 정보 (제목, 스트림 URL, 포맷 등)
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(vod_url, download=False)
                logger.info(f"VOD 정보 추출 성공: {info.get('title', 'Unknown')}")
                return info

        except Exception as e:
            logger.error(f"VOD 정보 추출 오류: {e}")
            return None

    def get_available_formats(self, vod_url):
        """
        사용 가능한 화질 옵션 가져오기

        Args:
            vod_url: VOD URL

        Returns:
            list: 사용 가능한 포맷 목록
        """
        try:
            info = self.get_vod_info_with_ytdlp(vod_url)
            if not info:
                return []

            formats = info.get('formats', [])

            # 비디오 포맷만 필터링
            video_formats = []
            for fmt in formats:
                if fmt.get('vcodec') != 'none':
                    video_formats.append({
                        'format_id': fmt.get('format_id'),
                        'ext': fmt.get('ext'),
                        'resolution': fmt.get('resolution', 'Unknown'),
                        'height': fmt.get('height', 0),
                        'width': fmt.get('width', 0),
                        'filesize': fmt.get('filesize', 0),
                        'fps': fmt.get('fps', 0),
                    })

            # 해상도 기준으로 정렬
            video_formats.sort(key=lambda x: x['height'], reverse=True)

            logger.info(f"사용 가능한 포맷: {len(video_formats)}개")
            return video_formats

        except Exception as e:
            logger.error(f"포맷 조회 오류: {e}")
            return []

    def search_vods(self, channel_id, keyword, page=0, size=30):
        """
        VOD 검색

        Args:
            channel_id: 채널 ID
            keyword: 검색 키워드
            page: 페이지 번호
            size: 페이지당 항목 수

        Returns:
            list: 검색 결과
        """
        try:
            # 전체 VOD 목록 가져오기
            all_vods = self.get_vod_list(channel_id, page, size)

            # 키워드로 필터링
            filtered_vods = [
                vod for vod in all_vods
                if keyword.lower() in vod.get('videoTitle', '').lower()
            ]

            logger.info(f"검색 결과: {len(filtered_vods)}개")
            return filtered_vods

        except Exception as e:
            logger.error(f"VOD 검색 오류: {e}")
            return []
