#!/usr/bin/env python
"""Drop and recreate the MySQL database defined in settings/.env."""
from pathlib import Path
import sys

import MySQLdb
from decouple import Config, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR.parent / '.env'
config = Config(RepositoryEnv(str(ENV_PATH)) if ENV_PATH.exists() else None)

DB_NAME = config('DB_NAME', default='cantinatitadb')
DB_USER = config('DB_USER', default='root')
DB_PASSWORD = config('DB_PASSWORD', default='')
DB_HOST = config('DB_HOST', default='localhost')
DB_PORT = config('DB_PORT', default=3306, cast=int)

print(f"⚠️  Eliminando base de datos '{DB_NAME}' en {DB_HOST}:{DB_PORT}...")

def main():
    try:
        conn = MySQLdb.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            port=DB_PORT,
            charset='utf8mb4',
            use_unicode=True,
        )
    except MySQLdb.MySQLError as exc:
        print(f"No se pudo conectar a MySQL: {exc}")
        sys.exit(1)

    conn.autocommit(True)
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS `{DB_NAME}`;")
    cursor.execute(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.close()
    conn.close()
    print(f"✅ Base '{DB_NAME}' recreada.")


if __name__ == '__main__':
    main()
