-- ============================================================
-- Student Grade Management System — plv_DB
-- Built following IM 102 (Advance Database Systems) Unit 1
-- naming conventions and constraint patterns
-- ============================================================

CREATE DATABASE IF NOT EXISTS plv_DB;
USE plv_DB;

-- ------------------------------------------------------------
-- Table 1: Department
-- ------------------------------------------------------------
CREATE TABLE department (
    dept_id     INT AUTO_INCREMENT PRIMARY KEY,
    dept_code   VARCHAR(10) UNIQUE NOT NULL,     -- 'CET', 'CBA'
    dept_name   VARCHAR(100) NOT NULL,
    dept_head   VARCHAR(100),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Table 2: Program (e.g., BSIT, BSCS)
-- ------------------------------------------------------------
CREATE TABLE program (
    prog_id                INT AUTO_INCREMENT PRIMARY KEY,
    prog_code              VARCHAR(10) UNIQUE NOT NULL,   -- 'BSIT'
    prog_name               VARCHAR(150) NOT NULL,
    dept_id                INT NOT NULL,
    prog_credits_required   INT DEFAULT 120,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_program_dept
        FOREIGN KEY (dept_id)
        REFERENCES department (dept_id)
        ON DELETE RESTRICT
);

-- ------------------------------------------------------------
-- Table 3: Student
-- ------------------------------------------------------------
CREATE TABLE student (
    stud_id      INT AUTO_INCREMENT PRIMARY KEY,
    stud_no      VARCHAR(20) UNIQUE NOT NULL,      -- '2025-00001'
    stud_fname   VARCHAR(100) NOT NULL,
    stud_lname   VARCHAR(100) NOT NULL,
    prog_id      INT NOT NULL,
    year_level   INT NOT NULL,                     -- 1,2,3,4
    section      VARCHAR(20) NOT NULL,
    stud_email   VARCHAR(150) UNIQUE,
    stud_phone   CHAR(11),                         -- 09171234567
    stud_gender  CHAR(1),                           -- 'M','F','O'
    stud_dob     DATE,
    stud_address VARCHAR(255),
    stud_status  CHAR(1) DEFAULT 'A',               -- 'A'=Active, 'I'=Inactive
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_student_prog
        FOREIGN KEY (prog_id)
        REFERENCES program (prog_id)
        ON DELETE RESTRICT,
    CHECK (stud_gender IN ('M', 'F', 'O')),
    CHECK (stud_status IN ('A', 'I'))
);

-- ------------------------------------------------------------
-- Table 4: Course / Subject
-- ------------------------------------------------------------
CREATE TABLE course (
    course_id          INT AUTO_INCREMENT PRIMARY KEY,
    course_code        VARCHAR(20) UNIQUE NOT NULL,   -- 'IM-102'
    course_title        VARCHAR(200) NOT NULL,
    course_description  TEXT,
    course_units        INT NOT NULL CHECK (course_units BETWEEN 1 AND 6),
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Table 5: Term (school year + semester)
-- ------------------------------------------------------------
CREATE TABLE term (
    term_id      INT AUTO_INCREMENT PRIMARY KEY,
    semester     VARCHAR(10) NOT NULL,        -- '1st', '2nd', 'Summer'
    school_year  VARCHAR(20) NOT NULL,        -- '2025-2026'
    UNIQUE (semester, school_year)
);

-- ------------------------------------------------------------
-- Table 6: Enrollment (links student to course per term, holds grade)
-- ------------------------------------------------------------
CREATE TABLE enrollment (
    enroll_id     INT AUTO_INCREMENT PRIMARY KEY,
    stud_id       INT NOT NULL,
    course_id     INT NOT NULL,
    term_id       INT NOT NULL,
    enroll_date   DATE DEFAULT (CURDATE()),
    raw_score     DECIMAL(5,2),                     -- 0-100 input score
    final_grade   DECIMAL(5,2),                     -- 1.0-5.0 PLV grading scale
    letter_grade  VARCHAR(5),
    status        VARCHAR(20) DEFAULT 'ENROLLED',   -- 'ENROLLED','DROPPED','COMPLETED'
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_enroll_student
        FOREIGN KEY (stud_id)
        REFERENCES student (stud_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_enroll_course
        FOREIGN KEY (course_id)
        REFERENCES course (course_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_enroll_term
        FOREIGN KEY (term_id)
        REFERENCES term (term_id)
        ON DELETE RESTRICT,
    -- Prevent duplicate enrollment in same course, same term
    CONSTRAINT uq_enroll_unique
        UNIQUE (stud_id, course_id, term_id),
    CHECK (raw_score IS NULL OR raw_score BETWEEN 0 AND 100),
    CHECK (final_grade IS NULL OR final_grade BETWEEN 1 AND 5),
    CHECK (status IN ('ENROLLED', 'DROPPED', 'COMPLETED'))
);

-- ------------------------------------------------------------
-- Table 7: Users (system login — admin/teacher/student)
-- ------------------------------------------------------------
CREATE TABLE users (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    username       VARCHAR(50) UNIQUE NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    role           VARCHAR(20) DEFAULT 'student',   -- 'admin','teacher','student'
    stud_id        INT,                              -- linked student account (nullable)
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_student
        FOREIGN KEY (stud_id)
        REFERENCES student (stud_id)
        ON DELETE SET NULL,
    CHECK (role IN ('admin', 'teacher', 'student'))
);

-- ------------------------------------------------------------
-- Indexes for frequently queried columns
-- ------------------------------------------------------------
CREATE INDEX idx_student_program  ON student (prog_id);
CREATE INDEX idx_student_status   ON student (stud_status);
CREATE INDEX idx_student_section  ON student (section);
CREATE INDEX idx_enroll_term      ON enrollment (term_id);
CREATE INDEX idx_enroll_student   ON enrollment (stud_id);
CREATE INDEX idx_enroll_course    ON enrollment (course_id);

-- ============================================================
-- Sample seed data (for testing CRUD, joins, and analytics)
-- ============================================================

-- ------------------------------------------------------------
-- Departments
-- ------------------------------------------------------------
INSERT INTO department (dept_code, dept_name, dept_head) VALUES
    ('CET', 'College of Engineering and Technology', 'Engr. Rommel Apostol'),
    ('CBA', 'College of Business Administration', 'Dr. Liza Fernandez'),
    ('CHS', 'College of Health Sciences', 'Dr. Mark Villanueva');

-- ------------------------------------------------------------
-- Programs
-- ------------------------------------------------------------
INSERT INTO program (prog_code, prog_name, dept_id, prog_credits_required) VALUES
    ('BSIT', 'Bachelor of Science in Information Technology', 1, 144),
    ('BSCS', 'Bachelor of Science in Computer Science', 1, 150),
    ('BSBA', 'Bachelor of Science in Business Administration', 2, 120),
    ('BSN',  'Bachelor of Science in Nursing', 3, 168);

-- ------------------------------------------------------------
-- Terms
-- ------------------------------------------------------------
INSERT INTO term (semester, school_year) VALUES
    ('1st', '2024-2025'),
    ('2nd', '2024-2025'),
    ('1st', '2025-2026'),
    ('2nd', '2025-2026');

-- ------------------------------------------------------------
-- Courses (mix of units, includes IM/NET/IT prefixes like PLV's)
-- ------------------------------------------------------------
INSERT INTO course (course_code, course_title, course_description, course_units) VALUES
    ('IM-101', 'Introduction to Databases', 'Fundamentals of database systems and SQL.', 3),
    ('IM-102', 'Advanced Database Systems', 'Constraints, ETL, and data analysis pipelines.', 3),
    ('NET-101', 'Networking Fundamentals', 'Intro to networking concepts and the OSI model.', 3),
    ('NET-102', 'Advanced Networking', 'VLANs, routing protocols, and network security.', 3),
    ('WS-101',  'Web Systems', 'Web development using HTML, CSS, PHP, and MySQL.', 3),
    ('IT-101',  'Object-Oriented Programming', 'OOP principles using Java or Python.', 4),
    ('CS-201',  'Data Structures and Algorithms', 'Core CS data structures and algorithm design.', 4),
    ('GE-001',  'Purposive Communication', 'General education communication course.', 3);

-- ------------------------------------------------------------
-- Students (varied programs, sections, statuses, completeness)
-- ------------------------------------------------------------
INSERT INTO student
    (stud_no, stud_fname, stud_lname, prog_id, year_level, section,
     stud_email, stud_phone, stud_gender, stud_dob, stud_address, stud_status)
VALUES
    ('2025-00001', 'Juan',     'Dela Cruz', 1, 2, 'BSIT-2A', 'juan.delacruz@plv.edu.ph',  '09171234567', 'M', '2004-03-15', 'Valenzuela City', 'A'),
    ('2025-00002', 'Maria',    'Santos',    1, 2, 'BSIT-2A', 'maria.santos@plv.edu.ph',   '09189876543', 'F', '2004-07-22', 'Valenzuela City', 'A'),
    ('2025-00003', 'Pedro',    'Reyes',     1, 2, 'BSIT-2B', NULL,                         NULL,          'M', '2003-11-02', 'Caloocan City',    'A'),
    ('2025-00004', 'Andrea',   'Gonzales',  2, 2, 'BSCS-2A', 'andrea.gonzales@plv.edu.ph', '09201234567', 'F', '2004-01-30', 'Malabon City',     'A'),
    ('2025-00005', 'Mark',     'Villar',    1, 3, 'BSIT-3A', 'mark.villar@plv.edu.ph',     '09175558899', 'M', '2003-05-18', 'Quezon City',      'A'),
    ('2025-00006', 'Angelica', 'Ramos',     3, 1, 'BSBA-1A', 'angelica.ramos@plv.edu.ph',  '09221112233', 'F', '2005-09-09', 'Valenzuela City',  'A'),
    ('2025-00007', 'Yves',     'Repayo',    1, 2, 'BSIT-2A', 'yves.repayo@plv.edu.ph',     '09173334455', 'M', '2004-04-12', 'Valenzuela City',  'A'),
    ('2025-00008', 'Andy',     'Hamon',     1, 2, 'BSIT-2A', 'andy.hamon@plv.edu.ph',      '09176667788', 'M', '2004-08-25', 'Valenzuela City',  'A'),
    ('2024-00045', 'Kristine', 'Bautista',  4, 4, 'BSN-4A',  'kristine.bautista@plv.edu.ph','09194445566','F', '2002-12-01', 'Navotas City',     'I'),  -- inactive example
    ('2025-00009', 'Carlo',    'Mendoza',   2, 1, 'BSCS-1A', 'carlo.mendoza@plv.edu.ph',   '09181237890', 'M', '2005-02-14', 'Manila City',      'A');

-- ------------------------------------------------------------
-- Enrollments (mix of completed/enrolled/dropped, varied scores)
-- ------------------------------------------------------------

-- Juan Dela Cruz (stud_id 1) — 1st Sem 2025-2026, completed grades
INSERT INTO enrollment (stud_id, course_id, term_id, raw_score, final_grade, letter_grade, status) VALUES
    (1, 2, 3, 92.50, 1.25, 'A',  'COMPLETED'),  -- IM-102
    (1, 4, 3, 88.00, 1.50, 'B+', 'COMPLETED'),  -- NET-102
    (1, 5, 3, 95.00, 1.00, 'A',  'COMPLETED');  -- WS-101

-- Maria Santos (stud_id 2) — same term, different performance
INSERT INTO enrollment (stud_id, course_id, term_id, raw_score, final_grade, letter_grade, status) VALUES
    (2, 2, 3, 78.00, 2.25, 'C+', 'COMPLETED'),
    (2, 4, 3, 65.50, 3.00, 'C',  'COMPLETED'),
    (2, 5, 3, NULL,  NULL, NULL, 'ENROLLED');  -- currently taking, no grade yet

-- Pedro Reyes (stud_id 3) — failing example
INSERT INTO enrollment (stud_id, course_id, term_id, raw_score, final_grade, letter_grade, status) VALUES
    (3, 2, 3, 58.00, 4.00, 'D',  'COMPLETED'),
    (3, 4, 3, 45.00, 5.00, 'F',  'COMPLETED'),
    (3, 6, 3, NULL,  NULL, NULL, 'DROPPED');   -- dropped subject example

-- Andrea Gonzales (stud_id 4) — BSCS student
INSERT INTO enrollment (stud_id, course_id, term_id, raw_score, final_grade, letter_grade, status) VALUES
    (4, 7, 3, 90.00, 1.25, 'A',  'COMPLETED'),
    (4, 6, 3, 85.00, 1.50, 'B+', 'COMPLETED');

-- Mark Villar (stud_id 5) — older term, for trend/history analysis
INSERT INTO enrollment (stud_id, course_id, term_id, raw_score, final_grade, letter_grade, status) VALUES
    (5, 1, 1, 80.00, 2.00, 'B',  'COMPLETED'),  -- 1st Sem 2024-2025
    (5, 2, 3, 91.00, 1.25, 'A',  'COMPLETED');  -- 1st Sem 2025-2026 (same course retaken term differs)

-- Angelica Ramos (stud_id 6) — BSBA, GE subject
INSERT INTO enrollment (stud_id, course_id, term_id, raw_score, final_grade, letter_grade, status) VALUES
    (6, 8, 3, 88.50, 1.50, 'B+', 'COMPLETED');

-- Yves Repayo & Andy Hamon (stud_id 7, 8) — same section as Juan, for class average testing
INSERT INTO enrollment (stud_id, course_id, term_id, raw_score, final_grade, letter_grade, status) VALUES
    (7, 2, 3, 84.00, 1.75, 'B',  'COMPLETED'),
    (7, 4, 3, 79.00, 2.25, 'C+', 'COMPLETED'),
    (8, 2, 3, 96.00, 1.00, 'A',  'COMPLETED'),
    (8, 4, 3, 91.00, 1.25, 'A',  'COMPLETED');

-- Carlo Mendoza (stud_id 10) — new enrollee, no grades yet
INSERT INTO enrollment (stud_id, course_id, term_id, raw_score, final_grade, letter_grade, status) VALUES
    (10, 1, 3, NULL, NULL, NULL, 'ENROLLED'),
    (10, 8, 3, NULL, NULL, NULL, 'ENROLLED');


-- -- ------------------------------------------------------------
-- -- Users (admin, teacher, and a couple of student-linked logins)
-- -- Passwords below are PLAIN TEXT placeholders for demo only —
-- -- always hash with bcrypt before inserting in real app code.
-- -- ------------------------------------------------------------
-- INSERT INTO users (username, password_hash, role, stud_id) VALUES
--     ('admin',        '$2b$12$REPLACE_WITH_BCRYPT_HASH', 'admin',   NULL),
--     ('apostol.r',    '$2b$12$REPLACE_WITH_BCRYPT_HASH', 'teacher', NULL),
--     ('juan.delacruz','$2b$12$REPLACE_WITH_BCRYPT_HASH', 'student', 1),
--     ('maria.santos', '$2b$12$REPLACE_WITH_BCRYPT_HASH', 'student', 2);