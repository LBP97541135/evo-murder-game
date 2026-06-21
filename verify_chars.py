import sqlite3
conn = sqlite3.connect('data/murder_mystery.db')
cursor = conn.cursor()
script_id = 'xiutie-avenue-missing-three-minutes'
cursor.execute("SELECT name, is_player, bio, secret FROM characters WHERE script_id=?", (script_id,))
rows = cursor.fetchall()
for row in rows:
    print(f"Name: {row[0]}, is_player: {row[1]}, bio_len: {len(row[2]) if row[2] else 0}, secret_len: {len(row[3]) if row[3] else 0}")
conn.close()
