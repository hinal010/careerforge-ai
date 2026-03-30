import shutil
from pathlib import Path

from fastapi import FastAPI, Request, Form, File, UploadFile, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import models
from auth import verify_password
from auth_config import SESSION_SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD
from crud import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    

    get_user_profile,
    update_user_profile,

    add_education,
    get_education,
    get_education_by_id,
    update_education,
    delete_education,

    add_experience,
    get_experience,
    get_experience_by_id,
    get_experience_type_by_id,
    add_experience_type,
    update_experience_type,
    delete_experience_type,
    update_experience,
    delete_experience,

    save_skills,
    get_skills,

    add_project,
    get_projects,
    get_project_by_id,
    update_project,
    delete_project,

    save_professional_summary,
    get_professional_summary,

    add_certification,
    get_certifications,
    get_certification_by_id,
    update_certification,
    delete_certification,

    save_selected_template,
    get_selected_template,

    get_degrees,
    get_all_courses,
    get_all_institutes,
    get_experience_types,
    get_job_titles,

    add_degree,
    delete_degree,
    add_course,
    delete_course,
    add_institute,
    delete_institute,
    add_job_title,
    delete_job_title,

    get_all_users,
    search_users,
    get_admin_user_detail,
)
from database import conn

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY or "careerforge_session_secret"
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "template"
UPLOAD_DIR = STATIC_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


# =========================================================
# HELPERS
# =========================================================
def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


def get_current_admin(request: Request):
    admin_id = request.session.get("admin_id")
    admin_email = request.session.get("admin_email")
    if not admin_id or not admin_email:
        return None
    return {"id": admin_id, "email": admin_email}


def require_login(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return user


def require_admin(request: Request):
    admin = get_current_admin(request)
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=303)
    return admin


def save_upload_file(upload_file: UploadFile):
    if not upload_file or not upload_file.filename:
        return None

    file_name = upload_file.filename.replace(" ", "_")
    file_path = UPLOAD_DIR / file_name

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return f"/static/uploads/{file_name}"


def get_resume_status(user_id: int):
    profile = get_user_profile(user_id)
    education = get_education(user_id)
    experience = get_experience(user_id)
    skills = get_skills(user_id)
    projects = get_projects(user_id)
    summary = get_professional_summary(user_id)
    certifications = get_certifications(user_id)

    score = 0
    if profile:
        score += 1
    if education:
        score += 1
    if experience:
        score += 1
    if skills:
        score += 1
    if projects:
        score += 1
    if summary:
        score += 1
    if certifications:
        score += 1

    if score >= 5:
        return "Completed"
    elif score >= 2:
        return "In Progress"
    return "Incomplete"


def get_job_role_text_from_skills(skills_data):
    if not skills_data:
        return ""

    if skills_data.get("job_role_name"):
        return skills_data["job_role_name"]

    if skills_data.get("custom_job_role"):
        return skills_data["custom_job_role"]

    return ""


def build_admin_user_list(rows):
    result = []
    for row in rows:
        user = dict(row)
        skills_data = get_skills(user["id"])
        user["job_role"] = get_job_role_text_from_skills(skills_data)
        user["status"] = get_resume_status(user["id"])
        result.append(user)
    return result


