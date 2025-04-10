@echo off
echo Fixing Git repository...

echo Step 1: Removing specific large files from Git tracking
git rm --cached "dist/WallStonks.exe" 2>nul
git rm --cached "build/WallStonks/WallStonks.pkg" 2>nul

echo Step 2: Also remove any other large files and build artifacts
git rm -r --cached dist/ 2>nul
git rm -r --cached build/ 2>nul
git rm --cached *.spec 2>nul
git rm --cached *.exe 2>nul
git rm --cached *.pyc 2>nul

echo Step 3: Adding .gitignore to prevent re-adding these files
git add .gitignore

echo Step 4: Committing changes
git commit -m "Remove large files from Git tracking and add .gitignore"

echo Step 5: Clean up Git repository
git gc

echo Done! Now try pushing with 'git push -f' to force update the remote repository
echo Note: This will overwrite the remote repository history! 