import sqlite3
import datetime
from tkinter import messagebox

DB_NAME = "currency_rates.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency TEXT NOT NULL,
            rate REAL NOT NULL,
            fetched_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_rate(id: int, target_currency: str, rate: float):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    date_now = datetime.datetime.now()
    date_str = f"{date_now.day}-{date_now.month}-{date_now.year} {date_now.strftime('%H:%M')}"
    cur.execute("""
        INSERT INTO rates (id, currency, rate, fetched_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
        rate = excluded.rate,
        fetched_at = excluded.fetched_at
    """, (id, target_currency, rate, date_str))
    conn.commit()
    conn.close()

def get_saved_rate(target_currency: str = 'USD') -> float:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT rate FROM rates WHERE currency='{target_currency}'")
        rate = cur.fetchone()[0]
        return rate
    except Exception as e:
        messagebox.showerror("Ошибка", "Обновите валютные курсы")
    conn.close()
    return None