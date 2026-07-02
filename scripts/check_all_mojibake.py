# -*- coding: utf-8 -*-
"""Check ALL tables (including legacy) for mojibake."""
import sqlite3, os
DB = os.getenv("SQLITE_PATH", "data/murder_mystery.db")
MOJIBAKE_CHARS = set('éåæèãçìë¯½ðïî')

def has_mojibake(text):
    if not text or not isinstance(text, str):
        return False
    return any(c in MOJIBAKE_CHARS for c in text)

conn = sqlite3.connect(DB)
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
total = 0
for t in sorted(tables):
    try:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info([{t}])").fetchall()]
        text_cols = []
        for col in cols:
            try:
                sample = conn.execute(f"SELECT [{col}] FROM [{t}] WHERE [{col}] IS NOT NULL AND [{col}] != '' LIMIT 1").fetchone()
                if sample and isinstance(sample[0], str):
                    text_cols.append(col)
            except:
                pass
        for col in text_cols:
            rows = conn.execute(f"SELECT id, [{col}] FROM [{t}] WHERE [{col}] IS NOT NULL").fetchall()
            for row in rows:
                if has_mojibake(row[1]):
                    total += 1
                    print(f"[MOJIBAKE] {t}.id={row[0]} col={col}: {row[1][:80]}")
    except Exception as e:
        print(f"[ERR] {t}: {e}")

if total == 0:
    print("[OK] No mojibake in any table")
else:
    print(f"\n[SUMMARY] {total} mojibake fields found")
conn.close()
