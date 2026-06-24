from db import get_connection
import bcrypt


class User:
    """
    Represents a logged-in system user.
    Call User.login(username, password) to authenticate.
    """

    def __init__(self, user_id, username, role, stud_id=None):
        self.user_id  = user_id
        self.username = username
        self.role     = role
        self.stud_id  = stud_id

    def get(self, key, default=None):
        """Dict-like .get() so login.py can do user.get('role') etc."""
        return getattr(self, key, default)

    # ─────────────────────────────────────────────
    # AUTHENTICATE
    # ─────────────────────────────────────────────

    @staticmethod
    def login(username, password):
        """
        Verify credentials against the users table.
        Returns a User instance on success, or None on failure.
        """
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM users WHERE username = %s", (username,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            # Compare plain password against stored bcrypt hash
            pw_bytes   = password.encode("utf-8")
            hash_bytes = row["password_hash"].encode("utf-8")

            if bcrypt.checkpw(pw_bytes, hash_bytes):
                return User(
                    user_id  = row["user_id"],
                    username = row["username"],
                    role     = row["role"],
                    stud_id  = row.get("stud_id")
                )
            return None
        finally:
            cursor.close()
            conn.close()

    # ─────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────

    @staticmethod
    def create(username, plain_password, role="student", stud_id=None):
        """
        Insert a new user with a bcrypt-hashed password.
        Returns the new user_id, or raises on duplicate username.
        """
        hashed = bcrypt.hashpw(
            plain_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO users (username, password_hash, role, stud_id)
                   VALUES (%s, %s, %s, %s)""",
                (username, hashed, role, stud_id)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            if "Duplicate entry" in str(e):
                raise ValueError(f"Username '{username}' is already taken.")
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def change_password(user_id, new_plain_password):
        """Hash and store a new password for a user."""
        hashed = bcrypt.hashpw(
            new_plain_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE user_id = %s",
                (hashed, user_id)
            )
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

    def __repr__(self):
        return f"<User id={self.user_id} username={self.username!r} role={self.role!r}>"