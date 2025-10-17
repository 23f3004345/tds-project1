@echo off
echo Committing and pushing fixes for Render deployment...
git add .
git commit -m "Fix deployment: make LLM provider imports conditional and fix env file"
git push
echo.
echo Done! Check your Render dashboard - deployment should work now.
pause

