@echo off
echo.
echo ===== FIXING RENDER DEPLOYMENT =====
echo.
echo Step 1: Adding all changes to git...
git add .

echo.
echo Step 2: Committing the fixes...
git commit -m "Fix deployment: remove problematic openai/anthropic imports"

echo.
echo Step 3: Pushing to GitHub...
git push

echo.
echo ===== DEPLOYMENT FIX COMPLETE =====
echo.
echo Your Render deployment should now work!
echo The OpenAI import error has been fixed.
echo.
pause
