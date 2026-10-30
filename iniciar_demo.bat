@echo off
chcp 65001 >nul
title Conferencia Operacoes (demo)
cd /d "%~dp0"
pip install -r requirements.txt -r requirements-demo.txt
python app.py --demo
pause
