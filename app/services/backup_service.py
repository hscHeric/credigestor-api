from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime
from typing import Iterable, List, Tuple

from sqlalchemy import text
from sqlalchemy.engine import Engine


def _list_tables(engine: Engine, schema: str = "public") -> List[str]:
    q = text(
        """
        SELECT tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname = :schema
        ORDER BY tablename;
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(q, {"schema": schema}).fetchall()
    return [r[0] for r in rows]


def _copy_table_csv(engine: Engine, table: str, schema: str = "public") -> bytes:
    """
    Faz COPY da tabela para CSV (com header) via TO STDOUT.
    Evita pg_dump. Retorna bytes do CSV.
    """
    sql = f'COPY "{schema}"."{table}" TO STDOUT WITH CSV HEADER'

    # pega conexão DBAPI (psycopg2/psycopg) por baixo do SQLAlchemy
    with engine.raw_connection() as raw:
        cur = raw.cursor()
        buf = io.StringIO()

        # psycopg2 tem copy_expert; psycopg3 tem copy também (mas nem sempre)
        if hasattr(cur, "copy_expert"):
            cur.copy_expert(sql, buf)
        else:
            # fallback: tenta executar COPY via cursor.copy (psycopg3)
            copy = cur.copy(sql)  # type: ignore[attr-defined]
            for row in copy.rows():  # type: ignore[attr-defined]
                buf.write(row)

        cur.close()

    return buf.getvalue().encode("utf-8")


def build_backup_zip(engine: Engine, schema: str = "public") -> Tuple[str, bytes]:
    """
    Gera um .zip em memória contendo:
      - manifest.json
      - data/<table>.csv para cada tabela do schema
    Retorna (filename, bytes_zip).
    """
    tables = _list_tables(engine, schema=schema)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"credigestor_backup_{ts}.zip"

    manifest = {
        "generated_at": datetime.now().isoformat(),
        "schema": schema,
        "tables": tables,
        "format": "zip+csv",
        "notes": "Backup lógico (dados) via COPY TO STDOUT. Requer restauração por importação dos CSVs.",
    }

    out = io.BytesIO()
    with zipfile.ZipFile(out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

        for t in tables:
            csv_bytes = _copy_table_csv(engine, t, schema=schema)
            zf.writestr(f"data/{t}.csv", csv_bytes)

    return filename, out.getvalue()
