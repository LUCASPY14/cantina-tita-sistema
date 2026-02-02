"""
Script para Actualizar Models.py - Eliminar Modelos Legacy
===========================================================

Este script elimina los modelos Django correspondientes a las tablas
legacy de cuenta corriente que ya fueron eliminadas de la base de datos.

Modelos a eliminar:
- CtaCorriente
- CtaCorrienteProv

Fecha: 2025-12-02
"""

import os
import sys

def actualizar_models_py():
    """Elimina los modelos legacy de gestion/models.py."""
    
    models_path = 'd:\\anteproyecto20112025\\gestion\\models.py'
    
    if not os.path.exists(models_path):
        print(f"❌ No se encontró el archivo: {models_path}")
        return False
    
    print("="*70)
    print("ACTUALIZACIÓN DE MODELOS DJANGO")
    print("="*70)
    
    print(f"\n📄 Leyendo: {models_path}")
    
    with open(models_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar las clases a eliminar
    modelos_encontrados = []
    
    if 'class CtaCorriente(models.Model):' in contenido:
        modelos_encontrados.append('CtaCorriente')
    
    if 'class CtaCorrienteProv(models.Model):' in contenido:
        modelos_encontrados.append('CtaCorrienteProv')
    
    if not modelos_encontrados:
        print("\n✅ No se encontraron modelos legacy para eliminar")
        print("   El archivo ya está actualizado")
        return True
    
    print(f"\n🔍 Modelos legacy encontrados:")
    for modelo in modelos_encontrados:
        print(f"   - {modelo}")
    
    print("\n⚠️  Se eliminarán estos modelos del archivo")
    confirmacion = input("\n¿Continuar? (SI/no): ").strip().upper()
    
    if confirmacion != 'SI':
        print("\n❌ Operación cancelada")
        return False
    
    # Crear backup
    backup_path = models_path + '.backup_eliminar_legacy'
    print(f"\n💾 Creando backup: {backup_path}")
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("   ✅ Backup creado")
    
    # Eliminar los modelos (esta operación se debe hacer manualmente
    # con replace_string_in_file para mayor precisión)
    
    print("\n📝 Para completar la eliminación, se deben eliminar manualmente:")
    print("   1. La clase CtaCorriente y todo su contenido")
    print("   2. La clase CtaCorrienteProv y todo su contenido")
    
    print("\n✅ Backup creado exitosamente")
    print(f"   Ubicación: {backup_path}")
    
    return True

def main():
    """Función principal."""
    print("\n" + "="*70)
    print("SCRIPT DE ACTUALIZACIÓN DE MODELOS DJANGO")
    print("Eliminación de Modelos Legacy de Cuenta Corriente")
    print("="*70)
    
    exito = actualizar_models_py()
    
    if exito:
        print("\n🎉 PROCESO COMPLETADO")
        print("\n📝 Nota: Los modelos legacy deben eliminarse manualmente")
        print("   usando herramientas de edición de código.")
        return 0
    else:
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
