import json

def load_skills(job_role):
    skills_by_role = {
        "data_analyst": ["python", "sql", "excel", "powerbi", "statistics"],
        "software_engineer": ["python", "dsa", "oops", "git", "sql"],
        "database_developer": ["sql", "dbms", "pl/sql", "normalization", "mysql"],
        "machine_learning_engineer": ["python", "numpy", "pandas", "sklearn", "matplotlib"],
        "cloud_engineer": ["aws", "linux", "git", "python", "docker"]
    }

    return skills_by_role.get(job_role.lower(), [])


def match_skills(resume_text, role_skills):
    found = [skill for skill in role_skills if skill in resume_text.lower()]
    missing = list(set(role_skills) - set(found))
    return found, missing

