@echo off
chcp 65001 >nul

echo.
echo ========================================================================
echo   CHECKING DOCKER DATA
echo ========================================================================
echo.

echo [1] HDFS Data:
docker exec namenode hdfs dfs -du -h / 2>nul
echo.

echo [2] Docker System Usage:
docker system df
echo.

echo [3] Docker Volumes:
docker volume ls
echo.

echo [4] Containers:
docker ps -a --format "table {{.Names}}\t{{.Size}}"
echo.

echo [5] Images:
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
echo.

echo ========================================================================
echo   ANALYSIS
echo ========================================================================
echo.
echo If you see large volumes or stopped containers with data,
echo run: DEEP_CLEAN_DOCKER.bat
echo.
pause


