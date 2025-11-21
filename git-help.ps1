# ============================================
# Script de Ayuda Rápida - Git & GitHub
# ============================================

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "   GIT & GITHUB - COMANDOS RÁPIDOS   " -ForegroundColor White -BackgroundColor DarkCyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Función para mostrar comando y descripción
function Show-Command {
    param($cmd, $desc)
    Write-Host "  $cmd" -ForegroundColor Yellow
    Write-Host "    → $desc`n" -ForegroundColor Gray
}

Write-Host "📊 ESTADO Y VISUALIZACIÓN:" -ForegroundColor Green
Show-Command "git status" "Ver archivos modificados"
Show-Command "git log --oneline" "Ver historial de commits"
Show-Command "git log --oneline -n 5" "Ver últimos 5 commits"
Show-Command "git diff" "Ver cambios en archivos"

Write-Host "📝 HACER CAMBIOS:" -ForegroundColor Green
Show-Command "git add ." "Agregar todos los archivos"
Show-Command "git add archivo.py" "Agregar archivo específico"
Show-Command 'git commit -m "mensaje"' "Hacer commit con mensaje"
Show-Command "git commit -am 'mensaje'" "Add + commit en un paso"

Write-Host "🔄 SINCRONIZAR CON GITHUB:" -ForegroundColor Green
Show-Command "git push" "Subir cambios a GitHub"
Show-Command "git pull" "Bajar cambios de GitHub"
Show-Command "git fetch" "Ver cambios sin aplicarlos"

Write-Host "🌿 RAMAS:" -ForegroundColor Green
Show-Command "git branch" "Ver todas las ramas"
Show-Command "git checkout -b nueva-rama" "Crear y cambiar a nueva rama"
Show-Command "git checkout main" "Cambiar a rama main"
Show-Command "git merge feature/rama" "Fusionar rama en la actual"

Write-Host "🔗 CONFIGURACIÓN REMOTA:" -ForegroundColor Green
Show-Command "git remote -v" "Ver repositorios remotos"
Show-Command "git remote add origin [URL]" "Conectar con GitHub"

Write-Host "⚠️  DESHACER CAMBIOS:" -ForegroundColor Red
Show-Command "git restore archivo.py" "Descartar cambios en archivo"
Show-Command "git restore ." "Descartar todos los cambios"
Show-Command "git reset HEAD~1" "Deshacer último commit (mantener cambios)"
Show-Command "git reset --hard HEAD~1" "Deshacer último commit (borrar cambios)"

Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "💡 TIPS:" -ForegroundColor Yellow
Write-Host "  • Haz commits frecuentes con mensajes descriptivos" -ForegroundColor Gray
Write-Host "  • Usa 'git pull' antes de 'git push'" -ForegroundColor Gray
Write-Host "  • Revisa 'git status' antes de hacer commit" -ForegroundColor Gray
Write-Host "  • Nunca subas archivos con contraseñas (.env)`n" -ForegroundColor Gray

Write-Host "📖 Más información: GUIA_GITHUB.md`n" -ForegroundColor Cyan
