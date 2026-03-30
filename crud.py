from database import conn
from auth import hash_password


# =========================================================
# USER AUTH
# =========================================================
def create_user(username: str, full_name: str, email: str, password: str):
    hashed = hash_password(password)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (username, full_name, email, hashed_password)
        VALUES (?, ?, ?, ?)
    """, (username, full_name, email, hashed))

    conn.commit()
    return get_user_by_email(email)


def get_user(username: str):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, full_name, email, hashed_password
        FROM users
        WHERE username = ?
    """, (username,))
    row = cur.fetchone()
    return dict(row) if row else None


def get_user_by_email(email: str):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, full_name, email, hashed_password
        FROM users
        WHERE email = ?
    """, (email,))
    row = cur.fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, full_name, email, hashed_password
        FROM users
        WHERE id = ?
    """, (user_id,))
    row = cur.fetchone()
    return dict(row) if row else None


# =========================================================
# ADMIN AUTH
# =========================================================
def create_admin_user(email: str, password: str):
    hashed = hash_password(password)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO admin_users (email, hashed_password)
        VALUES (?, ?)
    """, (email, hashed))

    conn.commit()


def get_admin_by_email(email: str):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, email, hashed_password
        FROM admin_users
        WHERE email = ?
    """, (email,))
    row = cur.fetchone()
    return dict(row) if row else None


# =========================================================
# PROFILE
# =========================================================
def create_user_profile(
    user_id,
    full_name="",
    email="",
    contact="",
    location="",
    country="",
    linkedin="",
    github="",
    photo=""
):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_profile
        (user_id, full_name, email, contact, location, country, linkedin, github, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, full_name, email, contact, location, country, linkedin, github, photo))
    conn.commit()


def get_user_profile(user_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def update_user_profile(
    user_id,
    full_name=None,
    email=None,
    contact=None,
    location=None,
    country=None,
    linkedin=None,
    github=None,
    photo=None
):
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if row is None:
        cur.execute("""
            INSERT INTO user_profile
            (user_id, full_name, email, contact, location, country, linkedin, github, photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            full_name or "",
            email or "",
            contact or "",
            location or "",
            country or "",
            linkedin or "",
            github or "",
            photo or ""
        ))
        conn.commit()
    else:
        updates = []
        params = []

        if full_name is not None:
            updates.append("full_name = ?")
            params.append(full_name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if contact is not None:
            updates.append("contact = ?")
            params.append(contact)
        if location is not None:
            updates.append("location = ?")
            params.append(location)
        if country is not None:
            updates.append("country = ?")
            params.append(country)
        if linkedin is not None:
            updates.append("linkedin = ?")
            params.append(linkedin)
        if github is not None:
            updates.append("github = ?")
            params.append(github)
        if photo is not None:
            updates.append("photo = ?")
            params.append(photo)

        if updates:
            params.append(user_id)
            query = f"UPDATE user_profile SET {', '.join(updates)} WHERE user_id = ?"
            cur.execute(query, params)
            conn.commit()

    return get_user_profile(user_id)


# =========================================================
# EDUCATION
# =========================================================
def add_education(user_id, degree, course, institution, location, start_month, end_month, grade):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO education
        (user_id, degree_id, course_id, institution_id, location, start_month, end_month, grade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, degree, course, institution, location, start_month, end_month, grade))
    conn.commit()


def get_education(user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT
            e.id,
            e.user_id,
            e.degree_id,
            e.course_id,
            e.institution_id,
            d.degree_name,
            c.course_name,
            i.institute_name,
            e.location,
            e.start_month,
            e.end_month,
            e.grade
        FROM education e
        LEFT JOIN degree_master d ON e.degree_id = d.id
        LEFT JOIN course_master c ON e.course_id = c.id
        LEFT JOIN institute_master i ON e.institution_id = i.id
        WHERE e.user_id = ?
        ORDER BY e.id DESC
    """, (user_id,))
    return cur.fetchall()


def get_education_by_id(edu_id, user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM education
        WHERE id = ? AND user_id = ?
    """, (edu_id, user_id))
    row = cur.fetchone()
    return dict(row) if row else None


def update_education(edu_id, degree, course, institution, location, start_month, end_month, grade):
    cur = conn.cursor()
    cur.execute("""
        UPDATE education
        SET degree_id = ?, course_id = ?, institution_id = ?, location = ?,
            start_month = ?, end_month = ?, grade = ?
        WHERE id = ?
    """, (degree, course, institution, location, start_month, end_month, grade, edu_id))
    conn.commit()


def delete_education(edu_id, user_id):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM education
        WHERE id = ? AND user_id = ?
    """, (edu_id, user_id))
    conn.commit()


# =========================================================
# EXPERIENCE
# =========================================================
def add_experience(
    user_id,
    job_title_id,
    custom_job_title,
    experience_type_id,
    company_name,
    location,
    start_month,
    end_month,
    currently_working,
    description
):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO experience
        (user_id, job_title_id, custom_job_title, experience_type_id,
         company_name, location, start_month, end_month,
         currently_working, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, job_title_id, custom_job_title, experience_type_id,
        company_name, location, start_month, end_month,
        currently_working, description
    ))
    conn.commit()


