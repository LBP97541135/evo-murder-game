# -*- coding: utf-8 -*-
"""Check database text fields for mojibake (double-encoded UTF-8)."""
import sqlite3
import sys
import os

DB_PATH = os.getenv("SQLITE_PATH", "data/murder_mystery.db")

# Characters that commonly appear in mojibake from UTF-8→Latin-1→UTF-8 double encoding
MOJIBAKE_CHARS = set('éåæèãçìë¯½ðïî')

def has_mojibake(text: str) -> bool:
    if not text:
        return False
    return any(c in MOJIBAKE_CHARS for c in text)

def fix_double_encoding(text: str) -> str:
    """Attempt to fix double-encoded UTF-8 (UTF-8→Latin-1→UTF-8)."""
    if not text:
        return text
    try:
        raw = text.encode('latin-1')
        fixed = raw.decode('utf-8')
        return fixed
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def main():
    conn = sqlite3.connect(DB_PATH)
    tables_to_check = [
        ('scripts', ['title', 'description', 'author', 'genre', 'theme']),
        ('script_characters', ['name', 'bio', 'personality', 'public_context', 'private_secret', 'behavior_rules']),
        ('agents', ['name', 'identity_doc', 'constitution']),
        ('skills', ['name', 'description', 'prompt_content', 'strategy', 'examples', 'anti_patterns']),
        ('experience_records', ['summary', 'detail', 'dm_comment']),
        ('conversation_messages', ['content']),
        ('evidence_instances', ['name', 'basic_description', 'detailed_description', 'deep_description']),
    ]

    total_mojibake = 0
    fixed_count = 0
    updates = []

    for table, columns in tables_to_check:
        try:
            rows = conn.execute(f"SELECT id, {', '.join(columns)} FROM {table}").fetchall()
        except sqlite3.OperationalError:
            continue

        for row in rows:
            row_id = row[0]
            for i, col in enumerate(columns):
                val = row[i + 1]
                if not val or not isinstance(val, str):
                    continue
                if has_mojibake(val):
                    total_mojibake += 1
                    fixed = fix_double_encoding(val)
                    if fixed != val:
                        updates.append((table, col, row_id, fixed))
                        fixed_count += 1
                    else:
                        print(f"[MOJIBAKE] {table}.id={row_id} col={col}: cannot auto-fix, first 60 chars: {val[:60]}")

    if updates:
        print(f"\n[REPAIR] Found {total_mojibake} mojibake fields, auto-fixable: {fixed_count}")
        for table, col, row_id, fixed in updates:
            conn.execute(f"UPDATE {table} SET {col} = ? WHERE id = ?", (fixed, row_id))
        conn.commit()
        print(f"[REPAIR] Applied {fixed_count} fixes")
    else:
        if total_mojibake == 0:
            print("[OK] No mojibake detected in any text fields")
        else:
            print(f"[WARN] {total_mojibake} mojibake fields found but not auto-fixable")

    conn.close()

if __name__ == "__main__":
    main()
