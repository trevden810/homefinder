@echo off
echo Setting up GitHub Pages branch for HomeFinder...

REM Check if git is installed
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed or not in the PATH. Please install Git.
    pause
    exit /b 1
)

REM Save current branch name
for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
echo Current branch: %CURRENT_BRANCH%

REM Check if there are any uncommitted changes
git diff --quiet --exit-code
if %ERRORLEVEL% NEQ 0 (
    echo You have uncommitted changes. Please commit or stash them first.
    pause
    exit /b 1
)

REM Check if gh-pages branch exists
git show-ref --verify --quiet refs/heads/gh-pages
if %ERRORLEVEL% EQU 0 (
    echo gh-pages branch already exists. Will update it.
    
    REM Switch to gh-pages branch
    git checkout gh-pages
    
    REM Clean the branch
    git rm -rf .
    
    REM Copy the static files
    copy index.html .
    copy style.css .
    copy script.js .
    copy README.md .
    
    REM Add the changes
    git add index.html style.css script.js README.md
    
    REM Commit the changes
    git commit -m "Update GitHub Pages content"
    
    REM Push to GitHub
    echo Pushing to GitHub...
    git push origin gh-pages
) else (
    echo Creating new gh-pages branch...
    
    REM Create and switch to a new gh-pages branch
    git checkout --orphan gh-pages
    
    REM Remove all tracked files
    git rm -rf .
    
    REM Copy the static files
    copy index.html .
    copy style.css .
    copy script.js .
    copy README.md .
    
    REM Add the new files
    git add index.html style.css script.js README.md
    
    REM Commit the changes
    git commit -m "Initial GitHub Pages content"
    
    REM Push to GitHub
    echo Pushing to GitHub...
    git push origin gh-pages
)

REM Switch back to the original branch
git checkout %CURRENT_BRANCH%

echo.
echo GitHub Pages branch has been created/updated!
echo.
echo To enable GitHub Pages:
echo 1. Go to your repository on GitHub
echo 2. Go to Settings -^> Pages
echo 3. Under "Source", select "Deploy from a branch"
echo 4. Select "gh-pages" branch and "/ (root)" folder
echo 5. Click "Save"
echo.
echo Your site will be available at https://trevden810.github.io/homefinder/
echo.
pause