def get_experience(user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT
            e.id,
            e.user_id,
            e.job_title_id,
            e.custom_job_title,
            e.experience_type_id,
            etm.type_name,
            COALESCE(j.job_title, e.custom_job_title) AS job_title_name,
            e.company_name,
            e.location,
            e.start_month,
            e.end_month,
            e.currently_working,
            e.description
        FROM experience e
        LEFT JOIN job_title_master j ON e.job_title_id = j.id
        LEFT JOIN experience_type_master etm ON e.experience_type_id = etm.id
        WHERE e.user_id = ?
        ORDER BY e.id DESC
    """, (user_id,))
    return cur.fetchall()


def get_experience_by_id(exp_id, user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM experience
        WHERE id = ? AND user_id = ?
    """, (exp_id, user_id))
    row = cur.fetchone()
    return dict(row) if row else None


def update_experience(
    exp_id,
    job_title_id,
    custom_job_title,
    experience_type_id,
    company_name,
    location,
    start_month,
    end_month,
    currently_working,
    description
):
    cur = conn.cursor()
    cur.execute("""
        UPDATE experience
        SET job_title_id = ?, custom_job_title = ?, experience_type_id = ?,
            company_name = ?, location = ?, start_month = ?, end_month = ?,
            currently_working = ?, description = ?
        WHERE id = ?
    """, (
        job_title_id, custom_job_title, experience_type_id,
        company_name, location, start_month, end_month,
        currently_working, description, exp_id
    ))
    conn.commit()


def delete_experience(exp_id, user_id):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM experience
        WHERE id = ? AND user_id = ?
    """, (exp_id, user_id))
    conn.commit()


# =========================================================
# SKILLS
# =========================================================
def save_skills(
    user_id,
    job_role_id=None,
    custom_job_role=None,
    languages="",
    frameworks="",
    tools="",
    cloud_platforms="",
    databases="",
    methodologies="",
    soft_skills=""
):
    cur = conn.cursor()
    cur.execute("SELECT id FROM user_skills WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if row:
        cur.execute("""
            UPDATE user_skills
            SET job_role_id = ?, custom_job_role = ?, languages = ?, frameworks = ?,
                tools = ?, cloud_platforms = ?, databases = ?, methodologies = ?,
                soft_skills = ?
            WHERE user_id = ?
        """, (
            job_role_id, custom_job_role, languages, frameworks,
            tools, cloud_platforms, databases, methodologies,
            soft_skills, user_id
        ))
    else:
        cur.execute("""
            INSERT INTO user_skills
            (user_id, job_role_id, custom_job_role, languages, frameworks,
             tools, cloud_platforms, databases, methodologies, soft_skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, job_role_id, custom_job_role, languages, frameworks,
            tools, cloud_platforms, databases, methodologies, soft_skills
        ))

    conn.commit()


