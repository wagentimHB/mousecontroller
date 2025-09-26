@echo off
echo Starting Mouse Recorder GUI...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the GUI using the virtual environment Python via main.py
venv\Scripts\python.exe src\test\main.py gui

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)