def admin_dashboard_stats():
    cur = conn.cursor()

    total_users = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_job_titles = cur.execute("SELECT COUNT(*) FROM job_title_master").fetchone()[0]
    total_degrees = cur.execute("SELECT COUNT(*) FROM degree_master").fetchone()[0]
    total_courses = cur.execute("SELECT COUNT(*) FROM course_master").fetchone()[0]
    total_resumes = cur.execute("SELECT COUNT(*) FROM selected_template").fetchone()[0]

    recent_raw = cur.execute("""
        SELECT id, username, full_name, email
        FROM users
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    recent_users = build_admin_user_list(recent_raw)

    all_users_raw = cur.execute("""
        SELECT id, username, full_name, email
        FROM users
        ORDER BY id DESC
    """).fetchall()

    total_count = len(all_users_raw)
    completed_count = 0
    progress_count = 0
    incomplete_count = 0

    for row in all_users_raw:
        status = get_resume_status(row["id"])
        if status == "Completed":
            completed_count += 1
        elif status == "In Progress":
            progress_count += 1
        else:
            incomplete_count += 1

    def percent(part, whole):
        if whole == 0:
            return 0
        return round((part / whole) * 100)

    completed_percent = percent(completed_count, total_count)
    progress_percent = percent(progress_count, total_count)
    incomplete_percent = percent(incomplete_count, total_count)

    top_roles_rows = cur.execute("""
        SELECT
            COALESCE(j.job_title, us.custom_job_role) AS role_name,
            COUNT(*) as total
        FROM user_skills us
        LEFT JOIN job_title_master j ON us.job_role_id = j.id
        WHERE COALESCE(j.job_title, us.custom_job_role) IS NOT NULL
          AND COALESCE(j.job_title, us.custom_job_role) != ''
        GROUP BY COALESCE(j.job_title, us.custom_job_role)
        ORDER BY total DESC
        LIMIT 5
    """).fetchall()

    top_roles = [{"role_name": row[0], "total": row[1]} for row in top_roles_rows]

    return {
        "total_users": total_users,
        "total_resumes": total_resumes,
        "total_job_titles": total_job_titles,
        "total_courses_degrees": total_courses + total_degrees,
        "recent_users": recent_users,
        "completed_percent": completed_percent,
        "progress_percent": progress_percent,
        "incomplete_percent": incomplete_percent,
        "top_roles": top_roles,
    }


# =========================================================
# PUBLIC ROUTES
# =========================================================
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "user": user
        }
    )


# =========================================================
# REGISTER / LOGIN / LOGOUT
# =========================================================
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/profile", status_code=303)

    return templates.TemplateResponse(
        request,
        "register.html",
        {
            "request": request
        }
    )


@app.post("/register")
@app.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    existing_user = get_user_by_email(email)
    if existing_user:
        return templates.TemplateResponse(
            request,
            "register.html",
            {
                "request": request,
                "error": "Email already registered"
            }
        )

    create_user(username, full_name, email, password)

    return RedirectResponse(url="/login?msg=registered", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/profile", status_code=303)

    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "request": request
        }
    )


@app.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    user = get_user_by_email(email)

    if not user or not verify_password(password, user["hashed_password"]):
        return templates.TemplateResponse(
            request,
            "login.html",
            {
                "request": request,
                "error": "Invalid email or password"
            }
        )

    request.session["user_id"] = user["id"]
    request.session["user_email"] = user["email"]
    request.session["user_name"] = user["full_name"]

    return RedirectResponse(url="/profile", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/auth/google")
def auth_google():
    return RedirectResponse(url="/login", status_code=303)


# =========================================================
# PROFILE
# =========================================================
@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    profile = get_user_profile(user["id"])

    return templates.TemplateResponse(
        request,
        "profile.html",
        {
            "request": request,
            "user": user,
            "profile": profile,
            "step": 1
        }
    )


@app.post("/profile")
def save_profile(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    contact: str = Form(""),
    location: str = Form(""),
    country: str = Form(""),
    linkedin: str = Form(""),
    github: str = Form(""),
    photo: UploadFile = File(None)
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    old_profile = get_user_profile(user["id"])
    photo_path = old_profile["photo"] if old_profile and old_profile.get("photo") else ""

    if photo and photo.filename:
        uploaded = save_upload_file(photo)
        if uploaded:
            photo_path = uploaded

    update_user_profile(
        user_id=user["id"],
        full_name=full_name,
        email=email,
        contact=contact,
        location=location,
        country=country,
        linkedin=linkedin,
        github=github,
        photo=photo_path
    )

    return RedirectResponse(url="/education_detail?msg=profile_saved", status_code=303)


# =========================================================
# EDUCATION
# =========================================================
@app.get("/education", response_class=HTMLResponse)
@app.get("/education_detail", response_class=HTMLResponse)
@app.get("/education.html", response_class=HTMLResponse)
def education_page(
    request: Request,
    edit_id: int | None = Query(None)
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    education_list = get_education(user["id"])
    degree_list = get_degrees()
    course_list = get_all_courses()
    institution_list = get_all_institutes()
    edit_education = get_education_by_id(edit_id, user["id"]) if edit_id else None

    return templates.TemplateResponse(
        request,
        "education.html",
        {
            "request": request,
            "user": user,
            "education_list": education_list,
            "degree_list": degree_list,
            "course_list": course_list,
            "institution_list": institution_list,
            "edit_education": edit_education,
            "step": 2
        }
    )


@app.post("/education_detail")
def save_education_detail(
    request: Request,
    education_id: int | None = Form(None),
    degree: int = Form(...),
    course: int = Form(...),
    institution: int = Form(...),
    location: str = Form(""),
    start_month: str = Form(...),
    end_month: str = Form(""),
    grade: str = Form(""),
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    if education_id:
        existing = get_education_by_id(education_id, user["id"])
        if existing:
            update_education(
                education_id,
                degree,
                course,
                institution,
                location,
                start_month,
                end_month,
                grade
            )
            return RedirectResponse(url="/education_detail?msg=updated", status_code=303)

    add_education(
        user["id"],
        degree,
        course,
        institution,
        location,
        start_month,
        end_month,
        grade
    )

    return RedirectResponse(url="/education_detail?msg=saved", status_code=303)


@app.get("/education/delete/{edu_id}")
def remove_education(request: Request, edu_id: int):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    delete_education(edu_id, user["id"])
    return RedirectResponse(url="/education_detail?msg=deleted", status_code=303)


# =========================================================
# EXPERIENCE
# =========================================================
@app.get("/experience", response_class=HTMLResponse)
@app.get("/experience_detail", response_class=HTMLResponse)
@app.get("/experience.html", response_class=HTMLResponse)
def experience_page(
    request: Request,
    edit_id: int | None = Query(None)
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    experience_list = get_experience(user["id"])
    job_title_list = get_job_titles()
    experience_type_list = get_experience_types()
    edit_experience = get_experience_by_id(edit_id, user["id"]) if edit_id else None

    return templates.TemplateResponse(
        request,
        "experience.html",
        {
            "request": request,
            "user": user,
            "experience_list": experience_list,
            "job_title_list": job_title_list,
            "experience_type_list": experience_type_list,
            "edit_experience": edit_experience,
            "step": 3
        }
    )


@app.post("/experience_detail")
def save_experience_detail(
    request: Request,
    experience_id: int | None = Form(None),
    job_title: str = Form(...),
    custom_job_title: str = Form(""),
    experience_type: int = Form(...),
    company_name: str = Form(...),
    location: str = Form(""),
    start_month: str = Form(...),
    end_month: str = Form(""),
    currently_working: str | None = Form(None),
    description: str = Form("")
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    currently_working_value = 1 if currently_working == "on" else 0

    job_title_id = None
    custom_title_value = ""

    if job_title == "other":
        custom_title_value = custom_job_title.strip()
    else:
        job_title_id = int(job_title)

    if currently_working_value == 1:
        end_month = ""

    if experience_id:
        existing = get_experience_by_id(experience_id, user["id"])
        if existing:
            update_experience(
                experience_id,
                job_title_id,
                custom_title_value,
                experience_type,
                company_name,
                location,
                start_month,
                end_month,
                currently_working_value,
                description
            )
            return RedirectResponse(url="/experience_detail?msg=updated", status_code=303)

    add_experience(
        user["id"],
        job_title_id,
        custom_title_value,
        experience_type,
        company_name,
        location,
        start_month,
        end_month,
        currently_working_value,
        description
    )

    return RedirectResponse(url="/experience_detail?msg=saved", status_code=303)


@app.get("/experience/delete/{exp_id}")
def remove_experience(request: Request, exp_id: int):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    delete_experience(exp_id, user["id"])
    return RedirectResponse(url="/experience_detail?msg=deleted", status_code=303)


# =========================================================
# SKILLS
# =========================================================
@app.get("/skills", response_class=HTMLResponse)
@app.get("/skills_projects", response_class=HTMLResponse)
@app.get("/skills.html", response_class=HTMLResponse)
def skills_page(request: Request):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    job_role_list = get_job_titles()
    skills_data = get_skills(user["id"])

    return templates.TemplateResponse(
        request,
        "skills.html",
        {
            "request": request,
            "user": user,
            "job_role_list": job_role_list,
            "skills_data": skills_data,
            "step": 6
        }
    )


@app.post("/skills_detail")
def save_skills_detail(
    request: Request,
    job_role: str = Form(...),
    custom_job_role: str = Form(""),
    languages: str = Form(""),
    frameworks: str = Form(""),
    tools: str = Form(""),
    cloud_platforms: str = Form(""),
    databases: str = Form(""),
    methodologies: str = Form(""),
    soft_skills: str = Form("")
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    job_role_id = None
    custom_role_value = ""

    if job_role == "other":
        custom_role_value = custom_job_role
    else:
        job_role_id = int(job_role)

    save_skills(
        user_id=user["id"],
        job_role_id=job_role_id,
        custom_job_role=custom_role_value,
        languages=languages,
        frameworks=frameworks,
        tools=tools,
        cloud_platforms=cloud_platforms,
        databases=databases,
        methodologies=methodologies,
        soft_skills=soft_skills
    )

    return RedirectResponse(url="/project?msg=skills_saved", status_code=303)


# =========================================================
# PROJECT
# =========================================================
@app.get("/project", response_class=HTMLResponse)
@app.get("/project_detail", response_class=HTMLResponse)
@app.get("/template/project", response_class=HTMLResponse)
def project_page(
    request: Request,
    edit_id: int | None = Query(None)
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    project_list = get_projects(user["id"])
    edit_project = get_project_by_id(edit_id, user["id"]) if edit_id else None

    return templates.TemplateResponse(
        request,
        "project.html",
        {
            "request": request,
            "user": user,
            "project_list": project_list,
            "edit_project": edit_project,
            "step": 5
        }
    )


@app.post("/project_detail")
def save_project_detail(
    request: Request,
    project_id: int | None = Form(None),
    project_title: str = Form(...),
    technologies: str = Form(""),
    description: str = Form("")
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    if project_id:
        existing = get_project_by_id(project_id, user["id"])
        if existing:
            update_project(project_id, project_title, technologies, description)
            return RedirectResponse(url="/project?msg=updated", status_code=303)

    add_project(user["id"], project_title, technologies, description)
    return RedirectResponse(url="/project?msg=saved", status_code=303)


@app.get("/project/delete/{project_id}")
def remove_project(request: Request, project_id: int):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    delete_project(project_id, user["id"])
    return RedirectResponse(url="/project?msg=deleted", status_code=303)


# =========================================================
# SUMMARY
# =========================================================
@app.get("/summary", response_class=HTMLResponse)
@app.get("/summary.html", response_class=HTMLResponse)
def summary_page(request: Request):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    summary_row = get_professional_summary(user["id"])
    saved_summary = summary_row["professional_summary"] if summary_row else ""

    return templates.TemplateResponse(
        request,
        "summary.html",
        {
            "request": request,
            "user": user,
            "saved_summary": saved_summary,
            "step": 7
        }
    )


@app.post("/save_summary")
def save_summary(request: Request, professional_summary: str = Form(...)):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    save_professional_summary(user["id"], professional_summary)
    return RedirectResponse(url="/certification?msg=summary_saved", status_code=303)


# =========================================================
# CERTIFICATION
# =========================================================
@app.get("/certification", response_class=HTMLResponse)
@app.get("/certification_detail", response_class=HTMLResponse)
@app.get("/certification.html", response_class=HTMLResponse)
def certification_page(
    request: Request,
    edit_id: int | None = Query(None)
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    certification_list = get_certifications(user["id"])
    edit_certification = get_certification_by_id(edit_id, user["id"]) if edit_id else None

    return templates.TemplateResponse(
        request,
        "certification.html",
        {
            "request": request,
            "user": user,
            "certification_list": certification_list,
            "edit_certification": edit_certification,
            "step": 4
        }
    )


@app.post("/certification_detail")
def save_certification_detail(
    request: Request,
    certification_id: int | None = Form(None),
    certificate_name: str = Form(...),
    organization: str = Form(...),
    certificate_date: str = Form(...)
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    if certification_id:
        existing = get_certification_by_id(certification_id, user["id"])
        if existing:
            update_certification(
                certification_id,
                certificate_name,
                organization,
                certificate_date
            )
            return RedirectResponse(url="/certification?msg=updated", status_code=303)

    add_certification(user["id"], certificate_name, organization, certificate_date)
    return RedirectResponse(url="/certification?msg=saved", status_code=303)


@app.get("/certification/delete/{cert_id}")
def remove_certification(request: Request, cert_id: int):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    delete_certification(cert_id, user["id"])
    return RedirectResponse(url="/certification?msg=deleted", status_code=303)


# =========================================================
# TEMPLATE CHOOSE
# =========================================================
@app.get("/choose_template", response_class=HTMLResponse)
@app.get("/choose-template", response_class=HTMLResponse)
@app.get("/template/choose_template", response_class=HTMLResponse)
def choose_template_page(request: Request):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    selected_template = get_selected_template(user["id"])

    return templates.TemplateResponse(
        request,
        "choose_template.html",
        {
            "request": request,
            "user": user,
            "selected_template": selected_template
        }
    )


# =========================================================
# RESUME PREVIEW
# =========================================================
@app.get("/resume_preview", response_class=HTMLResponse)
@app.get("/resume-preview", response_class=HTMLResponse)
def resume_preview_page(
    request: Request,
    template: str = Query(None),
    selected: str = Query(None)
):
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user

    if template and selected == "true":
        save_selected_template(user["id"], template)

    selected_row = get_selected_template(user["id"])
    selected_template_name = (
        selected_row["template_name"]
        if selected_row and selected_row.get("template_name")
        else (template if template else "classic-edge")
    )

    profile = get_user_profile(user["id"])
    educations = get_education(user["id"])
    experiences = get_experience(user["id"])
    skills = get_skills(user["id"])
    projects = get_projects(user["id"])
    certifications = get_certifications(user["id"])
    summary_row = get_professional_summary(user["id"])

    if skills:
        skills["job_role_text"] = get_job_role_text_from_skills(skills)

    return templates.TemplateResponse(
        request,
        "resume_preview.html",
        {
            "request": request,
            "user": user,
            "profile": profile,
            "educations": educations,
            "experiences": experiences,
            "skills": skills,
            "projects": projects,
            "certifications": certifications,
            "saved_summary": summary_row["professional_summary"] if summary_row else "",
            "selected_template_name": selected_template_name
        }
    )


# =========================================================
# ADMIN LOGIN / LOGOUT / DASHBOARD
# =========================================================
@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "admin/admin_login.html",
        {
            "request": request
        }
    )


@app.post("/admin/login")
def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    if email != ADMIN_EMAIL or password != ADMIN_PASSWORD:
        return templates.TemplateResponse(
            request,
            "admin/admin_login.html",
            {
                "request": request,
                "error": "Invalid admin credentials"
            }
        )

    request.session["admin_id"] = 1
    request.session["admin_email"] = ADMIN_EMAIL
    request.session["admin_name"] = ADMIN_EMAIL.split("@")[0]

    return RedirectResponse(url="/admin/dashboard", status_code=303)

@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.pop("admin_id", None)
    request.session.pop("admin_email", None)
    request.session.pop("admin_name", None)
    return RedirectResponse(url="/admin/login", status_code=303)


@app.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    stats = admin_dashboard_stats()

    return templates.TemplateResponse(
        request,
        "admin/admin_dashboard.html",
        {
            "request": request,
            "admin_name": request.session.get("admin_name", "Admin"),
            **stats
        }
    )
# =========================================================
# ADMIN USERS
# =========================================================
@app.get("/admin/users", response_class=HTMLResponse)
def admin_users_page(request: Request, q: str | None = Query(None)):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    if q and q.strip():
        users = search_users(q.strip())
    else:
        users = get_all_users()

    return templates.TemplateResponse(
        request,
        "admin/admin_users.html",
        {
            "request": request,
            "users": users,
            "q": q or ""
        }
    )


@app.get("/admin/users/{user_id}", response_class=HTMLResponse)
def admin_user_detail_page(request: Request, user_id: int):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    user_data = get_admin_user_detail(user_id)

    if not user_data["user"]:
        return RedirectResponse(url="/admin/users", status_code=303)

    return templates.TemplateResponse(
        request,
        "admin/admin_user_detail.html",
        {
            "request": request,
            "user_data": user_data,
             "user": user_data["user"]
        }
    )

# =========================================================
# ADMIN DEGREE MASTER
# =========================================================
@app.get("/admin/degrees", response_class=HTMLResponse)
def admin_degrees_page(request: Request, edit_id: int | None = Query(None)):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    degrees = get_degrees()
    edit_degree = None

    if edit_id:
        cur = conn.cursor()
        edit_degree = cur.execute(
            "SELECT id, degree_name FROM degree_master WHERE id = ?",
            (edit_id,)
        ).fetchone()

    return templates.TemplateResponse(
        request,
        "admin/admin_degrees.html",
        {
            "request": request,
            "degrees": degrees,
            "edit_degree": edit_degree
        }
    )


@app.post("/admin/degrees/add")
def admin_add_degree(
    request: Request,
    degree_id: int | None = Form(None),
    degree_name: str = Form(...)
):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    cur = conn.cursor()

    if degree_id:
        cur.execute(
            "UPDATE degree_master SET degree_name = ? WHERE id = ?",
            (degree_name, degree_id)
        )
        conn.commit()
        return RedirectResponse(url="/admin/degrees", status_code=303)

    add_degree(degree_name)
    return RedirectResponse(url="/admin/degrees", status_code=303)


@app.get("/admin/degrees/delete/{degree_id}")
def admin_remove_degree(request: Request, degree_id: int):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    delete_degree(degree_id)
    return RedirectResponse(url="/admin/degrees", status_code=303)


# =========================================================
# ADMIN COURSE MASTER
# =========================================================
@app.get("/admin/courses", response_class=HTMLResponse)
def admin_courses_page(request: Request, edit_id: int | None = Query(None)):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    degrees = get_degrees()
    courses = get_all_courses()
    edit_course = None

    if edit_id:
        cur = conn.cursor()
        edit_course = cur.execute(
            "SELECT id, degree_id, course_name FROM course_master WHERE id = ?",
            (edit_id,)
        ).fetchone()

    return templates.TemplateResponse(
        request,
        "admin/admin_courses.html",
        {
            "request": request,
            "degrees": degrees,
            "courses": courses,
            "edit_course": edit_course
        }
    )


@app.post("/admin/courses/add")
def admin_add_course(
    request: Request,
    course_id: int | None = Form(None),
    degree_id: int = Form(...),
    course_name: str = Form(...)
):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    cur = conn.cursor()

    if course_id:
        cur.execute(
            "UPDATE course_master SET degree_id = ?, course_name = ? WHERE id = ?",
            (degree_id, course_name, course_id)
        )
        conn.commit()
        return RedirectResponse(url="/admin/courses", status_code=303)

    add_course(degree_id, course_name)
    return RedirectResponse(url="/admin/courses", status_code=303)


@app.get("/admin/courses/delete/{course_id}")
def admin_remove_course(request: Request, course_id: int):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    delete_course(course_id)
    return RedirectResponse(url="/admin/courses", status_code=303)


# =========================================================
# ADMIN INSTITUTE MASTER
# =========================================================
@app.get("/admin/institutes", response_class=HTMLResponse)
def admin_institutes_page(request: Request, edit_id: int | None = Query(None)):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    courses = get_all_courses()
    institutes = get_all_institutes()
    edit_institute = None

    if edit_id:
        cur = conn.cursor()
        edit_institute = cur.execute(
            "SELECT id, course_id, institute_name FROM institute_master WHERE id = ?",
            (edit_id,)
        ).fetchone()

    return templates.TemplateResponse(
        request,
        "admin/admin_institutes.html",
        {
            "request": request,
            "courses": courses,
            "institutes": institutes,
            "edit_institute": edit_institute
        }
    )


@app.post("/admin/institutes/add")
def admin_add_institute(
    request: Request,
    institute_id: int | None = Form(None),
    course_id: int = Form(...),
    institute_name: str = Form(...)
):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    cur = conn.cursor()

    if institute_id:
        cur.execute(
            "UPDATE institute_master SET course_id = ?, institute_name = ? WHERE id = ?",
            (course_id, institute_name, institute_id)
        )
        conn.commit()
        return RedirectResponse(url="/admin/institutes", status_code=303)

    add_institute(course_id, institute_name)
    return RedirectResponse(url="/admin/institutes", status_code=303)


@app.get("/admin/institutes/delete/{institute_id}")
def admin_remove_institute(request: Request, institute_id: int):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    delete_institute(institute_id)
    return RedirectResponse(url="/admin/institutes", status_code=303)


# =========================================================
# ADMIN EXPERIENCE TYPE MASTER
# =========================================================
@app.get("/admin/experience-types", response_class=HTMLResponse)
def admin_experience_types_page(request: Request, edit_id: int | None = Query(None)):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    experience_types = get_experience_types()
    edit_experience_type = None

    if edit_id:
        edit_experience_type = get_experience_type_by_id(edit_id)

    return templates.TemplateResponse(
        request,
        "admin/admin_experience_types.html",
        {
            "request": request,
            "experience_types": experience_types,
            "edit_experience_type": edit_experience_type
        }
    )


@app.post("/admin/experience-types/add")
def admin_add_experience_type(
    request: Request,
    type_id: int | None = Form(None),
    type_name: str = Form(...)
):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    type_name = type_name.strip()

    if type_id:
        update_experience_type(type_id, type_name)
    else:
        add_experience_type(type_name)

    return RedirectResponse(url="/admin/experience-types", status_code=303)


@app.get("/admin/experience-types/delete/{type_id}")
def admin_remove_experience_type(request: Request, type_id: int):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    delete_experience_type(type_id)
    return RedirectResponse(url="/admin/experience-types", status_code=303)

# =========================================================
# ADMIN JOB TITLE MASTER
# =========================================================
@app.get("/admin/job-titles", response_class=HTMLResponse)
def admin_job_titles_page(request: Request, edit_id: int | None = Query(None)):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    job_titles = get_job_titles()
    edit_job_title = None

    if edit_id:
        cur = conn.cursor()
        edit_job_title = cur.execute(
            "SELECT id, job_title FROM job_title_master WHERE id = ?",
            (edit_id,)
        ).fetchone()

    return templates.TemplateResponse(
        request,
        "admin/admin_job_titles.html",
        {
            "request": request,
            "job_titles": job_titles,
            "edit_job_title": edit_job_title
        }
    )


@app.post("/admin/job-titles/add")
def admin_add_job_title(
    request: Request,
    job_title_id: int | None = Form(None),
    job_title: str = Form(...)
):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    cur = conn.cursor()

    if job_title_id:
        cur.execute(
            "UPDATE job_title_master SET job_title = ? WHERE id = ?",
            (job_title, job_title_id)
        )
        conn.commit()
        return RedirectResponse(url="/admin/job-titles", status_code=303)

    add_job_title(job_title)
    return RedirectResponse(url="/admin/job-titles", status_code=303)


@app.get("/admin/job-titles/delete/{job_title_id}")
def admin_remove_job_title(request: Request, job_title_id: int):
    admin = require_admin(request)
    if isinstance(admin, RedirectResponse):
        return admin

    delete_job_title(job_title_id)
    return RedirectResponse(url="/admin/job-titles", status_code=303)