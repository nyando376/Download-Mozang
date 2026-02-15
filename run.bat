@echo off
REM 사모장 치지직 다시보기 다운로더 실행 스크립트 (Windows CMD)

echo 사모장 치지직 다시보기 다운로더를 시작합니다...
echo.

REM 가상 환경 활성화
call venv\Scripts\activate.bat

REM Python 애플리케이션 실행
python main.py

pause
