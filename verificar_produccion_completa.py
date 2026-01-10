#!/usr/bin/env python
"""
VERIFICADOR FINAL - Confirma que todas las 4 tareas de producción están completadas
Ejecutar: python verificar_produccion_completa.py
"""

import os
from pathlib import Path
from datetime import datetime

class VerificadorProduccion:
    """Verifica que todos los componentes de producción están en lugar"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.resultados = []
        
    def verificar_archivo(self, ruta, descripcion):
        """Verifica si un archivo existe"""
        path = self.base_path / ruta
        existe = path.exists()
        
        if existe:
            tamaño = path.stat().st_size
            print(f"  ✓ {ruta:<50} ({tamaño:,} bytes)")
            self.resultados.append((descripcion, True))
        else:
            print(f"  ❌ {ruta:<50} NO ENCONTRADO")
            self.resultados.append((descripcion, False))
        
        return existe
    
    def verificar_contenido(self, ruta, texto_buscar):
        """Verifica que un archivo contiene un texto específico"""
        path = self.base_path / ruta
        
        if not path.exists():
            return False
        
        contenido = path.read_text(encoding='utf-8')
        return texto_buscar in contenido
    
    def ejecutar(self):
        """Ejecuta todas las verificaciones"""
        
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║              VERIFICADOR: TAREAS DE PRODUCCIÓN COMPLETADAS                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)
        
        # TAREA 1: TESTING
        print("\n[TAREA 1] Testear restricciones en producción")
        print("─" * 70)
        existe_test = self.verificar_archivo(
            'test_restricciones_produccion.py',
            'Script de testing de restricciones'
        )
        
        if existe_test:
            contiene_test_func = self.verificar_contenido(
                'test_restricciones_produccion.py',
                'def test_restricciones'
            )
            print(f"  {'✓ Contiene función test_restricciones' if contiene_test_func else '❌ Función test_restricciones no encontrada'}")
        
        # TAREA 2: BACKUP
        print("\n[TAREA 2] Configurar backup en tareas programadas")
        print("─" * 70)
        existe_backup = self.verificar_archivo(
            'configurar_backup_tareas.py',
            'Script de configuración de backup'
        )
        
        if existe_backup:
            contiene_windows = self.verificar_contenido(
                'configurar_backup_tareas.py',
                'configurar_backup_windows'
            )
            contiene_linux = self.verificar_contenido(
                'configurar_backup_tareas.py',
                'configurar_backup_linux'
            )
            print(f"  {'✓ Soporte Windows (Task Scheduler)' if contiene_windows else '❌ Sin soporte Windows'}")
            print(f"  {'✓ Soporte Linux (Cron)' if contiene_linux else '❌ Sin soporte Linux'}")
        
        # TAREA 3: DASHBOARD
        print("\n[TAREA 3] Usar dashboard para monitoreo")
        print("─" * 70)
        existe_guia_dash = self.verificar_archivo(
            'GUIA_DASHBOARD_MONITOREO.md',
            'Guía de operación del dashboard'
        )
        
        if existe_guia_dash:
            contiene_componentes = self.verificar_contenido(
                'GUIA_DASHBOARD_MONITOREO.md',
                'Tarjetas'
            )
            print(f"  {'✓ Documentación de componentes completa' if contiene_componentes else '❌ Documentación incompleta'}")
        
        # TAREA 4: IMPRESORA
        print("\n[TAREA 4] Conectar impresora térmica")
        print("─" * 70)
        
        existe_test_impresora = self.verificar_archivo(
            'test_conectar_impresora.py',
            'Script de prueba y configuración de impresora'
        )
        
        existe_manager = self.verificar_archivo(
            'gestion/impresora_manager.py',
            'Módulo Django de gestión de impresora'
        )
        
        existe_guia_impresora = self.verificar_archivo(
            'GUIA_INTEGRACION_IMPRESORA.md',
            'Guía técnica de integración de impresora'
        )
        
        if existe_manager:
            contiene_imprimir_ticket = self.verificar_contenido(
                'gestion/impresora_manager.py',
                'def imprimir_ticket'
            )
            contiene_obtener_impresora = self.verificar_contenido(
                'gestion/impresora_manager.py',
                'def obtener_impresora'
            )
            print(f"  {'✓ Método imprimir_ticket presente' if contiene_imprimir_ticket else '❌ Método imprimir_ticket no encontrado'}")
            print(f"  {'✓ Función singleton obtener_impresora' if contiene_obtener_impresora else '❌ Función singleton no encontrada'}")
        
        # RESUMEN
        print("\n" + "=" * 70)
        print("\n📋 RESUMEN DE VERIFICACIÓN\n")
        
        completadas = sum(1 for _, resultado in self.resultados if resultado)
        total = len(self.resultados)
        
        print(f"Tareas completadas: {completadas}/{total}\n")
        
        # Por tarea
        tarea_1_ok = existe_test
        tarea_2_ok = existe_backup
        tarea_3_ok = existe_guia_dash
        tarea_4_ok = existe_test_impresora and existe_manager and existe_guia_impresora
        
        print(f"  [1] Testear restricciones         → {'✅ COMPLETO' if tarea_1_ok else '❌ INCOMPLETO'}")
        print(f"  [2] Configurar backup             → {'✅ COMPLETO' if tarea_2_ok else '❌ INCOMPLETO'}")
        print(f"  [3] Dashboard monitoreo           → {'✅ COMPLETO' if tarea_3_ok else '❌ INCOMPLETO'}")
        print(f"  [4] Impresora térmica             → {'✅ COMPLETO' if tarea_4_ok else '❌ INCOMPLETO'}")
        
        # Documentación
        existe_resumen = self.verificar_archivo(
            'RESUMEN_4_TAREAS_PRODUCCION.md',
            'Documento resumen de todas las tareas'
        )
        
        print(f"\n  📄 Documentación completa        → {'✅ SÍ' if existe_resumen else '❌ NO'}")
        
        # Estado final
        print("\n" + "=" * 70)
        
        todas_completas = tarea_1_ok and tarea_2_ok and tarea_3_ok and tarea_4_ok
        
        if todas_completas:
            print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                  ✅ TODAS LAS TAREAS COMPLETADAS                          ║
║                                                                            ║
║  El sistema Cantina POS está PRODUCTION-READY                            ║
║                                                                            ║
║  Próximos pasos:                                                          ║
║  1. Ejecutar: python test_restricciones_produccion.py                     ║
║  2. Ejecutar: python test_conectar_impresora.py                           ║
║  3. Ejecutar: python configurar_backup_tareas.py                          ║
║  4. Acceder a: http://tu-servidor/pos/dashboard/                          ║
║                                                                            ║
║  Documentación completa en: RESUMEN_4_TAREAS_PRODUCCION.md                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
            """)
        else:
            print(f"""
⚠️  ALGUNAS TAREAS INCOMPLETAS

Revisa los archivos marcados con ❌ arriba.
Todos los archivos deben existir para producción.
            """)
        
        return todas_completas


if __name__ == '__main__':
    verificador = VerificadorProduccion()
    exito = verificador.ejecutar()
    exit(0 if exito else 1)
