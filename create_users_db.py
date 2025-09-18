import sqlite3
from hashlib import sha256

DB = 'users.db'

def hash_password(p):
    return sha256(p.encode('utf-8')).hexdigest()

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    blocked INTEGER NOT NULL DEFAULT 0
)
''')

# create admin user if not exists
admin_email = 'admin@nexusdark.ru'
admin_pass = 'adminpass'
admin_hash = hash_password(admin_pass)

c.execute('SELECT id FROM users WHERE email=?', (admin_email,))
if not c.fetchone():
    c.execute('INSERT INTO users (username, email, password_hash, blocked) VALUES (?,?,?,0)', ('admin', admin_email, admin_hash))
    print('Admin user created:', admin_email)
else:
    print('Admin already exists')

conn.commit()
conn.close()
print('DB ready:', DB)
