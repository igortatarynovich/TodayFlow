"""Database migration utilities."""

import logging
import re
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, ProgrammingError

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def _rewrite_sqlite_migration_sql(sql: str) -> str:
    """PostgreSQL-oriented .sql files: minimal rewrites so SQLite can execute DDL."""
    sql = re.sub(
        r"\bADD\s+COLUMN\s+IF\s+NOT\s+EXISTS\b",
        "ADD COLUMN",
        sql,
        flags=re.IGNORECASE,
    )
    # PL/pgSQL blocks (e.g. conditional ADD COLUMN) — SQLite не поддерживает
    sql = re.sub(
        r"DO\s*\$\$[\s\S]*?\bEND\s*\$\$\s*;",
        "",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r"\bSERIAL\s+PRIMARY\s+KEY\b",
        "INTEGER PRIMARY KEY AUTOINCREMENT",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(r"\bJSONB\b", "TEXT", sql, flags=re.IGNORECASE)
    return sql


def _strip_leading_comment_lines(stmt: str) -> str:
    lines: list[str] = []
    for line in stmt.splitlines():
        stripped = line.strip()
        if not lines and (not stripped or stripped.startswith("--")):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _split_sql_statements(sql: str) -> list[str]:
    """
    Разбить скрипт на отдельные выражения по строкам, заканчивающимся на ';'.
    Подходит для DDL-миграций в репозитории (без ';' внутри строк в конце строки).
    """
    sql = sql.replace("\r\n", "\n").strip()
    if not sql:
        return []
    statements: list[str] = []
    buffer: list[str] = []
    for line in sql.split("\n"):
        buffer.append(line)
        if line.rstrip().endswith(";"):
            chunk = "\n".join(buffer).strip()
            if chunk:
                statements.append(chunk)
            buffer = []
    if buffer:
        tail = "\n".join(buffer).strip()
        if tail:
            statements.append(tail)
    return statements


def _sqlite_expand_alter_table_add_columns(stmt: str) -> list[str]:
    """
    SQLite: в одном ``ALTER TABLE`` только один ``ADD COLUMN``.
    Разворачиваем PostgreSQL-стиль ``ADD … , ADD …`` в несколько ``ALTER``.
    """
    s = _strip_leading_comment_lines(stmt)
    if not s or not re.match(r"^\s*ALTER\s+TABLE\s+\S+", s, re.I):
        return [stmt]
    if not re.search(r",\s*ADD\s+COLUMN\s+", s, re.I):
        return [stmt]
    m = re.match(r"^\s*ALTER\s+TABLE\s+(\S+)\s+(.*)$", s, re.I | re.DOTALL)
    if not m:
        return [stmt]
    table, body = m.group(1), m.group(2).strip().rstrip(";")
    body = re.sub(r"^ADD\s+COLUMN\s+", "", body, count=1, flags=re.I)
    segments = re.split(r",\s*ADD\s+COLUMN\s+", body, flags=re.I)
    outs = [
        f"ALTER TABLE {table} ADD COLUMN {seg.strip().rstrip(',')};"
        for seg in segments
        if seg.strip()
    ]
    return outs if outs else [stmt]


def _sqlite_statement_skipped(stmt: str) -> bool:
    head = _strip_leading_comment_lines(stmt).lstrip().upper()
    if not head:
        return True
    if head.startswith("COMMENT ON"):
        return True
    return False


def _sqlite_execute_statement(
    conn, stmt: str, *, filename: str
) -> None:
    stmt = _strip_leading_comment_lines(stmt)
    if not stmt or _sqlite_statement_skipped(stmt):
        return
    try:
        conn.execute(text(stmt))
    except (OperationalError, ProgrammingError) as e:
        msg = str(e).lower()
        if "duplicate column name" in msg:
            logger.info(
                "SQLite duplicate column skipped in %s: %s",
                filename,
                e,
            )
            return
        if "already exists" in msg:
            logger.info(
                "SQLite object already exists skipped in %s: %s",
                filename,
                e,
            )
            return
        raise


def apply_migrations(engine: Engine) -> None:
    """Apply all SQL migrations from the migrations directory."""
    if not MIGRATIONS_DIR.exists():
        logger.warning(f"Migrations directory not found: {MIGRATIONS_DIR}")
        return

    # Get all SQL migration files, sorted by name
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    
    if not migration_files:
        logger.info("No migration files found")
        return

    logger.info(f"Found {len(migration_files)} migration files")

    with engine.connect() as conn:
        # Create migrations tracking table if it doesn't exist
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS _migrations (
                filename VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()

        # Get already applied migrations
        applied = set()
        result = conn.execute(text("SELECT filename FROM _migrations"))
        applied = {row[0] for row in result}

        # Apply each migration
        for migration_file in migration_files:
            filename = migration_file.name
            
            if filename in applied:
                logger.debug(f"Migration already applied: {filename}")
                continue

            logger.info(f"Applying migration: {filename}")
            
            try:
                sql_content = migration_file.read_text(encoding="utf-8")
                if engine.dialect.name == "sqlite":
                    sql_content = _rewrite_sqlite_migration_sql(sql_content)
                    # SQLite: один statement за вызов (ProgrammingError иначе).
                    for stmt in _split_sql_statements(sql_content):
                        for piece in _sqlite_expand_alter_table_add_columns(stmt):
                            _sqlite_execute_statement(conn, piece, filename=filename)
                else:
                    # PostgreSQL и др.: один скрипт как раньше (+ только IF NOT EXISTS для ADD COLUMN).
                    sql_pg = re.sub(
                        r"\bADD\s+COLUMN\s+IF\s+NOT\s+EXISTS\b",
                        "ADD COLUMN",
                        sql_content,
                        flags=re.IGNORECASE,
                    )
                    conn.execute(text(sql_pg))
                conn.commit()
                
                # Record migration as applied
                conn.execute(
                    text("INSERT INTO _migrations (filename) VALUES (:filename)"),
                    {"filename": filename}
                )
                conn.commit()
                
                logger.info(f"Successfully applied migration: {filename}")
            except Exception as e:
                logger.error(f"Error applying migration {filename}: {e}", exc_info=True)
                conn.rollback()
                raise
