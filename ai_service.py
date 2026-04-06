import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

client = genai.Client(api_key=api_key)


def generate_experience_description(
    job_title: str,
    custom_job_title: str,
    experience_type: str,
    company_name: str,
    location: str,
    user_input: str
) -> str:
    final_job_title = custom_job_title.strip() if custom_job_title.strip() else job_title.strip()
    experience_type = experience_type.strip()
    company_name = company_name.strip()
    location = location.strip()
    user_input = user_input.strip()

    if user_input:
        prompt = f"""
You are a professional resume writing assistant.

Rewrite and improve the user's work experience draft into strong, ATS-friendly resume bullet points.

Candidate details:
- Job Title: {final_job_title}
- Experience Type: {experience_type}
- Company Name: {company_name}
- Location: {location}

User draft:
{user_input}

Instructions:
- Keep the original meaning.
- Improve grammar, clarity, and professionalism.
- Write 4 to 6 bullet points.
- Start each line with "•".
- Use action verbs.
- Make the bullets realistic and resume-friendly.
- Do not invent fake metrics, fake achievements, or unrealistic claims.
- Return only the bullet points.
"""
    else:
        prompt = f"""
You are a professional resume writing assistant.

Generate a realistic, ATS-friendly work experience description for a resume.

Candidate details:
- Job Title: {final_job_title}
- Experience Type: {experience_type}
- Company Name: {company_name}
- Location: {location}

Instructions:
- Write 4 to 6 bullet points.
- Start each line with "•".
- Use action verbs.
- Make the content realistic and professional.
- Focus on common responsibilities, collaboration, problem solving, tools, and impact.
- Do not invent fake metrics, fake achievements, or unrealistic claims.
- Return only the bullet points.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = getattr(response, "text", None)
    if not text:
        raise ValueError("Empty response from Gemini.")
    return text.strip()

def generate_project_description(
    project_title: str,
    technologies: str,
    user_input: str
) -> str:
    project_title = project_title.strip()
    technologies = technologies.strip()
    user_input = user_input.strip()

    if user_input:
        prompt = f"""
You are a professional resume writing assistant.

Rewrite and improve the user's project description into strong, ATS-friendly resume bullet points.

Project details:
- Project Title: {project_title}
- Technologies Used: {technologies}

User draft:
{user_input}

Instructions:
- Keep the original meaning.
- Improve grammar, clarity, and professionalism.
- Write 3 to 5 bullet points.
- Start each line with "•".
- Use action verbs.
- Make the bullets realistic and resume-friendly.
- Highlight features, functionality, technologies, and impact.
- Do not invent fake metrics or unrealistic claims.
- Return only the bullet points.
"""
    else:
        prompt = f"""
You are a professional resume writing assistant.

Generate a realistic, ATS-friendly project description for a resume.

Project details:
- Project Title: {project_title}
- Technologies Used: {technologies}

Instructions:
- Write 3 to 5 bullet points.
- Start each line with "•".
- Use action verbs.
- Make the content realistic and professional.
- Highlight project functionality, user features, technologies used, and problem solving.
- Do not invent fake metrics or unrealistic claims.
- Return only the bullet points.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = getattr(response, "text", None)
    if not text:
        raise ValueError("Empty response from Gemini.")
    return text.strip()

def generate_missing_skills(
    job_role: str,
    current_core_skills: str,
    current_soft_skills: str,
    current_tools: str,
    current_languages: str
) -> str:
    job_role = job_role.strip()
    current_core_skills = current_core_skills.strip()
    current_soft_skills = current_soft_skills.strip()
    current_tools = current_tools.strip()
    current_languages = current_languages.strip()

    prompt = f"""
You are a professional resume and career assistant.

Based on the target job role and the user's current skills, suggest important missing skills.

Target Job Role:
{job_role}

Current Core Skills:
{current_core_skills}

Current Soft Skills:
{current_soft_skills}

Current Tools / Technologies:
{current_tools}

Current Languages:
{current_languages}

Instructions:
- Suggest realistic missing skills for this role.
- Do not repeat skills the user already entered.
- Organize the answer into these sections:
1. Missing Core Skills
2. Missing Soft Skills
3. Missing Tools / Technologies
4. Recommended AI / Modern Tools
- Keep it concise, practical, and resume-focused.
- Use bullet points.
- Return plain text only.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = getattr(response, "text", None)
    if not text:
        raise ValueError("Empty response from Gemini.")
    return text.strip()

def generate_professional_summary(
    profile: dict | None,
    educations: list,
    experiences: list,
    skills: dict | None,
    projects: list,
    certifications: list,
    existing_summary: str
) -> str:
    existing_summary = (existing_summary or "").strip()

    # ---------------------------
    # Profile
    # ---------------------------
    profile_text = ""
    if profile:
        profile_text = f"""
