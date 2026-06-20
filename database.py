
"""
database.py
SQLite database ka kaam: tables banana, users add/find karna, points update karna.
"""

import sqlite3
from datetime import datetime

DB_NAME = "users.db"
POINTS_PER_AD = 10


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            points INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ad_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            points_earned INTEGER NOT NULL,
            viewed_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


def create_user(phone):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (phone, points, created_at) VALUES (?, ?, ?)",
            (phone, 0, datetime.now().isoformat())
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {"id": user_id, "phone": phone, "points": 0}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_phone(phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, phone, points FROM users WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {"id": row["id"], "phone": row["phone"], "points": row["points"]}


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, phone, points FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    return {"id": row["id"], "phone": row["phone"], "points": row["points"]}


def add_points_for_ad(user_id, points=POINTS_PER_AD):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT points FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return None

    new_points = row["points"] + points
    cursor.execute("UPDATE users SET points = ? WHERE id = ?", (new_points, user_id))
    cursor.execute(
        "INSERT INTO ad_views (user_id, points_earned, viewed_at) VALUES (?, ?, ?)",
        (user_id, points, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return new_points


def get_ad_view_count(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM ad_views WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row["cnt"]


if __name__ == "__main__":
    init_db()
    print("Database initialized:", DB_NAME)
