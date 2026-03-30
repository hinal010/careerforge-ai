from database import conn

cur = conn.cursor()

# =========================
# USERS TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    full_name TEXT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
)
""")

# =========================
# ADMIN USERS TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
)
""")

# =========================
# USER PROFILE TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    full_name TEXT,
    email TEXT,
    contact TEXT,
    location TEXT,
    country TEXT,
    linkedin TEXT,
    github TEXT,
    photo TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

# =========================
# DEGREE MASTER TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS degree_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    degree_name TEXT NOT NULL UNIQUE
)
""")

# =========================
# COURSE MASTER TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS course_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    degree_id INTEGER,
    course_name TEXT NOT NULL,
    FOREIGN KEY (degree_id) REFERENCES degree_master(id) ON DELETE CASCADE
)
""")

# =========================
# INSTITUTE MASTER TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS institute_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER,
    institute_name TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES course_master(id) ON DELETE CASCADE
)
""")

# =========================
# EXPERIENCE TYPE MASTER TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS experience_type_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE
)
""")

# =========================
# JOB TITLE MASTER TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS job_title_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL UNIQUE
)
""")

# =========================
# EDUCATION TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    degree_id INTEGER,
    course_id INTEGER,
    institution_id INTEGER,
    location TEXT,
    start_month TEXT,
    end_month TEXT,
    grade TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (degree_id) REFERENCES degree_master(id),
    FOREIGN KEY (course_id) REFERENCES course_master(id),
    FOREIGN KEY (institution_id) REFERENCES institute_master(id)
)
""")

# =========================
# EXPERIENCE TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_title_id INTEGER,
    custom_job_title TEXT,
    experience_type_id INTEGER,
    company_name TEXT,
    location TEXT,
    start_month TEXT,
    end_month TEXT,
    currently_working INTEGER DEFAULT 0,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_title_id) REFERENCES job_title_master(id),
    FOREIGN KEY (experience_type_id) REFERENCES experience_type_master(id)
)
""")

# =========================
# USER SKILLS TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS user_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    job_role_id INTEGER,
    custom_job_role TEXT,
    languages TEXT,
    frameworks TEXT,
    tools TEXT,
    cloud_platforms TEXT,
    databases TEXT,
    methodologies TEXT,
    soft_skills TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_role_id) REFERENCES job_title_master(id)
)
""")

# =========================
# PROJECT TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    project_title TEXT NOT NULL,
    technologies TEXT,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

# =========================
# PROFESSIONAL SUMMARY TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS professional_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    professional_summary TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

# =========================
# CERTIFICATION TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS certification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    certificate_name TEXT NOT NULL,
    organization TEXT NOT NULL,
    certificate_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

# =========================
# CHOOSE TEMPLATE TABLE
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS selected_template (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    template_name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")

conn.commit()