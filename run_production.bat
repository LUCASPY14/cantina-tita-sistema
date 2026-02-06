@echo off
REM ================================================================
REM Script para ejecutar Cantina Tita en producción (Windows)
REM ================================================================

echo.
echo ========================================
echo   CANTINA TITA - SERVIDOR DE PRODUCCION
echo ========================================
echo.
echo Servidor: 192.168.100.10:8000
echo Entorno: Produccion
echo WSGI: Waitress
echo.

REM Cambiar al directorio backend
cd /d "%~dp0backend"

REM Activar entorno virtual y ejecutar Waitress
echo [INFO] Iniciando servidor Waitress...
echo [INFO] Acceso: http://192.168.100.10:8000
echo [INFO] Admin: http://192.168.100.10:8000/admin
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

..\.venv\Scripts\waitress-serve --host=0.0.0.0 --port=8000 --threads=4 cantina_project.wsgi:application

pause
