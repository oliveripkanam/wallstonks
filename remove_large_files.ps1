# PowerShell script to remove large files from Git history
Write-Host "Removing large files from Git history..." -ForegroundColor Yellow

# Add current changes
git add .

# Commit current changes
git commit -m "Update .gitignore with specific large files" -a

# Remove the large files using filter-branch
Write-Host "Removing large files from all Git history..." -ForegroundColor Red
git filter-branch -f --index-filter "git rm --cached --ignore-unmatch dist/WallStonks.exe build/WallStonks/WallStonks.pkg" HEAD

# Clean up refs
Write-Host "Cleaning up refs..." -ForegroundColor Cyan
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin

# Aggressive garbage collection
Write-Host "Running garbage collection..." -ForegroundColor Green
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host "`nDone! Now you can push with:" -ForegroundColor Green
Write-Host "git push -f origin main" -ForegroundColor Yellow
Write-Host "WARNING: This will overwrite remote history!" -ForegroundColor Red 