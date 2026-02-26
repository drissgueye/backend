@echo off
cd /d "%~dp0"
title Backend Django - CNTS
if exist "..\.venv\Scripts\activate.bat" call "..\.venv\Scripts\activate.bat"
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"
echo Demarrage du serveur Django sur http://127.0.0.1:8000
echo.
python manage.py runserver 127.0.0.1:8000
pause