def get_skills(user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT
            us.*,
            j.job_title AS job_role_name
        FROM user_skills us
        LEFT JOIN job_title_master j ON us.job_role_id = j.id
        WHERE us.user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    return dict(row) if row else None


# =========================================================
# PROJECTS
# =========================================================
def add_project(user_id, project_title, technologies, description):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO projects (user_id, project_title, technologies, description)
        VALUES (?, ?, ?, ?)
    """, (user_id, project_title, technologies, description))
    conn.commit()


def get_projects(user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, project_title, technologies, description
        FROM projects
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    return cur.fetchall()


def get_project_by_id(project_id, user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM projects
        WHERE id = ? AND user_id = ?
    """, (project_id, user_id))
    row = cur.fetchone()
    return dict(row) if row else None


def update_project(project_id, project_title, technologies, description):
    cur = conn.cursor()
    cur.execute("""
        UPDATE projects
        SET project_title = ?, technologies = ?, description = ?
        WHERE id = ?
    """, (project_title, technologies, description, project_id))
    conn.commit()


def delete_project(project_id, user_id):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM projects
        WHERE id = ? AND user_id = ?
    """, (project_id, user_id))
    conn.commit()


# =========================================================
# PROFESSIONAL SUMMARY
# =========================================================
def save_professional_summary(user_id, professional_summary):
    cur = conn.cursor()
    cur.execute("SELECT id FROM professional_summary WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if row:
        cur.execute("""
            UPDATE professional_summary
            SET professional_summary = ?
            WHERE user_id = ?
        """, (professional_summary, user_id))
    else:
        cur.execute("""
            INSERT INTO professional_summary (user_id, professional_summary)
            VALUES (?, ?)
        """, (user_id, professional_summary))

    conn.commit()


def get_professional_summary(user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM professional_summary
        WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    return dict(row) if row else None


# =========================================================
# CERTIFICATION
# =========================================================
def add_certification(user_id, certificate_name, organization, certificate_date):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO certification (user_id, certificate_name, organization, certificate_date)
        VALUES (?, ?, ?, ?)
    """, (user_id, certificate_name, organization, certificate_date))
    conn.commit()


