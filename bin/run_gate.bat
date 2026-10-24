@echo off
rem Запуск управления модулем "Шлагбаум"
cd /d "%~dp0..\src\gate"
python gate.py
pause