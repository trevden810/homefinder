@echo off
echo HomeFinder - Real Estate Property Scraper
echo ========================================
echo.

echo Checking Python installation...
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in the PATH. Please install Python.
    pause
    exit /b 1
)

echo Checking for virtual environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Installing requirements...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo Choose the application mode:
echo 1. Command-line interface
echo 2. Web interface
echo.

set /p mode="Enter your choice (1 or 2): "

if "%mode%"=="1" (
    echo.
    echo Starting command-line interface...
    echo.
    python app.py %*
) else if "%mode%"=="2" (
    echo.
    echo Starting web interface...
    echo.
    echo Web app will be available at http://localhost:5000
    echo Press Ctrl+C to exit
    echo.
    python web_app.py
) else (
    echo.
    echo Invalid choice. Please enter 1 or 2.
    pause
    exit /b 1
)

deactivate
