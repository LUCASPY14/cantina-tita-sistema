@echo off
REM Script de desarrollo para Windows - Cantina Tita Sistema

echo.
echo 🚀 ========================================
echo    CANTINA TITA - ENTORNO DE DESARROLLO
echo ========================================
echo.

REM Verificar que Node.js está instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js no está instalado
    echo 📥 Instale Node.js desde: https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar que Python está disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está disponible
    echo 📥 Active el entorno virtual o instale Python
    pause
    exit /b 1
)

REM Verificar entorno virtual
if exist .venv\Scripts\activate.bat (
    echo ✅ Entorno virtual encontrado
) else (
    echo ⚠️  Entorno virtual no encontrado en .venv\
    echo 🔧 Cree el entorno virtual con: python -m venv .venv
)

REM Verificar dependencias frontend
if exist frontend\node_modules (
    echo ✅ Dependencias frontend instaladas
) else (
    echo 📦 Instalando dependencias frontend...
    cd frontend && npm install
    cd ..
)

echo.
echo 🔥 Iniciando servidores simultáneos...
echo 📡 Backend: http://localhost:8000/
echo 🎨 Frontend: http://localhost:3000/
echo.

REM Ejecutar desarrollo con concurrently
npm run dev

echo.
echo ⛔ Servidores detenidos
pause