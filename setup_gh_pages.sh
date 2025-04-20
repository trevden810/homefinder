#!/bin/bash

echo "Setting up GitHub Pages branch for HomeFinder..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git."
    exit 1
fi

# Save current branch name
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Check if there are any uncommitted changes
if ! git diff --quiet --exit-code; then
    echo "You have uncommitted changes. Please commit or stash them first."
    exit 1
fi

# Check if gh-pages branch exists
if git show-ref --verify --quiet refs/heads/gh-pages; then
    echo "gh-pages branch already exists. Will update it."
    
    # Switch to gh-pages branch
    git checkout gh-pages
    
    # Clean the branch
    git rm -rf .
    
    # Copy the static files
    cp index.html .
    cp style.css .
    cp script.js .
    cp README.md .
    
    # Add the changes
    git add index.html style.css script.js README.md
    
    # Commit the changes
    git commit -m "Update GitHub Pages content"
    
    # Push to GitHub
    echo "Pushing to GitHub..."
    git push origin gh-pages
else
    echo "Creating new gh-pages branch..."
    
    # Create and switch to a new gh-pages branch
    git checkout --orphan gh-pages
    
    # Remove all tracked files
    git rm -rf .
    
    # Copy the static files
    cp index.html .
    cp style.css .
    cp script.js .
    cp README.md .
    
    # Add the new files
    git add index.html style.css script.js README.md
    
    # Commit the changes
    git commit -m "Initial GitHub Pages content"
    
    # Push to GitHub
    echo "Pushing to GitHub..."
    git push origin gh-pages
fi

# Switch back to the original branch
git checkout "$CURRENT_BRANCH"

echo
echo "GitHub Pages branch has been created/updated!"
echo
echo "To enable GitHub Pages:"
echo "1. Go to your repository on GitHub"
echo "2. Go to Settings -> Pages"
echo "3. Under 'Source', select 'Deploy from a branch'"
echo "4. Select 'gh-pages' branch and '/ (root)' folder"
echo "5. Click 'Save'"
echo
echo "Your site will be available at https://trevden810.github.io/homefinder/"
echo
