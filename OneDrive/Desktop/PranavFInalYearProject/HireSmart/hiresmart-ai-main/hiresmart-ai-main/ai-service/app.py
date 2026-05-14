from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
app=FastAPI(title='HireSmart AI Service')
SKILLS=['python','java','javascript','react','node','express','mongodb','sql','html','css','machine learning','deep learning','nlp','fastapi','flask','django','git','docker','aws','azure','data analysis','tensorflow','pytorch','communication','problem solving','teamwork']
class AnalyzeReq(BaseModel):
    resumeText:str
    jobDescription:str
class QuestionReq(BaseModel):
    role:str='Software Engineer'
    skills:list[str]=[]
class EvalReq(BaseModel):
    qa:list[dict]
def extract_skills(text):
    t=text.lower(); return sorted({s for s in SKILLS if re.search(r'\b'+re.escape(s)+r'\b',t)})
@app.get('/')
def root(): return {'message':'HireSmart AI Service Running'}
@app.post('/analyze')
def analyze(req:AnalyzeReq):
    resume=req.resumeText or ''; jd=req.jobDescription or ''
    skills=extract_skills(resume); jdskills=extract_skills(jd)
    missing=[s for s in jdskills if s not in skills]
    score=0
    if resume.strip() and jd.strip():
        vec=TfidfVectorizer(stop_words='english').fit_transform([resume,jd])
        score=int(round(float(cosine_similarity(vec[0:1],vec[1:2])[0][0])*100))
    if jdskills:
        skill_score=int(round((len(jdskills)-len(missing))/len(jdskills)*100))
        score=int(round((score+skill_score)/2))
    suggestions=[]
    if missing: suggestions.append('Add or improve these missing skills: '+', '.join(missing))
    if len(resume.split())<200: suggestions.append('Resume content is short. Add projects, achievements and measurable impact.')
    if not re.search(r'\d+%|\d+\+',resume): suggestions.append('Add numbers such as accuracy, percentage improvement, users served, or project metrics.')
    if not suggestions: suggestions.append('Resume matches the job description well. Improve formatting and add quantified achievements.')
    return {'atsScore':max(0,min(100,score)),'skills':skills,'missingSkills':missing,'suggestions':suggestions}
@app.post('/interview/questions')
def questions(req:QuestionReq):
    base=[f'Tell me about yourself for the role of {req.role}.',f'Explain one project related to {req.role}.','What are your strongest technical skills?','Describe a challenge you faced and how you solved it.','Why should we select you for this role?']
    for s in req.skills[:3]: base.append(f'Explain your experience with {s}.')
    return {'questions':base[:7]}
@app.post('/interview/evaluate')
def evaluate(req:EvalReq):
    feedback=[]; total=0
    for item in req.qa:
        ans=(item.get('answer') or '').strip(); words=len(ans.split())
        if words>=35: total+=15; feedback.append('Good detailed answer for: '+item.get('question',''))
        elif words>=12: total+=10; feedback.append('Average answer. Add more examples for: '+item.get('question',''))
        else: total+=5; feedback.append('Short answer. Explain with project example for: '+item.get('question',''))
    max_score=max(1,len(req.qa)*15)
    return {'score':int(round(total/max_score*100)),'feedback':feedback}
