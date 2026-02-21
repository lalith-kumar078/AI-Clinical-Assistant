import sqlite3
from datetime import datetime
import os

# --------------------------------------------------
# Correct Database Path (Project Root)
# --------------------------------------------------
print("DB FILE LOADED:",__file__)
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

DB_NAME = os.path.join(BASE_DIR, "patient_data.db")


def get_connection():
    return sqlite3.connect(DB_NAME)


# ==================================================
# CONSULTATIONS TABLE
# ==================================================

def init_db():
    with get_connection() as conn:
        c = conn.cursor()

        # Check if consultations table exists
        c.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='consultations';
        """)
        table_exists = c.fetchone()

        if table_exists:
            # Check columns
            c.execute("PRAGMA table_info(consultations);")
            columns = [column[1] for column in c.fetchall()]

            if "patient_username" not in columns:
                # Add missing column safely
                c.execute("""
                    ALTER TABLE consultations
                    ADD COLUMN patient_username TEXT DEFAULT 'unknown';
                """)

        else:
            # Create table if it doesn't exist
            c.execute("""
            CREATE TABLE consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_username TEXT NOT NULL,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                doctor TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                symptoms TEXT
            )
            """)

        conn.commit()

def save_consultation(patient_username, name, age, doctor, date, time, symptoms):
    init_db()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO consultations 
        (patient_username, name, age, doctor, date, time, symptoms)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (patient_username, name, age, doctor, date, time, symptoms))
        conn.commit()


def get_consultations():
    init_db()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM consultations ORDER BY id DESC")
        return c.fetchall()


def get_consultations_by_user(username, role):
    init_db()
    with get_connection() as conn:
        c = conn.cursor()

        if role == "patient":
            c.execute("""
                SELECT * FROM consultations
                WHERE patient_username = ?
                ORDER BY id DESC
            """, (username,))
        else:  # doctor
            c.execute("""
                SELECT * FROM consultations
                ORDER BY id DESC
            """)

        return c.fetchall()


def get_statistics():
    init_db()
    with get_connection() as conn:
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM consultations")
        total = c.fetchone()[0]

        c.execute("SELECT AVG(age) FROM consultations")
        avg_age = c.fetchone()[0]

        c.execute("""
            SELECT doctor, COUNT(*)
            FROM consultations
            GROUP BY doctor
            ORDER BY COUNT(*) DESC
            LIMIT 1
        """)
        doctor_data = c.fetchone()

        return total, avg_age, doctor_data


# ==================================================
# LOGIN HISTORY TABLE
# ==================================================

def init_login_table():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            login_time TEXT NOT NULL
        )
        """)
        conn.commit()


def save_login_history(username, role):
    init_login_table()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO login_history (username, role, login_time)
        VALUES (?, ?, ?)
        """, (
            username,
            role,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()


def get_login_history():
    init_login_table()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM login_history ORDER BY id DESC")
        return c.fetchall()


# ==================================================
# USERS TABLE
# ==================================================

def init_user_table():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """)
        conn.commit()


def create_user(username, hashed_password, role):
    init_user_table()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, (username, hashed_password, role))
        conn.commit()


def get_user(username):
    init_user_table()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        return c.fetchone()