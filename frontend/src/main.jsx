import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import axios from 'axios';
import './style.css';

const API = "https://hiresmart-backend-90jm.onrender.com/api";

function App() {
  const [resume, setResume] = useState(null);
  const [jd, setJd] = useState('');
  const [result, setResult] = useState(null);
  const [role, setRole] = useState('Software Engineer');
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);

  async function analyze(e) {
    e.preventDefault();

    if (!resume || !jd) {
      alert('Upload resume and enter job description');
      return;
    }

    setLoading(true);

    const fd = new FormData();
    fd.append('resume', resume);
    fd.append('jobDescription', jd);

    try {
      const res = await axios.post(`${API}/resume/analyze`, fd);
      setResult(res.data);
    } catch (err) {
      alert(err.response?.data?.message || 'Analysis failed. Start backend and AI service.');
    } finally {
      setLoading(false);
    }
  }

  async function startInterview() {
    try {
      const res = await axios.post(`${API}/interview/questions`, {
        role,
        skills: result?.skills || []
      });

      setQuestions(res.data.questions);
    } catch (e) {
      alert('Could not generate questions');
    }
  }

  async function evalInterview() {
    try {
      const payload = questions.map((q, i) => ({
        question: q,
        answer: answers[i] || ''
      }));

      const res = await axios.post(`${API}/interview/evaluate`, {
        qa: payload
      });

      setEvaluation(res.data);
    } catch (e) {
      alert('Could not evaluate interview');
    }
  }

  return (
    <div className="app">

      <header className="hero">
        <div className="hero-content">
          <span className="badge">AI Powered Recruitment Platform</span>

          <h1>HireSmart AI</h1>

          <p>
            Intelligent Resume Screening & AI Interview Evaluation System using NLP and Machine Learning.
          </p>

          <div className="hero-buttons">
            <a href="#resume" className="primary-btn">Analyze Resume</a>
            <a href="#interview" className="secondary-btn">Start AI Interview</a>
          </div>
        </div>

        <div className="hero-glow"></div>
      </header>

      <main>

        <section className="stats-grid">
          <div className="stat-card">
            <h3>{result ? `${result.atsScore}%` : '0%'}</h3>
            <p>ATS Score</p>
          </div>

          <div className="stat-card">
            <h3>{result ? result.skills.length : 0}</h3>
            <p>Skills Found</p>
          </div>

          <div className="stat-card">
            <h3>{result ? result.missingSkills.length : 0}</h3>
            <p>Missing Skills</p>
          </div>

          <div className="stat-card">
            <h3 className="recommendation-text">
              {result?.hiringRecommendation || 'N/A'}</h3>
            <p>Hiring Recommendation</p>
          </div>
        </section>

        <section id="resume" className="card">
          <div className="section-heading">
            <span>Resume Intelligence</span>
            <h2>Resume ATS Analyzer</h2>
          </div>

          <form onSubmit={analyze}>
            <label>Upload Resume PDF/TXT</label>

            <div className="upload-box">
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={e => setResume(e.target.files[0])}
              />

              <p>
                {resume ? resume.name : 'Choose your resume file'}
              </p>
            </div>

            <label>Job Description</label>

            <textarea
              value={jd}
              onChange={e => setJd(e.target.value)}
              placeholder="Paste full job description with required skills here..."
            />

            <button disabled={loading}>
              {loading ? 'Analyzing Resume...' : 'Analyze Resume'}
            </button>
          </form>
        </section>

        {result && (
          <section className="card">
            <div className="section-heading">
              <span>AI Generated Report</span>
              <h2>Analysis Report</h2>
            </div>

            <div className="ats-card">
              <h3>ATS Match Score</h3>

              <div className="ats-value">
                {result.atsScore}%
              </div>

              <p>
                {result.atsScore >= 80
                  ? 'Excellent resume match.'
                  : result.atsScore >= 60
                  ? 'Good match. Minor improvements suggested.'
                  : 'Keep improving your resume.'}
              </p>
            </div>

            <div className="report-box blue">
              <h3>Candidate Overview</h3>
              <p><b>Experience Level:</b> {result.experienceLevel || 'Not available'}</p>
              <p><b>Hiring Recommendation:</b> {result.hiringRecommendation || 'Not available'}</p>
              <p><b>Skill Match Score:</b> {result.skillMatchScore || 0}%</p>
            </div>

            <div className="report-box green">
              <h3>Detected Skills</h3>

              {result.skills && result.skills.length > 0 ? (
                <div className="skill-wrap">
                  {result.skills.map((skill, i) => (
                    <span className="skill-chip" key={i}>
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p>No skills detected</p>
              )}
            </div>

            <div className="report-box orange">
              <h3>Missing Skills</h3>

              {result.missingSkills && result.missingSkills.length > 0 ? (
                <div className="skill-wrap">
                  {result.missingSkills.map((skill, i) => (
                    <span className="missing-chip" key={i}>
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p>No major missing skills</p>
              )}
            </div>

            <div className="report-box green">
              <h3>Strengths</h3>

              {result.strengths && result.strengths.length > 0 ? (
                <ul>
                  {result.strengths.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              ) : (
                <p>No strengths available</p>
              )}
            </div>

            <div className="report-box orange">
              <h3>Weaknesses</h3>

              {result.weaknesses && result.weaknesses.length > 0 ? (
                <ul>
                  {result.weaknesses.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              ) : (
                <p>No weaknesses available</p>
              )}
            </div>

            <div className="report-box blue">
              <h3>Suggestions</h3>

              {result.suggestions && result.suggestions.length > 0 ? (
                <ul>
                  {result.suggestions.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              ) : (
                <p>No suggestions available</p>
              )}
            </div>

            <div className="report-box blue">
              <h3>Improvement Roadmap</h3>

              {result.improvementRoadmap && result.improvementRoadmap.length > 0 ? (
                <ol>
                  {result.improvementRoadmap.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ol>
              ) : (
                <p>No roadmap available</p>
              )}
            </div>
          </section>
        )}

        <section id="interview" className="card">
          <div className="section-heading">
            <span>Interview Intelligence</span>
            <h2>AI Interview</h2>
          </div>

          <label>Job Role</label>

          <input
            value={role}
            onChange={e => setRole(e.target.value)}
            placeholder="Job role"
          />

          <button onClick={startInterview}>
            Generate Interview Questions
          </button>

          {questions.map((q, i) => (
            <div className="q" key={i}>
              <b>Q{i + 1}. {q}</b>

              <textarea
                placeholder="Type your answer"
                onChange={e =>
                  setAnswers({
                    ...answers,
                    [i]: e.target.value
                  })
                }
              />
            </div>
          ))}

          {questions.length > 0 && (
            <button onClick={evalInterview}>
              Evaluate Interview
            </button>
          )}

          {evaluation && (
            <div className="report-box blue">
              <h3>Interview Score: {evaluation.score}%</h3>

              <ul>
                {evaluation.feedback.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </div>
          )}
        </section>

      </main>

      <footer className="footer">
        <p>
          Developed by <span>Pranav Peherkar</span>
        </p>
      </footer>

    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);