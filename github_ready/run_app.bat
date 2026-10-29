@echo off
title Fake Profile Detection Platform
cd /d "%~dp0"
start http://127.0.0.1:8000
py -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause