@echo off
echo Creating static version of HomeFinder for GitHub Pages...

REM Create directories for static content
mkdir gh-pages
mkdir gh-pages\static

REM Copy static files
copy static\style.css gh-pages\static\style.css

REM Create index.html
echo Creating index.html...
copy templates\index.html gh-pages\index.html

REM Create JavaScript file
echo Creating script.js...
echo // HomeFinder static demo script > gh-pages\script.js
type NUL >> gh-pages\script.js

echo.
echo Static files created in the gh-pages directory.
echo.
echo To publish to GitHub Pages:
echo 1. Push your main code to GitHub
echo 2. Create a gh-pages branch: git checkout -b gh-pages
echo 3. Copy all files from gh-pages directory to the root of the gh-pages branch
echo 4. Commit and push: git push origin gh-pages
echo 5. Go to your repository settings and enable GitHub Pages for the gh-pages branch
echo.
echo Or use the setup_github_pages.bat script.
pause