Profile:
- Full Name: {profile.get("full_name", "")}
- Location: {profile.get("location", "")}
- Country: {profile.get("country", "")}
"""

        # ---------------------------
    # Education
    # ---------------------------
    education_lines = []
    for edu in educations or []:
        degree_value = (
            edu.get("degree_name")
            or edu.get("custom_degree")
            or ""
        )

        course_value = (
            edu.get("course_name")
            or edu.get("custom_course")
            or ""
        )

        institution_value = (
            edu.get("institute_name")
            or edu.get("institution_name")
            or edu.get("custom_institution")
            or ""
        )

        education_lines.append(
            f"- Degree: {degree_value}, "
            f"Course: {course_value}, "
            f"Institution: {institution_value}, "
            f"Location: {edu.get('location', '')}, "
            f"Start: {edu.get('start_month', '')}, "
            f"End: {edu.get('end_month', '')}, "
            f"Grade: {edu.get('grade', '')}"
        )

    education_text = "Education:\n" + (
        "\n".join(education_lines) if education_lines else "- Not provided"
    )

    # ---------------------------
    # Experience
    # ---------------------------
    experience_lines = []
    meaningful_experience_count = 0

    for exp in experiences or []:
        job_title = exp.get("job_title_name") or exp.get("custom_job_title") or ""
        company_name = exp.get("company_name", "") or ""
        description = exp.get("description", "") or ""
        experience_type = exp.get("experience_type_name", "") or ""

        if job_title.strip() or company_name.strip() or description.strip():
            meaningful_experience_count += 1

        experience_lines.append(
            f"- Job Title: {job_title}, Company: {company_name}, "
            f"Type: {experience_type}, Location: {exp.get('location', '')}, "
            f"Start: {exp.get('start_month', '')}, End: {exp.get('end_month', '')}, "
            f"Description: {description}"
        )

    experience_text = "Experience:\n" + ("\n".join(experience_lines) if experience_lines else "- Not provided")

    # ---------------------------
    # Skills + Target Role
    # ---------------------------
    target_job_role = ""
    skills_text = "Skills:\n- Not provided"

    if skills:
        target_job_role = (skills.get("job_role_name") or skills.get("custom_job_role") or "").strip()

        skills_text = f"""
Skills:
- Target Job Role: {target_job_role}
- Core Skills: {skills.get("core_skills", "")}
- Soft Skills: {skills.get("soft_skills", "")}
- Tools / Technologies: {skills.get("tools_technologies", "")}
- Languages: {skills.get("languages", "")}
- Missing Skills Suggestions: {skills.get("missing_skills_suggestions", "")}
"""

    # ---------------------------
    # Projects
    # ---------------------------
    project_lines = []
    for project in projects or []:
        project_lines.append(
            f"- Title: {project.get('project_title', '')}, Technologies: {project.get('technologies', '')}, "
            f"Description: {project.get('description', '')}"
        )
    project_text = "Projects:\n" + ("\n".join(project_lines) if project_lines else "- Not provided")

    # ---------------------------
    # Certifications
    # ---------------------------
    certification_lines = []
    for cert in certifications or []:
        certification_lines.append(
            f"- Certificate: {cert.get('certificate_name', '')}, Organization: {cert.get('organization', '')}, "
            f"Date: {cert.get('certificate_date', '')}"
        )
    certification_text = "Certifications:\n" + ("\n".join(certification_lines) if certification_lines else "- Not provided")

    # ---------------------------
    # Candidate Type Logic
    # ---------------------------
    is_fresher = meaningful_experience_count == 0

    if is_fresher:
        career_level_instruction = """
Candidate Type:
- Fresher / Student / Entry-Level

Summary Style Instructions:
- Focus on education, academic background, projects, certifications, technical skills, learning mindset, and problem-solving ability.
- Highlight enthusiasm, adaptability, collaboration, and readiness to contribute.
- Keep the tone strong and professional, but suitable for a fresher.
- Do not make the user sound highly experienced.
"""
    else:
        career_level_instruction = """
Candidate Type:
- Experienced Professional

Summary Style Instructions:
- Focus on work experience, responsibilities, practical skills, project delivery, tools, collaboration, and professional strengths.
- Make the summary stronger and more confident than a fresher summary.
- Highlight proven ability, hands-on experience, execution, and impact.
- Keep it professional, polished, and ATS-friendly.
"""

    # ---------------------------
    # Target Role Logic
    # ---------------------------
    if target_job_role:
        role_instruction = f"""
Target Role Instructions:
- The candidate is targeting the role: {target_job_role}
- Tailor the summary to align with this target role.
- Use wording that matches this role naturally.
- Emphasize the most relevant skills, projects, tools, and experience for this role.
- Make the summary feel job-focused and resume-ready.
"""
    else:
        role_instruction = """
Target Role Instructions:
- No target role is explicitly provided.
- Create a general professional summary based on the candidate's strongest profile details.
"""

    # ---------------------------
    # Base Context
    # ---------------------------
    base_context = f"""
You are a professional resume writing assistant.

Use the candidate details below to create a strong, ATS-friendly professional summary.

{career_level_instruction}

{role_instruction}

Important Rules:
- Use profile details only as background context.
- Do NOT include email, phone number, LinkedIn URL, GitHub URL, or full address in the summary.
- Do NOT invent fake experience, fake achievements, fake companies, or unrealistic claims.
- Keep the summary natural, polished, and suitable for a resume.

{profile_text}

{education_text}

{experience_text}

{skills_text}

{project_text}

{certification_text}
"""

    # ---------------------------
    # Improve existing summary
    # ---------------------------
    if existing_summary:
        prompt = f"""
{base_context}

Current user summary:
{existing_summary}

Instructions:
- Improve and rewrite the current summary.
- Keep the meaning aligned with the user's actual resume details.
- Tailor it for the target role if available.
- Match the correct candidate level: fresher or experienced.
- Write in 3 to 5 lines.
- Use plain text only.
- Do not use bullet points.
- Keep it concise, strong, and ATS-friendly.
"""
    else:
        prompt = f"""
{base_context}

Instructions:
- Generate a strong professional resume summary.
- Tailor it for the target job role if available.
- Match the correct candidate level: fresher or experienced.
- Write in 3 to 5 lines.
- Use plain text only.
- Do not use bullet points.
- Keep it concise, polished, and ATS-friendly.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = getattr(response, "text", None)
    if not text:
        raise ValueError("Empty response from Gemini.")

    return text.strip()