@echo off
title Flask Server - Student API
echo ================================================
echo Starting Student API Flask Server
echo ================================================
echo.
echo Server will be available at: http://127.0.0.1:5000
echo.
echo Available endpoints:
echo   GET  /health        - Health check
echo   POST /api/deploy    - Deploy application
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

python student_api.py

echo.
echo Server stopped.
pause
