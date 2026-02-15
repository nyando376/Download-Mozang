"""
사모장 치지직 다시보기 다운로더
메인 진입점
"""
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from utils.logger import logger


def main():
    """메인 함수"""
    try:
        logger.info("=" * 50)
        logger.info("사모장 치지직 다시보기 다운로더 시작")
        logger.info("=" * 50)

        # 메인 윈도우 생성 및 실행
        app = MainWindow()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()

    except Exception as e:
        logger.error(f"치명적 오류: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
