from db import get_connection

# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────

def add_student(stud_no, stud_fname, stud_lname, prog_id, year_level, section,
                 stud_email=None, stud_phone=None, stud_gender=None,
                 stud_dob=None, stud_address=None):
    """
    Insert a new student record.
    Raises ValueError if stud_no or stud_email already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO student
                (stud_no, stud_fname, stud_lname, prog_id, year_level, section,
                 stud_email, stud_phone, stud_gender, stud_dob, stud_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (stud_no, stud_fname, stud_lname, prog_id, year_level,
                             section, stud_email, stud_phone, stud_gender,
                             stud_dob, stud_address))
        conn.commit()
        return cursor.lastrowid          # returns the new stud_id
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            raise ValueError(f"Student number or email already exists: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────

def get_all_students(active_only=True):
    """Return all students as a list of dicts. Excludes inactive by default."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if active_only:
            cursor.execute(
                "SELECT * FROM student WHERE stud_status = 'A' ORDER BY stud_lname"
            )
        else:
            cursor.execute("SELECT * FROM student ORDER BY stud_lname")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_student_by_id(stud_id):
    """Return one student dict or None."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM student WHERE stud_id = %s", (stud_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_student_by_no(stud_no):
    """Lookup by student number (e.g. '2025-00001')."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM student WHERE stud_no = %s", (stud_no,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def search_students(keyword):
    """Search by first name, last name, or student number (partial match)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        like = f"%{keyword}%"
        sql = """
            SELECT * FROM student
            WHERE stud_fname LIKE %s OR stud_lname LIKE %s OR stud_no LIKE %s
            ORDER BY stud_lname
        """
        cursor.execute(sql, (like, like, like))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_students_by_section(section):
    """Return all active students in a given section."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM student WHERE section = %s AND stud_status = 'A' "
            "ORDER BY stud_lname",
            (section,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_students_by_program(prog_id):
    """Return all active students under a given program."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM student WHERE prog_id = %s AND stud_status = 'A' "
            "ORDER BY stud_lname",
            (prog_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────

def update_student(stud_id, stud_fname, stud_lname, prog_id, year_level, section,
                    stud_email=None, stud_phone=None, stud_address=None):
    """Update a student's editable fields."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = """
            UPDATE student
            SET stud_fname = %s, stud_lname = %s, prog_id = %s,
                year_level = %s, section = %s, stud_email = %s,
                stud_phone = %s, stud_address = %s
            WHERE stud_id = %s
        """
        cursor.execute(sql, (stud_fname, stud_lname, prog_id, year_level, section,
                             stud_email, stud_phone, stud_address, stud_id))
        conn.commit()
        return cursor.rowcount   # 1 if updated, 0 if stud_id not found
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def set_student_status(stud_id, status):
    """
    Soft-activate/deactivate a student. status must be 'A' or 'I'.
    Use this instead of deleting students with enrollment history.
    """
    if status not in ("A", "I"):
        raise ValueError("status must be 'A' (active) or 'I' (inactive)")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE student SET stud_status = %s WHERE stud_id = %s",
            (status, stud_id)
        )
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────

def delete_student(stud_id):
    """
    Permanently delete a student and their enrollments (ON DELETE CASCADE).
    Prefer set_student_status(stud_id, 'I') for soft-delete instead.
    Returns True if deleted, False if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM student WHERE stud_id = %s", (stud_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()