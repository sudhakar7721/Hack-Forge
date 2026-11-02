"""Copy an existing Maatram SQLite database into the configured MySQL database.

Run from the backend directory after configuring backend/.env:
    python migrate_sqlite_to_mysql.py ./maatram.db

The target MySQL tables must be empty. The script never deletes or overwrites data.
"""
from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import MetaData, Table, URL, create_engine, func, inspect, select

# Import models so every mapped table is registered on Base.metadata.
from app.database import Base, engine as mysql_engine  # noqa: E402
from app import models  # noqa: F401,E402


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python migrate_sqlite_to_mysql.py <path-to-maatram.db>")
        return 2

    sqlite_path = Path(sys.argv[1]).expanduser().resolve()
    if not sqlite_path.is_file():
        print(f"SQLite database file not found: {sqlite_path}")
        return 2

    sqlite_engine = create_engine(URL.create("sqlite", database=str(sqlite_path)))
    Base.metadata.create_all(bind=mysql_engine)

    try:
        with mysql_engine.connect() as target_check:
            for target_table in Base.metadata.sorted_tables:
                count = target_check.scalar(select(func.count()).select_from(target_table)) or 0
                if count:
                    print(
                        f"Target table '{target_table.name}' already contains {count} rows. "
                        "Migration stopped to avoid duplicates or overwriting data."
                    )
                    return 1

        source_metadata = MetaData()
        copied_total = 0
        with sqlite_engine.connect() as source_conn, mysql_engine.begin() as target_conn:
            source_table_names = set(inspect(sqlite_engine).get_table_names())

            for target_table in Base.metadata.sorted_tables:
                if target_table.name not in source_table_names:
                    print(f"Skipping '{target_table.name}': not present in SQLite database.")
                    continue

                source_table = Table(
                    target_table.name,
                    source_metadata,
                    autoload_with=sqlite_engine,
                )
                source_columns = {column.name for column in source_table.columns}
                rows = source_conn.execute(select(source_table)).mappings().all()
                payload = [
                    {
                        column.name: row[column.name]
                        for column in target_table.columns
                        if column.name in source_columns
                    }
                    for row in rows
                ]

                if payload:
                    target_conn.execute(target_table.insert(), payload)
                copied_total += len(payload)
                print(f"Copied {len(payload)} rows into '{target_table.name}'.")

        print(f"Migration completed. Total rows copied: {copied_total}.")
        print("Verify the records in MySQL Workbench before using the application.")
        return 0
    finally:
        sqlite_engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
