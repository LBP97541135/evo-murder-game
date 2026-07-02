# -*- coding: utf-8 -*-
"""List all tables in the database."""
import sqlite3, os
DB = os.getenv("SQLITE_PATH", "data/murder_mystery.db")
conn = sqlite3.connect(DB)
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"Total tables: {len(tables)}")
for t in sorted(tables):
    cnt = conn.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
    print(f"  {t}: {cnt} rows")
conn.close()
