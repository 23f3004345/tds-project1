@echo off
echo Starting Flask Server...
echo.
python -c "print('Testing configuration...')"
python -c "import config; print('LLM Provider:', config.LLM_PROVIDER); print('Port:', config.API_PORT)"
echo.
echo Starting server on http://127.0.0.1:5000
echo Press Ctrl+C to stop
echo.
python student_api.py
pause

