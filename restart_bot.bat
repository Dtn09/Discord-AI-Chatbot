@echo off
echo 🔄 Restarting Discord Bot with Duplicate Response Fix
echo =====================================================

echo 🛑 Stopping current bot instance...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 >nul

echo ✅ Starting bot with Albert Einstein 2025 persona...
echo.

python main.py

pause