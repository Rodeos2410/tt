import sqlite3
import os

# Try common locations for the SQLite file
candidates = [
    os.path.join(os.path.dirname(__file__), '..', 'database.db'),
    os.path.join(os.path.dirname(__file__), 'database.db'),
    os.path.join(os.getcwd(), 'database.db'),
]

db_path = None
for p in candidates:
    p = os.path.abspath(p)
    if os.path.exists(p):
        db_path = p
        break

if not db_path:
    print('No existing database.db found in common locations:')
    for p in candidates:
        print('  ', os.path.abspath(p))
    print('If you want to create a fresh DB (data will be lost), run the server with an empty database or create one manually.')
    raise SystemExit(1)

print('Using database file:', db_path)
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# check if user table has blocked column
cur.execute("PRAGMA table_info('user')")
cols = cur.fetchall()
col_names = [c[1] for c in cols]
if 'blocked' in col_names:
    print('Column "blocked" already exists on table user. Nothing to do.')
else:
    print('Adding column "blocked" to table user...')
    try:
        cur.execute("ALTER TABLE user ADD COLUMN blocked BOOLEAN DEFAULT 0")
        conn.commit()
        print('Column added successfully.')
    except Exception as e:
        print('Failed to add column:', e)
        print('You can recreate the database by removing the file and letting the app create tables, but that will erase data.')

# Also ensure purchase table exists (create if missing)
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='purchase'")
if not cur.fetchone():
    print('Creating table purchase...')
    try:
        cur.execute('''
            CREATE TABLE purchase (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                qty INTEGER NOT NULL DEFAULT 1,
                total_price REAL NOT NULL DEFAULT 0.0
            )
        ''')
        conn.commit()
        print('Purchase table created.')
    except Exception as e:
        print('Failed to create purchase table:', e)

conn.close()
print('Migration finished.')
