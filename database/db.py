import sqlite3
import hashlib
from config import DB_PATH

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    # users table for authentication
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT
    )
    """)

    # OSINT IoCs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS iocs (
        value TEXT PRIMARY KEY,
        type TEXT,
        threat TEXT,
        confidence REAL
    )
    """)

    # UPDATED alerts table (with geo data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        ip TEXT,
        severity TEXT,
        reason TEXT,
        lat REAL,
        lon REAL,
        country TEXT
    )
    """)

    # Blocked IPs table for active blocking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blocked_ips (
        ip TEXT PRIMARY KEY,
        reason TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()


def create_user(username, password):
    try:
        pw_hash = hash_password(password)
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, pw_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username exists
    except Exception as e:
        print("[DB ERROR USER]", e)
        return False

def authenticate_user(username, password):
    pw_hash = hash_password(password)
    cursor.execute("SELECT 1 FROM users WHERE username = ? AND password_hash = ?", (username, pw_hash))
    result = cursor.fetchone()
    return result is not None

def insert_ioc(ioc):
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO iocs VALUES (?, ?, ?, ?)",
            (ioc["value"], ioc["type"], ioc["threat"], ioc["confidence"])
        )
        conn.commit()
    except Exception as e:
        print("[DB ERROR IOC]", e)


def get_all_iocs():
    cursor.execute("SELECT value FROM iocs")
    return set([row[0] for row in cursor.fetchall()])


# ✅ UPDATED FUNCTION (IMPORTANT)
def insert_alert(ip, severity, reason, lat, lon, country):
    try:
        cursor.execute(
            "INSERT INTO alerts VALUES (?, ?, ?, ?, ?, ?)",
            (ip, severity, reason, lat, lon, country)
        )
        conn.commit()
    except Exception as e:
        print("[DB ERROR ALERT]", e)

def insert_blocked_ip(ip, reason):
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO blocked_ips (ip, reason) VALUES (?, ?)",
            (ip, reason)
        )
        conn.commit()
    except Exception as e:
        print("[DB ERROR BLOCKED IP]", e)