#!/usr/bin/env python
"""
CONFIGURACIÓN DE BACKUP AUTOMÁTICO
Automáticamente configura backups en Windows (Task Scheduler) o Linux (Cron)
"""

import os
import sys
import subprocess
from pathlib import Path

def configurar_backup_windows():
    """Configurar backup en Windows Task Scheduler"""
    print("\n🪟 Configurando backup automático en WINDOWS...")
    print("─" * 70)
    
    # Ruta del script
    script_path = str(Path(__file__).parent / 'crear_backup_automatico.py')
    python_exe = sys.executable
    
    # Comando para crear tarea programada
    comando_tarea = f"""
schtasks /create /tn "Backup-CantinaBD" /tr "cd {Path(__file__).parent} && {python_exe} crear_backup_automatico.py backup" /sc daily /st 22:00 /f
"""
    
    print(f"Script a ejecutar: {script_path}")
    print(f"Python: {python_exe}")
    print(f"Horario: 22:00 (10:00 PM) todos los días")
    
    print("\n⚠️  PASOS MANUALES EN WINDOWS:")
    print("─" * 70)
    
    print("""
1. Abre "Programador de tareas" (Task Scheduler):
   - Presiona: Win + R
   - Escribe: taskschd.msc
   - Presiona: Enter

2. En el panel izquierdo, haz clic en "Crear tarea básica..."

3. Rellena los campos:
   
   GENERAL:
   • Nombre: Backup-CantinaBD
   • Descripción: Backup automático diario de la BD Cantina
   • Ejecutar con los privilegios más altos: ✓ (marcar)
   
   DESENCADENADOR:
   • Frecuencia: Diaria
   • Hora: 22:00 (o la que prefieras)
   • Repetir cada: 1 día
   
   ACCIÓN:
   • Programa/script: """ + python_exe + """
   • Argumentos (agregar): 
     crear_backup_automatico.py backup
   • Iniciar en (opcional):
     """ + str(Path(__file__).parent) + """

4. Haz clic en "Finalizar"

5. VERIFICACIÓN:
   • Abre la carpeta: ./backups/
   • Verifica que se crean archivos diarios
   • Ejemplo: backup_cantina_bd_20250109_220000.sql.gz
""")
    
    print("\n✅ ALTERNATIVA: Ejecutar automáticamente con PowerShell")
    print("─" * 70)
    
    print(f"""
Abre PowerShell como ADMINISTRADOR y ejecuta:

$trigger = New-ScheduledTaskTrigger -Daily -At 22:00
$action = New-ScheduledTaskAction -Execute "{python_exe}" -Argument "crear_backup_automatico.py backup" -WorkingDirectory "{Path(__file__).parent}"
Register-ScheduledTask -TaskName "Backup-CantinaBD" -Trigger $trigger -Action $action -RunLevel Highest
""")
    
    return True


def configurar_backup_linux():
    """Configurar backup en Linux con Cron"""
    print("\n🐧 Configurando backup automático en LINUX...")
    print("─" * 70)
    
    script_path = str(Path(__file__).parent / 'crear_backup_automatico.py')
    
    print(f"Script a ejecutar: {script_path}")
    print(f"Horario: 22:00 (10:00 PM) todos los días")
    
    print("\n⚠️  PASOS MANUALES EN LINUX:")
    print("─" * 70)
    
    print("""
1. Abre terminal y edita el archivo crontab:
   $ crontab -e

2. Agrega la siguiente línea (para ejecutar a las 22:00):
   0 22 * * * cd """ + str(Path(__file__).parent) + """ && python3 crear_backup_automatico.py backup

   O si usas virtual environment:
   0 22 * * * cd """ + str(Path(__file__).parent) + """ && source .venv/bin/activate && python crear_backup_automatico.py backup

3. Guarda y cierra (Ctrl+O, Enter, Ctrl+X en nano)

4. VERIFICACIÓN:
   • Ver tareas cron: crontab -l
   • Ver backups: ls -la backups/
   • Ver logs: grep CRON /var/log/syslog

5. NOTAS:
   • Cron no tiene PATH completo, mejor usar rutas absolutas
   • Redirige output a archivo si lo necesitas:
     0 22 * * * cd /home/usuario/cantina && python crear_backup_automatico.py backup >> cron_backup.log 2>&1
""")
    
    # Intenta crear el cron automáticamente (si el usuario permite)
    print("\n✅ CREACIÓN AUTOMÁTICA (Experimental):")
    print("─" * 70)
    
    try:
        # Verificar si crontab existe
        result = subprocess.run(['which', 'crontab'], capture_output=True)
        
        if result.returncode == 0:
            print("crontab encontrado, intentando crear entrada...")
            
            cron_line = f"0 22 * * * cd {Path(__file__).parent} && python3 crear_backup_automatico.py backup\n"
            
            # Leer crontab actual
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_crontab = result.stdout if result.returncode == 0 else ""
            
            # Verificar si ya existe
            if "crear_backup_automatico.py" in current_crontab:
                print("⚠️  El backup ya está configurado en cron")
            else:
                # Crear nuevo crontab
                new_crontab = current_crontab + cron_line
                
                # Escribir nuevo crontab
                process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
                process.communicate(new_crontab)
                
                if process.returncode == 0:
                    print("✅ Crontab configurado exitosamente!")
                    print(f"   Línea agregada: {cron_line}")
                else:
                    print("❌ Error al configurar crontab")
        else:
            print("crontab no encontrado, seguir pasos manuales")
            
    except Exception as e:
        print(f"No se pudo configurar automáticamente: {e}")
        print("Sigue los pasos manuales arriba")
    
    return True


def mostrar_menu():
    """Mostrar menú principal"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║            ⚙️  CONFIGURACIÓN DE BACKUP AUTOMÁTICO                          ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

¿En qué sistema operativo estás?

1. Windows (Usa Task Scheduler)
2. Linux (Usa Cron)
3. Ambos (mostrar ambos)
0. Salir
""")


def main():
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSelecciona una opción (0-3): ").strip()
            
            if opcion == "0":
                print("\n✅ Saliendo...")
                break
            
            elif opcion == "1":
                configurar_backup_windows()
                input("\n\nPresiona Enter para continuar...")
                
            elif opcion == "2":
                configurar_backup_linux()
                input("\n\nPresiona Enter para continuar...")
                
            elif opcion == "3":
                configurar_backup_windows()
                print("\n")
                configurar_backup_linux()
                input("\n\nPresiona Enter para continuar...")
            
            else:
                print("\n❌ Opción inválida")
                
        except KeyboardInterrupt:
            print("\n\n✅ Cancelado por el usuario")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                   🔄 BACKUP AUTOMÁTICO - CONFIGURACIÓN                     ║
║                                                                            ║
║  Este script ayuda a configurar backups automáticos diarios de la BD       ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    main()
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                        ✅ CONFIGURACIÓN COMPLETADA                         ║
║                                                                            ║
║  Próximos pasos:                                                          ║
║  1. Verifica que el backup se ejecute automáticamente                     ║
║  2. Revisa la carpeta ./backups/ diariamente                              ║
║  3. Prueba la restauración: python crear_backup_automatico.py restaurar   ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
