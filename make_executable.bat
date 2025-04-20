@echo off
echo Making setup_gh_pages.sh executable...
echo This script needs to be run on a Linux/macOS system to work.
echo If you're on Windows, you can ignore this or run it in Git Bash.

git update-index --chmod=+x setup_gh_pages.sh
git commit -m "Make setup_gh_pages.sh executable"
git push

echo Done!
pause
