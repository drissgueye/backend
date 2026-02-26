@echo off
REM Cree les documents de suivi pour les requetes existantes.
REM Double-cliquez ou exécutez depuis le dossier backendCnts avec le venv activé.

cd /d "%~dp0"

REM Si vous utilisez un venv dans le parent (cntsNew\.venv)
if exist "..\.venv\Scripts\activate.bat" (
    call "..\.venv\Scripts\activate.bat"
)
REM Si vous utilisez un venv dans ce dossier
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

python manage.py create_suivi_documents_for_requetes
pause
