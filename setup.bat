@echo off
echo Setting up LLM Code Deployment System...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium

REM Copy example env file
if not exist .env (
    echo Creating .env file from example...
    copy .env.example .env
    echo Please edit .env file with your configuration
)

REM Initialize database
echo Initializing database...
python init_db.py

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your API keys and configuration
echo 2. For students: Run 'python student_api.py' to start the student API
echo 3. For instructors: Run 'python evaluation_api.py' to start the evaluation API
echo.
pause

