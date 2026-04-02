@echo off
title Moot Court Tabulation System
echo ==================================================
echo   Moot Court Tabulation System
echo ==================================================
echo.
echo Starting server...
echo Close this window to stop the server.
echo.
cd /d "%~dp0"
python launcher.py
pause
