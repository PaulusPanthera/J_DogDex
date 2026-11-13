@echo off
cd /d "%~dp0"
title DogDex - Local Collection
"%~dp0runtime\python.exe" -X utf8 "%~dp0app.py"
if errorlevel 1 (
  echo.
  echo DogDex could not start. Keep this window open and share the error above.
  pause
)
