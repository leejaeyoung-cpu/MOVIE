@echo off
chcp 65001 > nul
echo ========================================================
echo 🎬 영화 리뷰 시스템을 시작합니다...
echo ========================================================

:: 1. Backend 실행 (새 창)
echo [1/2] 백엔드 서버 시작 중...
:: "Movie Backend"라는 제목의 새 창을 열고, 거기서 명령어 실행.
:: 실행 후 창이 꺼지지 않도록 /k 옵션 사용
start "Movie Backend" cmd /k "call venv\Scripts\activate && cd backend && echo 백엔드 시작 중... && uvicorn app.main:app --reload --port 8000"

:: 백엔드가 완전히 뜰 때까지 충분히 대기 (5초)
echo 백엔드 로딩 대기 중 (5초)...
timeout /t 5 /nobreak > nul

:: 2. Frontend 실행 (새 창)
echo [2/2] 프론트엔드 대시보드 시작 중...
start "Movie Frontend" cmd /k "call venv\Scripts\activate && cd frontend && echo 프론트엔드 시작 중... && streamlit run app.py"

echo.
echo ✅ 실행 명령을 모두 보냈습니다!
echo.
echo ⚠️ 주의:
echo 1. 'Movie Backend' 창이 켜져 있어야 합니다. (에러가 나면 그 창을 확인하세요)
echo 2. 브라우저가 열리면 잠시 기다려주세요.
echo.
pause
