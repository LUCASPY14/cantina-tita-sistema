@echo off
REM Script de desarrollo para Windows

echo 🚀 Iniciando entorno de desarrollo Cantina Tita...

REM Activar entorno virtual si existe
if exist .venv\Scripts\activate.bat (
    echo 🐍 Activando entorno virtual...
    call .venv\Scripts\activate.bat
)

REM Ejecutar servidor de desarrollo
python dev_server.py %*