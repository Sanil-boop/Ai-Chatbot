import sqlite3
import os

# ================= DATABASE PATH =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

# ================= CONNECTION =================

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ================= TABLE =================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

conn.commit()
