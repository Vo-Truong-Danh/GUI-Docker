@echo off
chcp 65001 >nul
echo ================================================
echo   🛑 SPARK RUNNER GUI - STOP ALL
echo ================================================
echo.

echo [1/2] Dừng tất cả Docker containers...
docker-compose down

if %errorlevel% neq 0 (
    echo ❌ Lỗi khi stop containers!
    pause
    exit /b 1
)

echo.
echo [2/2] Kiểm tra trạng thái...
docker-compose ps

echo.
echo ================================================
echo ✅ Đã dừng tất cả containers!
echo ================================================
echo.
echo 💡 Để start lại, chạy: START_ALL.bat
echo.
pause

