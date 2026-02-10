import sys
import traceback
import argparse
from pathlib import Path

import os
import django
from django.conf import settings
from django.db import (
    connection,
    OperationalError as DjangoOperationalError,
    ProgrammingError as DjangoProgrammingError,
)
from MySQLdb import OperationalError, ProgrammingError

# Ruta del SQL generado por sqlmigrate gestion 0002 (valor por defecto)
DEFAULT_SQL_PATH = Path(__file__).resolve().parent.parent / "create_sql_0002.sql"

# Códigos de error que se ignoran porque indican que ya existe
IGNORE_ERRORS = {
    1050,  # Table already exists
    1060,  # Duplicate column name
    1061,  # Duplicate key name
    1068,  # Multiple primary key defined
    1091,  # Can't DROP ... check that column/key exists
    1146,  # Table doesn't exist (para alter sobre tablas que aún no están)
}

def load_sql_statements(path: Path):
    if not path.exists():
        print(f"No se encontró el archivo SQL: {path}")
        sys.exit(1)
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if "\x00" in raw:
        raw = path.read_text(encoding="utf-16", errors="ignore")
    # Eliminamos líneas de señalización que no son SQL
    cleaned = []
    for line in raw.splitlines():
        # filtramos cualquier línea que tenga marcadores o corchetes iniciales
        if "[SIGNALS" in line or line.strip().startswith("["):
            continue
        cleaned.append(line)
    sql_text = "\n".join(cleaned)
    # Dividir por punto y coma; cuidamos vacíos
    stmts = [s.strip() for s in sql_text.split(";") if s.strip()]
    return stmts


def apply_sql(sql_path: Path):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cantina_project.settings")
    django.setup()
    stmts = load_sql_statements(sql_path)
    print(f"Aplicando SQL desde {sql_path}")
    print(f"Cargadas {len(stmts)} sentencias antes de filtrar")
    for i in range(min(3, len(stmts))):
        print(f"Sentencia cruda {i}: {repr(stmts[i][:120])}")
    allowed_patterns = (
        "ALTER TABLE `",
        "CREATE TABLE `",
        "CREATE INDEX `",
        "ALTER INDEX `",
        "DROP TABLE `",
        "INSERT INTO `",
        "SET @",
        "SET SQL",
    )

    filtered = []
    debug_shown = 0
    for stmt in stmts:
        upper_stmt = stmt.upper()
        start = None
        for keyword in allowed_patterns:
            pos = upper_stmt.find(keyword)
            if pos != -1 and (start is None or pos < start):
                start = pos
        if start is None:
            continue
        body = stmt[start:].strip()
        if debug_shown < 5:
            print("\nCandidato bruto:\n" + body[:200])
            debug_shown += 1
        filtered.append(body)
    stmts = filtered
    print(f"Aplicando {len(stmts)} sentencias después de filtrar")
    total = len(stmts)
    ok, skipped = 0, 0
    with connection.cursor() as cursor:
        for idx, stmt in enumerate(stmts, 1):
            try:
                cursor.execute(stmt)
                ok += 1
            except (OperationalError, ProgrammingError, DjangoOperationalError, DjangoProgrammingError) as exc:  # MySQL/Django errors
                code = getattr(exc, "args", [None])[0]
                if isinstance(code, str) and code.isdigit():
                    code = int(code)
                if code in IGNORE_ERRORS:
                    skipped += 1
                    continue
                print(f"\n❌ Error en sentencia #{idx}/{total} (código {code}):\n{stmt}\n")
                traceback.print_exc()
                sys.exit(1)
    print(f"\n✅ SQL aplicado. Ejecutadas: {ok}, Omitidas por existir: {skipped}, Total: {total}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aplica SQL generado por sqlmigrate tolerando errores de objetos existentes")
    parser.add_argument("sql_file", nargs="?", default=str(DEFAULT_SQL_PATH), help="Ruta al archivo SQL a ejecutar")
    args = parser.parse_args()
    apply_sql(Path(args.sql_file))
