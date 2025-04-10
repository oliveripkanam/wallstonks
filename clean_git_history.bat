@echo off
echo *** IMPORTANT: This script will rewrite Git history! ***
echo This will completely remove large files from the repository history.
echo You will need to force-push (git push -f) after running this script.
echo.
pause

echo Step 1: Removing large files from Git history...
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch dist/WallStonks.exe build/WallStonks/WallStonks.pkg" --prune-empty --tag-name-filter cat -- --all

echo Step 2: Removing the original refs...
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin

echo Step 3: Performing garbage collection...
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo Step 4: Adding and committing .gitignore...
git add .gitignore
git commit -m "Add .gitignore to prevent large files from being added" || echo "No changes to commit"

echo.
echo Cleanup complete! Now you should force-push with:
echo git push -f
echo.
echo WARNING: This will overwrite history on the remote repository. 