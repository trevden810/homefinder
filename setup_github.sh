#!/bin/bash

echo "Setting up GitHub repository for HomeFinder..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git."
    exit 1
fi

# Initialize git repository
git init
if [ $? -ne 0 ]; then
    echo "Failed to initialize git repository."
    exit 1
fi

# Add all files to git
git add .
if [ $? -ne 0 ]; then
    echo "Failed to add files to git."
    exit 1
fi

# Commit all files
git commit -m "Initial commit of HomeFinder application"
if [ $? -ne 0 ]; then
    echo "Failed to commit files."
    exit 1
fi

# Add remote repository
git remote add origin https://github.com/trevden810/homefinder.git
if [ $? -ne 0 ]; then
    echo "Failed to add remote repository."
    exit 1
fi

# Push to GitHub
echo
echo "Ready to push to GitHub."
echo "You will need to enter your GitHub username and password/token."
echo
git push -u origin master
if [ $? -ne 0 ]; then
    echo "Failed to push to GitHub. Trying main branch instead of master..."
    git push -u origin main
    if [ $? -ne 0 ]; then
        echo "Failed to push to GitHub."
        exit 1
    fi
fi

echo
echo "Successfully pushed HomeFinder to GitHub!"
echo "Repository URL: https://github.com/trevden810/homefinder"
echo
