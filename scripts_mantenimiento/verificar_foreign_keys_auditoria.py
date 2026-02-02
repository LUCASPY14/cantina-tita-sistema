#!/usr/bin/env python
"""
Script para verificar que las foreign keys de las tablas de auditoría
se hayan corregido correctamente (SET NULL en lugar de CASCADE)
"""

import os
import sys
import django
from pathlib import Path
from django.db import connection

# Agregar el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

def verificar_foreign_keys():
    """Verifica las foreign keys de las tablas de auditoría"""

    queries = {
        'auditoria_empleados': """
            SELECT
                rc.CONSTRAINT_NAME,
                kcu.COLUMN_NAME,
                kcu.REFERENCED_TABLE_NAME,
                kcu.REFERENCED_COLUMN_NAME,
                rc.DELETE_RULE
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                ON rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                AND rc.TABLE_NAME = kcu.TABLE_NAME
            WHERE rc.TABLE_NAME = 'auditoria_empleados'
                AND rc.CONSTRAINT_SCHEMA = DATABASE();
        """,

        'auditoria_usuarios_web': """
            SELECT
                rc.CONSTRAINT_NAME,
                kcu.COLUMN_NAME,
                kcu.REFERENCED_TABLE_NAME,
                kcu.REFERENCED_COLUMN_NAME,
                rc.DELETE_RULE
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                ON rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                AND rc.TABLE_NAME = kcu.TABLE_NAME
            WHERE rc.TABLE_NAME = 'auditoria_usuarios_web'
                AND rc.CONSTRAINT_SCHEMA = DATABASE();
        """,

        'auditoria_comisiones': """
            SELECT
                rc.CONSTRAINT_NAME,
                kcu.COLUMN_NAME,
                kcu.REFERENCED_TABLE_NAME,
                kcu.REFERENCED_COLUMN_NAME,
                rc.DELETE_RULE
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                ON rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
                AND rc.TABLE_NAME = kcu.TABLE_NAME
            WHERE rc.TABLE_NAME = 'auditoria_comisiones'
                AND rc.CONSTRAINT_SCHEMA = DATABASE();
        """
    }

    print("=== VERIFICACIÓN DE FOREIGN KEYS EN TABLAS DE AUDITORÍA ===\n")

    with connection.cursor() as cursor:
        for tabla, query in queries.items():
            print(f"Tabla: {tabla}")
            print("-" * 50)

            cursor.execute(query)
            resultados = cursor.fetchall()

            if resultados:
                print("Foreign Keys encontradas:")
                for resultado in resultados:
                    constraint, columna, tabla_ref, columna_ref, delete_rule = resultado
                    print(f"  - {constraint}: {columna} -> {tabla_ref}.{columna_ref} (ON DELETE {delete_rule})")
            else:
                print("  No se encontraron foreign keys no-CASCADE (posiblemente todas eliminadas)")

            print()

    # Verificar que las columnas permitan NULL
    print("=== VERIFICACIÓN DE COLUMNAS NULLABLES ===\n")

    null_checks = {
        'auditoria_empleados': "DESCRIBE auditoria_empleados;",
        'auditoria_usuarios_web': "DESCRIBE auditoria_usuarios_web;",
        'auditoria_comisiones': "DESCRIBE auditoria_comisiones;"
    }

    with connection.cursor() as cursor:
        for tabla, query in null_checks.items():
            print(f"Tabla: {tabla}")
            print("-" * 50)

            cursor.execute(query)
            columnas = cursor.fetchall()

            for col in columnas:
                field, tipo, null, key, default, extra = col
                if 'ID_' in field and field != 'ID_Auditoria':  # Solo campos de ID que podrían ser FK
                    nullable = null == 'YES'
                    print(f"  - {field}: NULL={nullable}")

            print()

if __name__ == '__main__':
    verificar_foreign_keys()