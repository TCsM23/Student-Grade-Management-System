import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
from config import DB_CONFIG

# database helpers
def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        messagebox.showerror("DB Error", str(e))
        return None

def query(sql, params=(), fetch="all"):
    conn = get_connection()
    if not conn:
        return [] if fetch == "all" else None
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        result = cur.fetchall() if fetch == "all" else cur.fetchone()
        return result or ([] if fetch == "all" else None)
    finally:
        cur.close(); conn.close()

def execute(sql, params=()):
    conn = get_connection()
    if not conn: 
        return False
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid or True
    except Error as e:
        conn.rollback()
        messagebox.showerror("Error", str(e))
        return False
    finally:
        cur.close(); conn.close()

def get_stats():
    conn = get_connection()
    if not conn:
        return {}
    cur = conn.cursor(dictionary=True)
    stats = {}
    try:
        cur.execute("SELECT COUNT(*) AS n FROM student WHERE stud_status='A'")
        stats["students"] = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM course")
        stats["courses"] = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM enrollment WHERE status='ENROLLED'")
        stats["enrolled"] = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM enrollment WHERE final_grade > 3.00")
        stats["failing"] = cur.fetchone()["n"]
    finally:
        cur.close(); conn.close()
    return stats

def compute_letters(score):
    if score is None: return ""
    if score >= 90: return "A"
    if score >= 85: return "B+"
    if score >= 80: return "B"
    if score >= 75: return "C+"
    if score >= 70: return "C"
    if score >= 65: return "D"
    return "F"

def compute_final(score):
    if score is None: return None
    if score >= 97: return 1.00
    if score >= 94: return 1.25
    if score >= 91: return 1.50
    if score >= 88: return 1.75
    if score >= 85: return 2.00
    if score >= 82: return 2.25
    if score >= 79: return 2.50
    if score >= 76: return 2.75
    if score >= 75: return 3.00
    return 5.00