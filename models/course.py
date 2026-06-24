# models/course.py
from db import get_connection

# create

def add_course(course_code, course_title, course_units, course_description=None):
    """
    Insert a new course record.
    Raises ValueError if course_code already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO course
                (course_code, course_title, course_units, course_description)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (course_code, course_title, course_units, course_description))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            raise ValueError(f"Course code '{course_code}' already exists.")
        raise
    finally:
        cursor.close()
        conn.close()

# read

def get_all_courses():
    """Return all courses as a list of dicts, ordered by course_code."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM course ORDER BY course_code")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_course_by_id(course_id):
    """Return one course dict or None."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM course WHERE course_id = %s", (course_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_course_by_code(course_code):
    """Lookup by course code (e.g. 'IM-102')."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM course WHERE course_code = %s", (course_code,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def search_courses(keyword):
    """Search by course code or title (partial match)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        like = f"%{keyword}%"
        cursor.execute(
            "SELECT * FROM course WHERE course_code LIKE %s OR course_title LIKE %s ORDER BY course_code",
            (like, like)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

# update

def update_course(course_id, course_code, course_title, course_units, course_description=None):
    """Update a course's fields."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = """
            UPDATE course
            SET course_code = %s, course_title = %s,
                course_units = %s, course_description = %s
            WHERE course_id = %s
        """
        cursor.execute(sql, (course_code, course_title, course_units,
                             course_description, course_id))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

# delete

def delete_course(course_id):
    """
    Delete a course permanently.
    Will fail if students are enrolled — handle with ON DELETE RESTRICT.
    Returns True if deleted, False if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM course WHERE course_id = %s", (course_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()