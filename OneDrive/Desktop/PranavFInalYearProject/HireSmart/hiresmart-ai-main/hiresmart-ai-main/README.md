# HireSmart AI - Smart Resume Analyzer & AI Interview System

## Folder structure
- frontend: React + Vite UI
- backend: Node.js + Express API
- ai-service: Python FastAPI NLP service

## Requirements
- Node.js 20 LTS recommended
- Python 3.10+
- MongoDB local or MongoDB Atlas

## Run locally

### 1. Backend
```bash
cd backend
copy .env.example .env
npm install
npm run dev
```
Backend runs on http://localhost:5000

### 2. AI Service
```bash
cd ai-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```
AI service runs on http://localhost:8000

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on http://localhost:5173

## Test flow
1. Open frontend.
2. Upload PDF or TXT resume.
3. Paste job description.
4. Click Analyze Resume.
5. Generate interview questions and evaluate answers.
