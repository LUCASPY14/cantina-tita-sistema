# Script de gestión para el proyecto Django
# Ejecuta este script con: . .\run.ps1 <comando>

param(
    [Parameter(Position=0)]
    [string]$Comando = "help"
)

$python = "D:/anteproyecto20112025/.venv/Scripts/python.exe"

switch ($Comando) {
    "migrate" {
        Write-Host "Aplicando migraciones..." -ForegroundColor Green
        & $python manage.py migrate
    }
    "makemigrations" {
        Write-Host "Creando migraciones..." -ForegroundColor Green
        & $python manage.py makemigrations
    }
    "superuser" {
        Write-Host "Creando superusuario..." -ForegroundColor Green
        & $python manage.py createsuperuser
    }
    "runserver" {
        Write-Host "Iniciando servidor de desarrollo..." -ForegroundColor Green
        & $python manage.py runserver
    }
    "shell" {
        Write-Host "Iniciando shell de Django..." -ForegroundColor Green
        & $python manage.py shell
    }
    "test" {
        Write-Host "Ejecutando pruebas..." -ForegroundColor Green
        & $python manage.py test
    }
    default {
        Write-Host @"
╔═══════════════════════════════════════════════════════════╗
║    Sistema de Gestión de Cantina - Scripts de Ayuda      ║
╚═══════════════════════════════════════════════════════════╝

Uso: .\run.ps1 <comando>

Comandos disponibles:

  makemigrations  - Crear migraciones de la base de datos
  migrate         - Aplicar migraciones a la base de datos
  superuser       - Crear un superusuario para el admin
  runserver       - Iniciar el servidor de desarrollo
  shell           - Abrir shell interactivo de Django
  test            - Ejecutar pruebas del proyecto

Ejemplos:
  .\run.ps1 migrate
  .\run.ps1 runserver
  .\run.ps1 superuser

"@ -ForegroundColor Cyan
    }
}
