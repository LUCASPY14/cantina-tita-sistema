"""
Script para crear la tabla de restricciones alimentarias de hijos

Este script crea la estructura necesaria para registrar restricciones
alimentarias (alergias, intolerancias, dietas especiales) de los estudiantes.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

def crear_tabla_restricciones():
    """Crear tabla restricciones_hijos"""
    print("\n" + "="*70)
    print("CREANDO TABLA DE RESTRICCIONES ALIMENTARIAS")
    print("="*70)
    
    with connection.cursor() as cursor:
        # Verificar si la tabla ya existe
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'cantinatitadb' 
            AND TABLE_NAME = 'restricciones_hijos'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("\n⚠️  La tabla restricciones_hijos ya existe")
            respuesta = input("¿Deseas recrearla? (s/N): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada")
                return False
            
            cursor.execute("DROP TABLE IF EXISTS restricciones_hijos")
            print("✅ Tabla anterior eliminada")
        
        # Crear tabla
        sql = """
        CREATE TABLE restricciones_hijos (
            ID_Restriccion INT AUTO_INCREMENT PRIMARY KEY,
            ID_Hijo INT NOT NULL,
            Tipo_Restriccion VARCHAR(100) NOT NULL COMMENT 'Tipo: Celíaco, Intolerancia lactosa, Alergia maní, etc.',
            Descripcion TEXT COMMENT 'Descripción detallada de la restricción',
            Observaciones TEXT COMMENT 'Observaciones adicionales o ingredientes específicos a evitar',
            Severidad ENUM('Leve', 'Moderada', 'Severa', 'Crítica') DEFAULT 'Moderada',
            Requiere_Autorizacion BOOLEAN DEFAULT TRUE COMMENT 'Si requiere autorización para consumir productos restringidos',
            Fecha_Registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            Fecha_Ultima_Actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            Activo BOOLEAN DEFAULT TRUE,
            
            CONSTRAINT FK_Restriccion_Hijo 
                FOREIGN KEY (ID_Hijo) REFERENCES hijos(ID_Hijo)
                ON DELETE CASCADE,
                
            INDEX idx_hijo (ID_Hijo),
            INDEX idx_tipo (Tipo_Restriccion),
            INDEX idx_activo (Activo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        COMMENT='Restricciones alimentarias de los estudiantes (alergias, intolerancias, dietas especiales)';
        """
        
        cursor.execute(sql)
        print("\n✅ Tabla restricciones_hijos creada exitosamente")
        
        # Insertar datos de ejemplo
        print("\n📝 Insertando datos de ejemplo...")
        
        # Obtener IDs de hijos existentes
        cursor.execute("SELECT ID_Hijo, Nombre, Apellido FROM hijos WHERE Activo = TRUE LIMIT 5")
        hijos = cursor.fetchall()
        
        if not hijos:
            print("⚠️  No hay hijos registrados. Omitiendo datos de ejemplo.")
            return True
        
        restricciones_ejemplo = [
            {
                'tipo': 'Celíaco',
                'descripcion': 'No puede consumir gluten (trigo, avena, cebada, centeno)',
                'observaciones': 'Evitar: pan, pasta, galletas, pizza, empanadas',
                'severidad': 'Severa'
            },
            {
                'tipo': 'Intolerancia a la lactosa',
                'descripcion': 'Dificultad para digerir lácteos',
                'observaciones': 'Evitar: leche, queso, yogur, crema, helados',
                'severidad': 'Moderada'
            },
            {
                'tipo': 'Alergia al maní',
                'descripcion': 'Alergia severa a maní y derivados',
                'observaciones': 'Evitar: maní, mantequilla de maní, productos que contengan trazas',
                'severidad': 'Crítica'
            },
            {
                'tipo': 'Vegetariano',
                'descripcion': 'No consume carne ni derivados de animales',
                'observaciones': 'Evitar: carne, pollo, pescado, embutidos',
                'severidad': 'Leve'
            },
            {
                'tipo': 'Diabetes',
                'descripcion': 'Debe controlar ingesta de azúcares',
                'observaciones': 'Evitar: dulces, gaseosas, jugos azucarados, postres',
                'severidad': 'Moderada'
            }
        ]
        
        # Insertar una restricción para cada hijo de ejemplo
        for i, hijo in enumerate(hijos[:5]):
            if i < len(restricciones_ejemplo):
                restriccion = restricciones_ejemplo[i]
                
                cursor.execute("""
                    INSERT INTO restricciones_hijos 
                    (ID_Hijo, Tipo_Restriccion, Descripcion, Observaciones, Severidad, Activo)
                    VALUES (%s, %s, %s, %s, %s, TRUE)
                """, (
                    hijo[0],  # ID_Hijo
                    restriccion['tipo'],
                    restriccion['descripcion'],
                    restriccion['observaciones'],
                    restriccion['severidad']
                ))
                
                print(f"  ✅ {hijo[1]} {hijo[2]}: {restriccion['tipo']} ({restriccion['severidad']})")
        
        print("\n✅ Datos de ejemplo insertados")
        
        # Mostrar resumen
        cursor.execute("SELECT COUNT(*) FROM restricciones_hijos WHERE Activo = TRUE")
        total = cursor.fetchone()[0]
        
        print(f"\n📊 Total de restricciones activas: {total}")
        
        # Mostrar distribución por tipo
        cursor.execute("""
            SELECT Tipo_Restriccion, COUNT(*) as total
            FROM restricciones_hijos
            WHERE Activo = TRUE
            GROUP BY Tipo_Restriccion
            ORDER BY total DESC
        """)
        
        print("\n📈 Distribución por tipo:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")
        
        print("\n" + "="*70)
        print("✅ TABLA CREADA Y CONFIGURADA EXITOSAMENTE")
        print("="*70)
        
        return True


if __name__ == '__main__':
    try:
        if crear_tabla_restricciones():
            print("\n✅ Proceso completado exitosamente")
        else:
            print("\n❌ Proceso cancelado")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
