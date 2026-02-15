# 치지직 다운로더 (Chzzk VOD Downloader)

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

치지직(Chzzk) 플랫폼의 VOD(다시보기)를 편리하게 다운로드할 수 있는 GUI 데스크톱 애플리케이션

</div>

## ✨ 주요 기능

- 🎥 **자동 VOD 목록 로드** - 프로그램 시작 시 자동으로 VOD 목록 불러오기
- 🔍 **VOD 검색 기능** - 제목으로 빠르게 검색
- 📥 **다중 다운로드** - 최대 3개 동시 다운로드 지원
- 🎬 **화질 선택** - 360p, 480p, 720p, 1080p, 최고화질
- ⏸ **다운로드 제어** - 중지/삭제 버튼으로 다운로드 관리
- 📊 **실시간 진행률** - 다운로드 속도, 남은 시간 표시
- 🌙 **테마 지원** - 다크/라이트/시스템 테마
- 🔄 **자동 업데이트 체크** - 새 버전 자동 확인 및 알림
- ⚙️ **설정 저장** - 사용자 설정 자동 저장

## 📸 스크린샷

*(여기에 스크린샷 추가)*

## 💾 다운로드

최신 버전: [Releases](https://github.com/nyando376/Download-Mozang/releases/latest)에서 다운로드

### Windows
1. `치지직_다운로더_v1.0.zip` 다운로드
2. 압축 해제
3. `치지직_다운로더.exe` 실행

> **Python 설치 불필요!** 독립 실행 파일로 제공됩니다.

## 🚀 사용 방법

### 기본 사용법

1. **프로그램 실행**
   - `치지직_다운로더.exe` 더블클릭

2. **VOD 목록 확인**
   - 자동으로 지정된 채널의 VOD 목록이 로드됩니다

3. **다운로드**
   - 원하는 VOD의 "다운로드" 버튼 클릭
   - 우측 패널에서 진행 상황 확인
   - 다운로드된 파일은 `downloads` 폴더에 저장

4. **다운로드 제어**
   - ⏸ **중지**: 다운로드 일시 중지
   - ✕ **삭제**: 다운로드 항목 제거

### 설정 변경

- **화질**: 좌측 사이드바에서 기본 화질 선택
- **테마**: 다크/라이트 모드 전환
- **다운로드 경로**: `config.json`에서 수정 가능

## 🛠️ 개발자용 설정

### 필수 요구사항

- Python 3.8 이상
- pip 패키지 관리자

### 설치

```bash
# 저장소 클론
git clone https://github.com/nyando376/Download-Mozang.git
cd Download-Mozang

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows (Git Bash)
source venv/Scripts/activate
# Windows (CMD)
venv\Scripts\activate.bat
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 실행

```bash
python main.py
```

### 빌드

```bash
# PyInstaller로 실행 파일 생성
pyinstaller --onefile --windowed --name "치지직_다운로더" main.py

# 빌드된 파일은 dist/ 폴더에 생성됩니다
```

## 📁 프로젝트 구조

```
chzzk-downloader/
├── main.py                    # 앱 진입점
├── requirements.txt           # 의존성 목록
├── .gitignore                # Git 무시 파일
├── README.md                 # 프로젝트 설명
├── gui/                      # GUI 모듈
│   ├── main_window.py        # 메인 윈도우
│   ├── vod_list_frame.py     # VOD 목록 표시
│   ├── search_frame.py       # 검색 UI
│   ├── download_frame.py     # 다운로드 진행 상태
│   └── update_dialog.py      # 업데이트 알림
├── core/                     # 핵심 모듈
│   ├── chzzk_api.py          # 치지직 API 래퍼
│   ├── downloader.py         # 다운로드 로직
│   └── config_manager.py     # 설정 관리
└── utils/                    # 유틸리티
    ├── logger.py             # 로깅
    ├── validators.py         # 입력 검증
    └── version_checker.py    # 버전 체크
```

## 🔧 기술 스택

- **GUI**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 현대적인 Tkinter UI
- **다운로드**: [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 범용 비디오 다운로더
- **HTTP**: requests, aiohttp
- **이미지**: Pillow
- **빌드**: PyInstaller

## ⚠️ 주의사항

- 이 프로그램은 **개인적 용도**로만 사용하세요
- 다운로드한 콘텐츠를 재배포하거나 상업적으로 사용하지 마세요
- 치지직 플랫폼의 이용약관을 준수하세요

## 🐛 문제 해결

### 프로그램이 실행되지 않아요
- Windows Defender에서 차단했을 수 있습니다
- "추가 정보" → "실행"을 클릭하세요

### 다운로드가 실패해요
- 인터넷 연결을 확인하세요
- 로그 폴더의 로그 파일을 확인하세요

### VOD 목록이 로드되지 않아요
- 프로그램을 재시작해보세요
- 채널 URL이 올바른지 확인하세요

## 📝 업데이트 내역

### v1.0.0 (2026-02-15)
- 🎉 첫 릴리즈
- ✨ 자동 VOD 목록 로드
- ✨ 다운로드 중지/삭제 기능
- ✨ 자동 업데이트 체크
- ✨ 단일 실행 파일 배포

## 📄 라이센스

이 프로젝트는 MIT 라이센스로 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들을 참고하여 제작되었습니다:
- [chzzk-vod-downloader-v2](https://github.com/honey720/chzzk-vod-downloader-v2)
- [awesome-chzzk](https://github.com/dokdo2013/awesome-chzzk)

## 👨‍💻 개발자

Made with ❤️ by Claude + User

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!**

</div>
