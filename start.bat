@echo off
echo ===================================
echo Starting File Converter Application
echo ===================================
echo.

echo Checking if Redis is running...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Redis is not running!
    echo Please start Redis first:
    echo   redis-server
    echo   or
    echo   net start redis
    echo.
    pause
    exit /b 1
)
echo [OK] Redis is running

echo.
echo Starting Celery worker in background...
start /B cmd /c "celery -A fileconverter worker --pool=solo --loglevel=info > celery.log 2>&1"

timeout /t 3 /nobreak >nul

echo.
echo Starting Django development server...
echo.
echo Application will be available at:
echo   http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

daphne -b 127.0.0.1 -p 8000 fileconverter.asgi:application

