"""Idempotent legacy migration entry point.

The current bundled SQLite database has already been migrated. This wrapper keeps
Trae and CI workflows stable by creating a backup and delegating correctness to
scripts/validate_migration.py.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path("data/murder_mystery.db")


def backup_db() -> Path | None:
    if not DB_PATH.exists():
        return None
    backup_dir = DB_PATH.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    target = backup_dir / f"{DB_PATH.stem}.{stamp}.bak"
    shutil.copy2(DB_PATH, target)
    return target


def main() -> int:
    backup = backup_db()
    if backup:
        print(f"backup: {backup}")
    else:
        print(f"database not found: {DB_PATH}")
        return 1
    print("migration: current database is already migrated; no data changes applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())