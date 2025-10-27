@echo off
chcp 65001 >nul
echo ================================================
echo   🚀 SPARK RUNNER GUI - AUTO START
echo ================================================
echo.

REM Kiểm tra Docker đang chạy
echo [1/3] Kiểm tra Docker Desktop...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop chưa chạy!
    echo    → Hãy mở Docker Desktop và chờ nó khởi động xong
    echo    → Sau đó chạy lại file này
    pause
    exit /b 1
)
echo ✅ Docker Desktop đang chạy

echo.
echo [2/3] Khởi động Spark Cluster...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Lỗi khi start containers!
    pause
    exit /b 1
)

echo.
echo ⏳ Đợi containers khởi động (10 giây)...
timeout /t 10 /nobreak >nul

echo.
echo [3/3] Kiểm tra trạng thái containers...
docker-compose ps

echo.
echo ================================================
echo ✅ Spark Cluster đã sẵn sàng!
echo ================================================
echo.
echo 🌐 Có thể truy cập:
echo    • Spark Master UI:  http://localhost:8080
echo    • HDFS NameNode:    http://localhost:9870
echo.
echo 🖥️  Bây giờ chạy GUI Application:
echo    cd run_spark_gui
echo    python main.py
echo.
echo Hoặc nhấn Enter để tự động mở GUI...
pause

REM Mở GUI
cd run_spark_gui
start "Spark Runner GUI" python main.py

echo.
echo ✅ GUI đã mở!
echo ⚠️  ĐỪNG ĐÓNG cửa sổ này nếu muốn xem logs Docker
echo.
pause

