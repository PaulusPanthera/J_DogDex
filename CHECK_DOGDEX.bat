@echo off
cd /d "%~dp0"
"%~dp0runtime\python.exe" -X utf8 "%~dp0tools\check_project.py" --output "%~dp0my_collection\checks\latest.json"
pause
