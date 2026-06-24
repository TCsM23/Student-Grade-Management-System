from db import get_connection


# ─────────────────────────────────────────────
# HELPER — grade computation (PLV scale: 1.0 best, 5.0 worst)
# ─────────────────────────────────────────────

def compute_letter_grade(raw_score):
    """Map a 0-100 raw score to a letter grade."""
    if raw_score is None:
        return None
    if raw_score >= 90: return "A"
    if raw_score >= 85: return "B+"
    if raw_score >= 80: return "B"
    if raw_score >= 75: return "C+"
    if raw_score >= 70: return "C"
    if raw_score >= 65: return "D"
    return "F"


def compute_final_grade(raw_score):
    """
    Convert a 0-100 raw score into PLV's 1.0-5.0 scale.
    1.0 = highest, 5.0 = failing. Adjust breakpoints to match your syllabus.
    """
    if raw_score is None:
        return None
    if raw_score >= 97: return 1.00
    if raw_score >= 94: return 1.25
    if raw_score >= 91: return 1.50
    if raw_score >= 88: return 1.75
    if raw_score >= 85: return 2.00
    if raw_score >= 82: return 2.25
    if raw_score >= 79: return 2.50
    if raw_score >= 76: return 2.75
    if raw_score >= 75: return 3.00
    return 5.00   # below passing mark


def is_passing(final_grade, passing_grade=3.00):
    """PLV scale: lower is better, so passing means <= passing_grade."""
    return final_grade is not None and final_grade <= passing_grade


# ─────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────

def enroll_student(stud_id, course_id, term_id):
    """
    Enroll a student in a course for a term (no grade yet).
    Raises ValueError on duplicate enrollment (same student+course+term).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO enrollment (stud_id, course_id, term_id, status)
            VALUES (%s, %s, %s, 'ENROLLED')
        """
        cursor.execute(sql, (stud_id, course_id, term_id))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        if "Duplicate entry" in str(e):
            raise ValueError("This student is already enrolled in this course for this term.")
        raise
    finally:
        cursor.close()
        conn.close()


def record_grade(enroll_id, raw_score):
    """
    Record/update a score for an existing enrollment.
    Auto-computes final_grade and letter_grade, marks status COMPLETED.
    """
    final_grade = compute_final_grade(raw_score)
    letter = compute_letter_grade(raw_score)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = """
            UPDATE enrollment
            SET raw_score = %s, final_grade = %s, letter_grade = %s,
                status = 'COMPLETED'
            WHERE enroll_id = %s
        """
        cursor.execute(sql, (raw_score, final_grade, letter, enroll_id))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────

def get_enrollments_by_student(stud_id, term_id=None):
    """Return all enrollments for a student, optionally filtered by term."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if term_id:
            sql = """
                SELECT e.*, c.course_code, c.course_title, c.course_units,
                       t.semester, t.school_year
                FROM enrollment e
                JOIN course c USING (course_id)
                JOIN term   t USING (term_id)
                WHERE e.stud_id = %s AND e.term_id = %s
                ORDER BY c.course_title
            """
            cursor.execute(sql, (stud_id, term_id))
        else:
            sql = """
                SELECT e.*, c.course_code, c.course_title, c.course_units,
                       t.semester, t.school_year
                FROM enrollment e
                JOIN course c USING (course_id)
                JOIN term   t USING (term_id)
                WHERE e.stud_id = %s
                ORDER BY e.term_id, c.course_title
            """
            cursor.execute(sql, (stud_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_enrollments_by_course(course_id, term_id):
    """Return all students enrolled in a course for a given term."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT e.*, s.stud_no, s.stud_fname, s.stud_lname, s.section
            FROM enrollment e
            JOIN student s USING (stud_id)
            WHERE e.course_id = %s AND e.term_id = %s
            ORDER BY s.stud_lname
        """
        cursor.execute(sql, (course_id, term_id))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def compute_gpa(stud_id, term_id):
    """
    Weighted GPA on PLV scale = sum(final_grade * units) / sum(units).
    Lower is better. Returns None if no completed grades exist.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT e.final_grade, c.course_units
            FROM enrollment e
            JOIN course c USING (course_id)
            WHERE e.stud_id = %s AND e.term_id = %s
              AND e.final_grade IS NOT NULL
        """
        cursor.execute(sql, (stud_id, term_id))
        rows = cursor.fetchall()
        if not rows:
            return None
        total_points = sum(r["final_grade"] * r["course_units"] for r in rows)
        total_units  = sum(r["course_units"] for r in rows)
        return round(total_points / total_units, 2) if total_units else None
    finally:
        cursor.close()
        conn.close()


def get_class_rank(stud_id, section, term_id):
    """Return the student's rank within their section for a term (1 = best GPA)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT s.stud_id,
                   SUM(e.final_grade * c.course_units) / SUM(c.course_units) AS gpa
            FROM enrollment e
            JOIN student s USING (stud_id)
            JOIN course  c USING (course_id)
            WHERE e.term_id = %s AND s.section = %s
              AND e.final_grade IS NOT NULL
            GROUP BY s.stud_id
            ORDER BY gpa ASC
        """
        cursor.execute(sql, (term_id, section))
        rows = cursor.fetchall()
        for rank, row in enumerate(rows, start=1):
            if row["stud_id"] == stud_id:
                return rank
        return None
    finally:
        cursor.close()
        conn.close()


def get_failing_students(term_id, passing_grade=3.00):
    """Return students with at least one failing final_grade in a term."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT s.stud_id, s.stud_no, s.stud_fname, s.stud_lname, s.section,
                   c.course_title, e.final_grade
            FROM enrollment e
            JOIN student s USING (stud_id)
            JOIN course  c USING (course_id)
            WHERE e.term_id = %s AND e.final_grade > %s
            ORDER BY s.section, s.stud_lname
        """
        cursor.execute(sql, (term_id, passing_grade))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────

def update_enrollment_status(enroll_id, status):
    """Change status to 'ENROLLED', 'DROPPED', or 'COMPLETED'."""
    if status not in ("ENROLLED", "DROPPED", "COMPLETED"):
        raise ValueError("Invalid status value.")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE enrollment SET status = %s WHERE enroll_id = %s",
            (status, enroll_id)
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

def delete_enrollment(enroll_id):
    """Remove a single enrollment record."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM enrollment WHERE enroll_id = %s", (enroll_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()