"""Copy a legacy Maatram SQLite database into the configured MySQL database.

Run from the backend directory:
    python migrate_sqlite_to_mysql.py path/to/maatram.db

The target tables must be empty. The script never deletes or overwrites data.
"""
from __future__ import annotations
import sys
from pathlib import Path

from sqlalchemy import MetaData, Table, URL, create_engine, func, inspect, select
from app.database import Base, engine as mysql_engine  # noqa: E402
from app import models  # noqa: F401,E402

ALIASES = {
    "students": {
        "dob": "date_of_birth", "previous_school": "school_name",
        "tenth_mark": "tenth_marks", "twelfth_mark": "twelfth_marks",
        "applied_domain": "domain", "college": "college_name",
        "application_status": "admission_status", "fees_details": "fees",
        "academic_details": "academic_performance", "self_learning_details": "self_learning",
        "zone_name": "zone",
    },
    "alumni": {
        "current_company": "company_name", "job_title": "job_role",
        "work_location": "current_location",
    },
    "zone_information": {"sender_name": "zone_incharge", "message": "description"},
    "student_feedback": {"message": "feedback"},
}


def normalize_value(table_name: str, target_name: str, value):
    if table_name == "students" and target_name == "application_status":
        text_value = str(value or "").strip().lower().replace("_", " ")
        if text_value in {"pending", "waiting list", "waitlist"}:
            return "Waiting List"
        if text_value in {"approved", "accepted"}:
            return "Approved"
        if text_value in {"rejected", "declined"}:
            return "Declined"
        return value or "Waiting List"
    if table_name == "alumni" and target_name == "placed":
        return str(value or "").strip().lower() in {"placed", "yes", "true", "1"}
    if table_name == "alumni" and target_name == "placement_status":
        return "placed" if str(value or "").strip().lower() in {"placed", "yes", "true", "1"} else "not_placed"
    if table_name == "students" and target_name == "fees_details" and value is not None:
        return str(value)
    return value


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
                    print(f"Target table '{target_table.name}' already contains {count} rows. Migration stopped to avoid duplicates.")
                    return 1

        source_metadata = MetaData()
        source_names = set(inspect(sqlite_engine).get_table_names())
        copied_total = 0
        student_names = {}
        with sqlite_engine.connect() as source_conn, mysql_engine.begin() as target_conn:
            for target_table in Base.metadata.sorted_tables:
                table_name = target_table.name
                if table_name not in source_names:
                    print(f"Skipping '{table_name}': not present in SQLite database.")
                    continue
                source_table = Table(table_name, source_metadata, autoload_with=sqlite_engine)
                source_columns = {column.name for column in source_table.columns}
                rows = source_conn.execute(select(source_table)).mappings().all()
                payload = []
                for row in rows:
                    item = {}
                    for column in target_table.columns:
                        name = column.name
                        if name in source_columns:
                            value = row[name]
                        elif name in ALIASES.get(table_name, {}) and ALIASES[table_name][name] in source_columns:
                            value = row[ALIASES[table_name][name]]
                        else:
                            continue
                        item[name] = normalize_value(table_name, name, value)
                    if table_name == "students" and item.get("id") is not None:
                        student_names[item["id"]] = item.get("full_name", "")
                    if table_name == "student_feedback":
                        item.setdefault("student_name", student_names.get(item.get("student_id"), ""))
                        item.setdefault("feedback_type", "general")
                        item.setdefault("feedback", item.get("message", ""))
                    if table_name == "zone_information":
                        item.setdefault("title", "Legacy notice")
                        item.setdefault("sender_role", "")
                        item.setdefault("link", "")
                        item.setdefault("attachment_name", "")
                        item.setdefault("attachment_data", "")
                        item.setdefault("active", True)
                    if table_name == "students":
                        item.setdefault("application_status", "Waiting List")
                        item.setdefault("admission_status", str(item.get("application_status", "Waiting List")).lower().replace(" ", "_"))
                        item.setdefault("certificate_files", "[]")
                    if table_name == "alumni":
                        item.setdefault("placed", False)
                        item.setdefault("placement_status", "placed" if item.get("placed") else "not_placed")
                    payload.append(item)
                if payload:
                    target_conn.execute(target_table.insert(), payload)
                copied_total += len(payload)
                print(f"Copied {len(payload)} rows into '{table_name}'.")
        print(f"Migration completed. Total rows copied: {copied_total}.")
        print("Verify records in MySQL Workbench before using the application.")
        return 0
    finally:
        sqlite_engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
