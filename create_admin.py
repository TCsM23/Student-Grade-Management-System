import bcrypt
import mysql.connector

DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "@YvesJerico23",
    "database": "plv_DB"
}

def create_user(username, plain_password, role="admin", stud_id=None):
    hashed = bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    conn = mysql.connector.connect(**DB_CONFIG)
    cur  = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO users (username, password_hash, role, stud_id)
               VALUES (%s, %s, %s, %s)""",
            (username, hashed, role, stud_id)
        )
        conn.commit()
        print(f"[OK] User '{username}' created with role '{role}'.")
    except mysql.connector.errors.IntegrityError:
        print(f"[SKIP] Username '{username}' already exists.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    # ── Create your default accounts here ──────────────────────
    create_user("admin",        "admin123",   role="admin")
    create_user("apostol.r",    "teacher123", role="teacher")
    create_user("juan.delacruz","student123", role="student", stud_id=1)
    create_user("maria.santos", "student123", role="student", stud_id=2)

    print("\nDone! You can now log in with:")
    print("  Username: admin       Password: admin123")
    print("  Username: apostol.r   Password: teacher123")
