@echo off
echo Setting up PetPoint Automation Environment
echo =========================================

REM Create virtual environment
echo Creating virtual environment...
python -m venv petpoint_env

REM Activate virtual environment
echo Activating virtual environment...
call petpoint_env\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements_petpoint.txt

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file template...
    (
        echo # PetPoint Automation Environment Variables
        echo # Fill in your actual credentials below
        echo.
        echo PETPOINT_USER=your_username_here
        echo PETPOINT_PASS=your_password_here
        echo PETPOINT_BASE_URL=https://your-petpoint-instance.com
    ) > .env
    echo Created .env file. Please edit it with your actual credentials.
) else (
    echo .env file already exists.
)

echo.
echo Setup complete! Next steps:
echo 1. Edit .env file with your PetPoint credentials
echo 2. Update selectors in pull_petpoint_reports.py based on your PetPoint instance
echo 3. Run: python pull_petpoint_reports.py
echo.
echo To activate the environment in the future:
echo petpoint_env\Scripts\activate.bat
pause
