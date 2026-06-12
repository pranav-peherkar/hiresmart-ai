from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

app = FastAPI(title="HireSmart AI Service")

SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "reactjs",
    "node",
    "nodejs",
    "express",
    "expressjs",
    "mongodb",
    "mysql",
    "postgresql",
    "sql",
    "html",
    "css",
    "tailwind",
    "bootstrap",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "nlp",
    "fastapi",
    "flask",
    "django",
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "data analysis",
    "tensorflow",
    "pytorch",
    "scikit learn",
    "rest api",
    "api",
    "jwt",
    "authentication",
    "communication",
    "problem solving",
    "teamwork",
    "leadership"
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

    if len(jd_skills) > 0:
        matched_skills = len(jd_skills) - len(missing_skills)

        skill_score = int(
            (matched_skills / len(jd_skills)) * 100
        )

        score = int((score + skill_score) / 2)

    suggestions = []

    if missing_skills:
        suggestions.append(
            "Add these missing skills: "
            + ", ".join(missing_skills)
        )

    if len(resume.split()) < 200:
        suggestions.append(
            "Resume content is short. Add more projects, experience, and achievements."
        )

    if not re.search(r"\d+%|\d+\+", resume):
        suggestions.append(
            "Add measurable achievements such as 40% improvement, 1M+ users, or 25% faster performance."
        )

    if not suggestions:
        suggestions.append(
            "Resume is well aligned with the job description."
        )

    return {
        "atsScore": max(0, min(score, 100)),
        "skills": resume_skills,
        "jobSkills": jd_skills,
        "missingSkills": missing_skills,
        "suggestions": suggestions
    }

@app.post("/interview/questions")
def interview_questions(req: QuestionReq):

    questions = [
        f"Tell me about yourself for the role of {req.role}.",
        f"Explain one project related to {req.role}.",
        "What are your strongest technical skills?",
        "Describe a challenge you faced and how you solved it.",
        "Why should we hire you?"
    ]

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