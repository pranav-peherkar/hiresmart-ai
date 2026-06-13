from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

app = FastAPI(title="HireSmart AI Service")

SKILLS = [
    "python", "java", "javascript", "typescript", "react", "reactjs",
    "node", "nodejs", "express", "expressjs", "mongodb", "mysql",
    "postgresql", "sql", "html", "css", "tailwind", "bootstrap",
    "machine learning", "deep learning", "artificial intelligence",
    "ai", "nlp", "fastapi", "flask", "django", "git", "github",
    "docker", "kubernetes", "aws", "azure", "data analysis",
    "tensorflow", "pytorch", "scikit learn", "rest api", "api",
    "jwt", "authentication", "communication", "problem solving",
    "teamwork", "leadership"
]

SKILL_ALIASES = {
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node",
    "node.js": "node",
    "expressjs": "express",
    "express.js": "express",
    "js": "javascript",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "scikit-learn": "scikit learn",
    "restful api": "rest api",
    "apis": "api"
}

class AnalyzeReq(BaseModel):
    resumeText: str
    jobDescription: str

class QuestionReq(BaseModel):
    role: str = "Software Engineer"
    skills: list[str] = []

class EvalReq(BaseModel):
    qa: list[dict]

def normalize_text(text):
    text = text.lower()

    for alias, standard in SKILL_ALIASES.items():
        text = text.replace(alias, standard)

    text = text.replace(".js", "js")
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    text = text.replace("htmachine learning", "machine learning")
    text = re.sub(r"[^a-z0-9\s+#]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def extract_skills(text):
    clean_text = normalize_text(text)
    found_skills = []

    for skill in SKILLS:
        clean_skill = normalize_text(skill)

        if re.search(r"\b" + re.escape(clean_skill) + r"\b", clean_text):
            found_skills.append(skill)

    normalized_found = []

    for skill in found_skills:
        skill_clean = normalize_text(skill)
        final_skill = SKILL_ALIASES.get(skill_clean, skill_clean)
        normalized_found.append(final_skill)

    return sorted(list(set(normalized_found)))

def detect_experience_level(resume):
    text = resume.lower()

    if re.search(r"5\+?\s*years|five years|senior", text):
        return "Senior Level"

    if re.search(r"3\+?\s*years|4\+?\s*years|mid level", text):
        return "Mid-Level"

    if re.search(r"1\+?\s*year|2\+?\s*years|junior", text):
        return "Junior Level"

    if "internship" in text or "intern" in text or "fresher" in text:
        return "Fresher"

    return "Entry Level"

def get_hiring_recommendation(score):
    if score >= 85:
        return "Strong Hire"
    elif score >= 70:
        return "Hire"
    elif score >= 50:
        return "Consider"
    else:
        return "Not Recommended"

def analyze_resume_sections(resume):
    text = resume.lower()

    section_analysis = {
        "contactInformation": bool(
            re.search(r"\b\d{10}\b", text)
            or re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
            or "email" in text
            or "phone" in text
            or "mobile" in text
        ),
        "education": any(word in text for word in [
            "education", "degree", "bachelor", "master", "b.tech",
            "b.e", "computer science", "university", "college", "cgpa"
        ]),
        "skills": any(word in text for word in [
            "skills", "technical skills", "programming", "technologies"
        ]),
        "projects": any(word in text for word in [
            "project", "projects", "developed", "built", "created"
        ]),
        "experience": any(word in text for word in [
            "experience", "work experience", "employment", "internship",
            "software engineer", "developer", "company"
        ]),
        "certifications": any(word in text for word in [
            "certification", "certifications", "certified", "certificate"
        ]),
        "linkedin": "linkedin" in text,
        "github": "github" in text,
        "achievements": any(word in text for word in [
            "achievement", "achievements", "award", "winner", "improved",
            "reduced", "increased"
        ])
    }

    present_sections = []
    missing_sections = []

    labels = {
        "contactInformation": "Contact Information",
        "education": "Education",
        "skills": "Skills",
        "projects": "Projects",
        "experience": "Experience",
        "certifications": "Certifications",
        "linkedin": "LinkedIn",
        "github": "GitHub",
        "achievements": "Achievements"
    }

    for key, value in section_analysis.items():
        if value:
            present_sections.append(labels[key])
        else:
            missing_sections.append(labels[key])

    section_score = int((len(present_sections) / len(section_analysis)) * 100)

    return {
        "sections": section_analysis,
        "presentSections": present_sections,
        "missingSections": missing_sections,
        "sectionScore": section_score
    }

def generate_strengths(resume, resume_skills, score):
    strengths = []

    if len(resume_skills) >= 8:
        strengths.append("Strong technical skill set")

    if "github" in resume.lower():
        strengths.append("GitHub profile or project links available")

    if "linkedin" in resume.lower():
        strengths.append("LinkedIn profile available")

    if re.search(r"\d+%|\d+\+", resume):
        strengths.append("Contains measurable achievements")

    if "project" in resume.lower():
        strengths.append("Project experience mentioned")

    if score >= 70:
        strengths.append("Good match with the job description")

    if not strengths:
        strengths.append("Basic resume structure is present")

    return strengths

def generate_weaknesses(resume, missing_skills):
    weaknesses = []

    if missing_skills:
        weaknesses.append(
            "Missing important job skills: " + ", ".join(missing_skills[:5])
        )

    if len(resume.split()) < 200:
        weaknesses.append("Resume content is short")

    if "github" not in resume.lower():
        weaknesses.append("GitHub profile is missing")

    if "linkedin" not in resume.lower():
        weaknesses.append("LinkedIn profile is missing")

    if not re.search(r"\d+%|\d+\+", resume):
        weaknesses.append("Measurable achievements are missing")

    if "certification" not in resume.lower() and "certified" not in resume.lower():
        weaknesses.append("Certifications are not mentioned")

    if not weaknesses:
        weaknesses.append("No major weaknesses found")

    return weaknesses

def generate_roadmap(missing_skills, resume):
    roadmap = []

    if missing_skills:
        roadmap.append(
            "Add projects or practical experience related to: "
            + ", ".join(missing_skills[:5])
        )

    if "github" not in resume.lower():
        roadmap.append("Add GitHub profile with live project repositories")

    if "linkedin" not in resume.lower():
        roadmap.append("Add LinkedIn profile for professional visibility")

    if not re.search(r"\d+%|\d+\+", resume):
        roadmap.append("Add measurable results like 30% improvement or 500+ users")

    if len(resume.split()) < 200:
        roadmap.append("Expand resume with more projects, internships, and achievements")

    if not roadmap:
        roadmap.append("Resume is strong. Keep tailoring it for each job description")

    return roadmap

@app.get("/")
def root():
    return {
        "message": "HireSmart AI Service Running"
    }

@app.post("/analyze")
def analyze(req: AnalyzeReq):

    resume = req.resumeText or ""
    jd = req.jobDescription or ""

    resume_skills = extract_skills(resume)
    jd_skills = extract_skills(jd)

    resume_skills_lower = [skill.lower() for skill in resume_skills]

    missing_skills = [
        skill for skill in jd_skills
        if skill.lower() not in resume_skills_lower
    ]

    score = 0

    if resume.strip() and jd.strip():
        vectors = TfidfVectorizer(
            stop_words="english"
        ).fit_transform([resume, jd])

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        score = int(similarity * 100)

    skill_score = 0

    if len(jd_skills) > 0:
        matched_skills = len(jd_skills) - len(missing_skills)
        skill_score = int((matched_skills / len(jd_skills)) * 100)
        score = int((score * 0.30) + (skill_score * 0.70))

    section_analysis = analyze_resume_sections(resume)

    score = int((score * 0.85) + (section_analysis["sectionScore"] * 0.15))
    score = max(0, min(score, 100))

    suggestions = []

    if missing_skills:
        suggestions.append(
            f"Consider adding experience, certifications, or projects related to: {', '.join(missing_skills[:5])}"
        )

    if section_analysis["missingSections"]:
        suggestions.append(
            "Improve resume structure by adding: "
            + ", ".join(section_analysis["missingSections"][:4])
        )

    if score < 50:
        suggestions.append(
            "Low match with the job description. Customize your resume to better align with the required skills."
        )

    elif score < 75:
        suggestions.append(
            "Moderate match. Add more relevant technical skills, projects, and work experience."
        )

    else:
        suggestions.append(
            "Strong match with the job description. Focus on highlighting achievements and measurable impact."
        )

    if len(resume.split()) < 200:
        suggestions.append(
            "Resume content is short. Add more projects, internships, certifications, or professional experience."
        )

    if not re.search(r"\d+%|\d+\+", resume):
        suggestions.append(
            "Add measurable achievements such as 'Improved efficiency by 30%' or 'Served 500+ customers monthly'."
        )

    experience_level = detect_experience_level(resume)
    hiring_recommendation = get_hiring_recommendation(score)
    strengths = generate_strengths(resume, resume_skills, score)
    weaknesses = generate_weaknesses(resume, missing_skills)
    improvement_roadmap = generate_roadmap(missing_skills, resume)

    return {
        "atsScore": score,
        "skillMatchScore": skill_score,
        "sectionScore": section_analysis["sectionScore"],
        "sectionAnalysis": section_analysis,
        "skills": resume_skills,
        "jobSkills": jd_skills,
        "missingSkills": missing_skills,
        "suggestions": suggestions,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "experienceLevel": experience_level,
        "hiringRecommendation": hiring_recommendation,
        "improvementRoadmap": improvement_roadmap
    }

@app.post("/interview/questions")
def interview_questions(req: QuestionReq):

    role = req.role.lower()
    skills = [skill.lower() for skill in req.skills]

    questions = [
        f"Tell me about yourself for the role of {req.role}.",
        f"Explain one project related to {req.role}.",
        "What are your strongest technical skills?",
        "Describe a challenge you faced and how you solved it.",
        "Why should we hire you?"
    ]

    if "react" in role or "react" in skills:
        questions.extend([
            "What are React Hooks?",
            "Explain the difference between useState and useEffect.",
            "How do you optimize performance in a React application?"
        ])

    if "python" in role or "python" in skills:
        questions.extend([
            "What is the difference between list, tuple, and dictionary in Python?",
            "Explain exception handling in Python.",
            "What are Python decorators?"
        ])

    if "node" in role or "node" in skills:
        questions.extend([
            "What is middleware in Express.js?",
            "Explain asynchronous programming in Node.js.",
            "How do you handle authentication in Node.js?"
        ])

    if "aws" in role or "aws" in skills:
        questions.extend([
            "What is the difference between EC2 and S3?",
            "Explain how you would deploy an application on AWS.",
            "What is load balancing in cloud deployment?"
        ])

    for skill in req.skills[:3]:
        questions.append(
            f"Explain your experience with {skill}."
        )

    return {
        "questions": questions[:7]
    }

@app.post("/interview/evaluate")
def evaluate_interview(req: EvalReq):

    feedback = []
    total_score = 0

    for item in req.qa:

        answer = item.get("answer", "").strip()
        question = item.get("question", "")

        word_count = len(answer.split())

        if word_count >= 35:
            total_score += 15
            feedback.append(
                f"Good detailed answer for: {question}"
            )

        elif word_count >= 12:
            total_score += 10
            feedback.append(
                f"Average answer. Add more examples for: {question}"
            )

        else:
            total_score += 5
            feedback.append(
                f"Answer is too short for: {question}"
            )

    max_score = max(1, len(req.qa) * 15)

    return {
        "score": int((total_score / max_score) * 100),
        "feedback": feedback
    }