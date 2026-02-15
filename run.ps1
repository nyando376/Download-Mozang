# 사모장 치지직 다시보기 다운로더 실행 스크립트 (PowerShell)

Write-Host "사모장 치지직 다시보기 다운로더를 시작합니다..." -ForegroundColor Green
Write-Host ""

# 가상 환경 활성화
& .\venv\Scripts\Activate.ps1

# Python 애플리케이션 실행
python main.py
