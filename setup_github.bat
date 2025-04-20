@echo off
echo Setting up GitHub repository for HomeFinder...

REM Check if git is installed
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed or not in the PATH. Please install Git.
    pause
    exit /b 1
)

REM Initialize git repository
git init
if %ERRORLEVEL% NEQ 0 (
    echo Failed to initialize git repository.
    pause
    exit /b 1
)

REM Add all files to git
git add .
if %ERRORLEVEL% NEQ 0 (
    echo Failed to add files to git.
    pause
    exit /b 1
)

REM Commit all files
git commit -m "Initial commit of HomeFinder application"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to commit files.
    pause
    exit /b 1
)

REM Add remote repository
git remote add origin https://github.com/trevden810/homefinder.git
if %ERRORLEVEL% NEQ 0 (
    echo Failed to add remote repository.
    pause
    exit /b 1
)

REM Push to GitHub
echo.
echo Ready to push to GitHub.
echo You will need to enter your GitHub username and password/token.
echo.
git push -u origin master
if %ERRORLEVEL% NEQ 0 (
    echo Failed to push to GitHub. Trying main branch instead of master...
    git push -u origin main
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to push to GitHub.
        pause
        exit /b 1
    )
)

echo.
echo Successfully pushed HomeFinder to GitHub!
echo Repository URL: https://github.com/trevden810/homefinder
echo.
pause
