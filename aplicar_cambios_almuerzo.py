"""
Script para aplicar cambios en la tabla tipos_almuerzo
Agrega campos de componentes del almuerzo
"""
import os
import django
import sys

# Configurar Django
sys.path.append('D:/anteproyecto20112025')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def aplicar_cambios():
    """Aplica los cambios a la tabla tipos_almuerzo"""
    
    with connection.cursor() as cursor:
        print("=" * 60)
        print("APLICANDO CAMBIOS A tipos_almuerzo")
        print("=" * 60)
        
        # 1. Agregar columnas
        print("\n[1/4] Agregando columnas...")
        try:
            cursor.execute("""
                ALTER TABLE tipos_almuerzo
                ADD COLUMN Incluye_Plato_Principal BOOLEAN DEFAULT TRUE AFTER Precio_Unitario,
                ADD COLUMN Incluye_Postre BOOLEAN DEFAULT TRUE AFTER Incluye_Plato_Principal,
                ADD COLUMN Incluye_Bebida BOOLEAN DEFAULT TRUE AFTER Incluye_Postre
            """)
            print("✅ Columnas agregadas exitosamente")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("⚠️  Las columnas ya existen, continuando...")
            else:
                print(f"❌ Error: {e}")
                return False
        
        # 2. Desactivar tipos no usados
        print("\n[2/4] Desactivando tipos de almuerzo no usados...")
        cursor.execute("""
            UPDATE tipos_almuerzo 
            SET Activo = FALSE
            WHERE Nombre != 'Almuerzo Completo'
        """)
        filas = cursor.rowcount
        print(f"✅ {filas} tipos desactivados")
        
        # 3. Configurar Almuerzo Completo
        print("\n[3/4] Configurando 'Almuerzo Completo'...")
        cursor.execute("""
            UPDATE tipos_almuerzo 
            SET 
                Incluye_Plato_Principal = TRUE,
                Incluye_Postre = TRUE,
                Incluye_Bebida = TRUE,
                Descripcion = 'Plato principal + Postre + Jugo',
                Activo = TRUE
            WHERE Nombre = 'Almuerzo Completo'
        """)
        print("✅ Almuerzo Completo configurado")
        
        # 4. Verificar configuración
        print("\n[4/4] Verificando configuración...")
        cursor.execute("""
            SELECT 
                ID_Tipo_Almuerzo,
                Nombre,
                Descripcion,
                Precio_Unitario,
                Incluye_Plato_Principal,
                Incluye_Postre,
                Incluye_Bebida,
                Activo
            FROM tipos_almuerzo
            ORDER BY Activo DESC, ID_Tipo_Almuerzo
        """)
        
        resultados = cursor.fetchall()
        print("\n" + "=" * 120)
        print(f"{'ID':<5} {'Nombre':<25} {'Precio':<12} {'Plato':<8} {'Postre':<8} {'Bebida':<8} {'Activo':<8}")
        print("=" * 120)
        
        for row in resultados:
            id_tipo, nombre, desc, precio, plato, postre, bebida, activo = row
            print(f"{id_tipo:<5} {nombre:<25} Gs. {precio:>8,.0f} {plato!s:<8} {postre!s:<8} {bebida!s:<8} {activo!s:<8}")
        
        print("=" * 120)
        print("\n✅ CAMBIOS APLICADOS EXITOSAMENTE")
        print("\nNota: El precio del almuerzo puede modificarse desde:")
        print("      http://127.0.0.1:8000/pos/almuerzo/configurar-precio/")
        print("=" * 60)
        
        return True

if __name__ == '__main__':
    try:
        if aplicar_cambios():
            print("\n✅ Proceso completado. Puedes recargar la página del navegador.")
        else:
            print("\n❌ Hubo errores durante el proceso.")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
