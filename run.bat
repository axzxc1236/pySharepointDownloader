@echo off
cd /D "%~dp0"
if not exist venv (
    python -m venv venv
    call %cd%\venv\Scripts\activate.bat
    pip install requests
)
call %cd%\venv\Scripts\activate.bat
python cli.py
pause