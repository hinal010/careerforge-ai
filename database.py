import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