def get_certifications(user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, user_id, certificate_name, organization, certificate_date
        FROM certification
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    return cur.fetchall()


def get_certification_by_id(cert_id, user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM certification
        WHERE id = ? AND user_id = ?
    """, (cert_id, user_id))
    row = cur.fetchone()
    return dict(row) if row else None


def update_certification(cert_id, certificate_name, organization, certificate_date):
    cur = conn.cursor()
    cur.execute("""
        UPDATE certification
        SET certificate_name = ?, organization = ?, certificate_date = ?
        WHERE id = ?
    """, (certificate_name, organization, certificate_date, cert_id))
    conn.commit()


def delete_certification(cert_id, user_id):
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM certification
        WHERE id = ? AND user_id = ?
    """, (cert_id, user_id))
    conn.commit()


# =========================================================
# TEMPLATE SELECTION
# =========================================================
def save_selected_template(user_id, template_name):
    cur = conn.cursor()
    cur.execute("SELECT id FROM selected_template WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if row:
        cur.execute("""
            UPDATE selected_template
            SET template_name = ?
            WHERE user_id = ?
        """, (template_name, user_id))
    else:
        cur.execute("""
            INSERT INTO selected_template (user_id, template_name)
            VALUES (?, ?)
        """, (user_id, template_name))

    conn.commit()


def get_selected_template(user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM selected_template
        WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()
    return dict(row) if row else None


# =========================================================
# MASTER TABLES - FOR USER FORMS
# =========================================================
def get_degrees():
    cur = conn.cursor()
    cur.execute("SELECT id, degree_name FROM degree_master ORDER BY degree_name")
    return cur.fetchall()


def get_degree_by_id(degree_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, degree_name
        FROM degree_master
        WHERE id = ?
    """, (degree_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def get_courses_by_degree(degree_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, course_name
        FROM course_master
        WHERE degree_id = ?
        ORDER BY course_name
    """, (degree_id,))
    return cur.fetchall()


def get_all_courses():
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.course_name, c.degree_id, d.degree_name
        FROM course_master c
        LEFT JOIN degree_master d ON c.degree_id = d.id
        ORDER BY c.id DESC
    """)
    return cur.fetchall()


def get_course_by_id(course_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.course_name, c.degree_id, d.degree_name
        FROM course_master c
        LEFT JOIN degree_master d ON c.degree_id = d.id
        WHERE c.id = ?
    """, (course_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def get_institutes_by_course(course_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, institute_name
        FROM institute_master
        WHERE course_id = ?
        ORDER BY institute_name
    """, (course_id,))
    return cur.fetchall()


def get_all_institutes():
    cur = conn.cursor()
    cur.execute("""
        SELECT i.id, i.institute_name, i.course_id, c.course_name
        FROM institute_master i
        LEFT JOIN course_master c ON i.course_id = c.id
        ORDER BY i.id DESC
    """)
    return cur.fetchall()


def get_institute_by_id(institute_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT i.id, i.institute_name, i.course_id, c.course_name
        FROM institute_master i
        LEFT JOIN course_master c ON i.course_id = c.id
        WHERE i.id = ?
    """, (institute_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def get_experience_types():
    cur = conn.cursor()
    cur.execute("""
        SELECT id, type_name
        FROM experience_type_master
        ORDER BY type_name
    """)
    return cur.fetchall()


def get_experience_type_by_id(type_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, type_name
        FROM experience_type_master
        WHERE id = ?
    """, (type_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def get_job_titles():
    cur = conn.cursor()
    cur.execute("""
        SELECT id, job_title
        FROM job_title_master
        ORDER BY job_title
    """)
    return cur.fetchall()


def get_job_title_by_id(job_title_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, job_title
        FROM job_title_master
        WHERE id = ?
    """, (job_title_id,))
    row = cur.fetchone()
    return dict(row) if row else None


# =========================================================
# ADMIN PANEL CRUD
# =========================================================
def add_degree(degree_name):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO degree_master (degree_name)
        VALUES (?)
    """, (degree_name,))
    conn.commit()


def update_degree(degree_id, degree_name):
    cur = conn.cursor()
    cur.execute("""
        UPDATE degree_master
        SET degree_name = ?
        WHERE id = ?
    """, (degree_name, degree_id))
    conn.commit()


def delete_degree(degree_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM degree_master WHERE id = ?", (degree_id,))
    conn.commit()


def add_course(degree_id, course_name):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO course_master (degree_id, course_name)
        VALUES (?, ?)
    """, (degree_id, course_name))
    conn.commit()


def update_course(course_id, degree_id, course_name):
    cur = conn.cursor()
    cur.execute("""
        UPDATE course_master
        SET degree_id = ?, course_name = ?
        WHERE id = ?
    """, (degree_id, course_name, course_id))
    conn.commit()


def delete_course(course_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM course_master WHERE id = ?", (course_id,))
    conn.commit()


def add_institute(course_id, institute_name):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO institute_master (course_id, institute_name)
        VALUES (?, ?)
    """, (course_id, institute_name))
    conn.commit()


def update_institute(institute_id, course_id, institute_name):
    cur = conn.cursor()
    cur.execute("""
        UPDATE institute_master
        SET course_id = ?, institute_name = ?
        WHERE id = ?
    """, (course_id, institute_name, institute_id))
    conn.commit()


def delete_institute(institute_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM institute_master WHERE id = ?", (institute_id,))
    conn.commit()


def add_job_title(job_title):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO job_title_master (job_title)
        VALUES (?)
    """, (job_title,))
    conn.commit()


def update_job_title(job_title_id, job_title):
    cur = conn.cursor()
    cur.execute("""
        UPDATE job_title_master
        SET job_title = ?
        WHERE id = ?
    """, (job_title, job_title_id))
    conn.commit()


def delete_job_title(job_title_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM job_title_master WHERE id = ?", (job_title_id,))
    conn.commit()


def add_experience_type(type_name):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO experience_type_master (type_name)
        VALUES (?)
    """, (type_name,))
    conn.commit()


def update_experience_type(type_id, type_name):
    cur = conn.cursor()
    cur.execute("""
        UPDATE experience_type_master
        SET type_name = ?
        WHERE id = ?
    """, (type_name, type_id))
    conn.commit()


def delete_experience_type(type_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM experience_type_master WHERE id = ?", (type_id,))
    conn.commit()


# =========================================================
# ADMIN USER LIST / SEARCH / DETAIL
# =========================================================
def get_all_users():
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, full_name, email
        FROM users
        ORDER BY id DESC
    """)
    return cur.fetchall()


def search_users(keyword):
    cur = conn.cursor()
    like_value = f"%{keyword}%"
    cur.execute("""
        SELECT id, username, full_name, email
        FROM users
        WHERE username LIKE ? OR full_name LIKE ? OR email LIKE ?
        ORDER BY id DESC
    """, (like_value, like_value, like_value))
    return cur.fetchall()


def get_admin_user_detail(user_id):
    cur = conn.cursor()

    user = cur.execute("""
        SELECT id, username, full_name, email
        FROM users
        WHERE id = ?
    """, (user_id,)).fetchone()

    profile = cur.execute("""
        SELECT *
        FROM user_profile
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    education = cur.execute("""
        SELECT
            e.*,
            d.degree_name,
            c.course_name,
            i.institute_name
        FROM education e
        LEFT JOIN degree_master d ON e.degree_id = d.id
        LEFT JOIN course_master c ON e.course_id = c.id
        LEFT JOIN institute_master i ON e.institution_id = i.id
        WHERE e.user_id = ?
        ORDER BY e.id DESC
    """, (user_id,)).fetchall()

    experience = cur.execute("""
        SELECT
            e.*,
            etm.type_name,
            COALESCE(j.job_title, e.custom_job_title) AS job_title_name
        FROM experience e
        LEFT JOIN experience_type_master etm ON e.experience_type_id = etm.id
        LEFT JOIN job_title_master j ON e.job_title_id = j.id
        WHERE e.user_id = ?
        ORDER BY e.id DESC
    """, (user_id,)).fetchall()

    skills = cur.execute("""
        SELECT
            us.*,
            j.job_title AS job_role_name
        FROM user_skills us
        LEFT JOIN job_title_master j ON us.job_role_id = j.id
        WHERE us.user_id = ?
    """, (user_id,)).fetchone()

    projects = cur.execute("""
        SELECT *
        FROM projects
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    summary = cur.execute("""
        SELECT *
        FROM professional_summary
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    certifications = cur.execute("""
        SELECT *
        FROM certification
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    template = cur.execute("""
        SELECT *
        FROM selected_template
        WHERE user_id = ?
    """, (user_id,)).fetchone()

    return {
        "user": dict(user) if user else None,
        "profile": dict(profile) if profile else None,
        "education": [dict(x) for x in education],
        "experience": [dict(x) for x in experience],
        "skills": dict(skills) if skills else None,
        "projects": [dict(x) for x in projects],
        "summary": dict(summary) if summary else None,
        "certifications": [dict(x) for x in certifications],
        "template": dict(template) if template else None,
    }