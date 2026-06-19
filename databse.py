"""
database.py

Handles all SQLite database operations:
creating tables, adding/finding users, and updating points.

English Notes:
- This file only communicates with the database.
  There is no Flask or Kivy code here.
- There are 2 tables:
    1. users     -> stores phone number and points
    2. ad_views  -> stores every ad watch record
                   (when it was watched and how many points were earned)
"""

import sqlite3
from datetime import datetime

DB_NAME = "users.db"

# Fixed reward points given for each ad watched
POINTS_PER_AD = 10


def get_connection():
    """
    Returns a new database connection.

    Each function creates and closes its own connection,
    which keeps things safe and simple.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Allows row access like a dictionary
    return conn


def init_db():
    """
    Creates database tables if they do not already exist.

    This function is called once when the app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # users table:
    # phone number must be unique (one account per phone number)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            points INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # ad_views table:
    # stores every ad watch log linked with user_id
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
    """
    Creates a new user using the given phone number.

    Returns:
        dict -> {id, phone, points}
        None -> if the phone number already exists
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (phone, points, created_at) VALUES (?, ?, ?)",
            (phone, 0, datetime.now().isoformat())
        )

        conn.commit()
        user_id = cursor.lastrowid

        return {
            "id": user_id,
            "phone": phone,
            "points": 0
        }

    except sqlite3.IntegrityError:
        # Phone number already exists (UNIQUE constraint failed)
        return None

    finally:
        conn.close()


def get_user_by_phone(phone):
    """
    Finds a user using the phone number.

    Returns:
        dict -> {id, phone, points}
        None -> if user is not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, phone, points FROM users WHERE phone = ?",
        (phone,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "phone": row["phone"],
        "points": row["points"]
    }


def get_user_by_id(user_id):
    """
    Finds a user using the user ID.

    Useful for checking balance after login.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, phone, points FROM users WHERE id = ?",
        (user_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "phone": row["phone"],
        "points": row["points"]
    }


def add_points_for_ad(user_id, points=POINTS_PER_AD):
    """
    User watched an ad:
    increase points and save the event in ad_views.

    Returns:
        int  -> new total points
        None -> if user does not exist
    """
    conn = get_connection()
    cursor = conn.cursor()

    # First check whether the user exists
    cursor.execute(
        "SELECT points FROM users WHERE id = ?",
        (user_id,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return None

    new_points = row["points"] + points

    # Update user's points
    cursor.execute(
        "UPDATE users SET points = ? WHERE id = ?",
        (new_points, user_id)
    )

    # Save ad watch log
    cursor.execute(
        "INSERT INTO ad_views (user_id, points_earned, viewed_at) VALUES (?, ?, ?)",
        (user_id, points, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

    return new_points


def get_ad_view_count(user_id):
    """
    Returns the total number of ads watched by a user.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM ad_views WHERE user_id = ?",
        (user_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return row["cnt"]


# If this file is run directly,
# create the tables for testing purposes.
if __name__ == "__main__":
    init_db()
    print("Database initialized:", DB_NAME)
