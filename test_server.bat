@echo off
cd d:\anteproyecto20112025
start /B .venv\Scripts\python.exe manage.py runserver 8000 --noreload
timeout /t 5 /nobreak > nul
.venv\Scripts\python.exe prueba_rapida.py