@echo off
echo Fixing Git repository...

echo Step 1: Removing large files and build artifacts from Git tracking
git rm --cached -r dist 2>nul
git rm --cached -r build 2>nul
git rm --cached *.spec 2>nul
git rm --cached *.exe 2>nul
git rm --cached *.pyc 2>nul

echo Step 2: Adding .gitignore to track it
git add .gitignore

echo Step 3: Committing changes
git commit -m "Remove large files from Git tracking and add .gitignore"

echo Step 4: Making sure the repository is clean
git gc

echo Done! Now you should be able to push to GitHub without issues
echo Use "git push" to push your changes 