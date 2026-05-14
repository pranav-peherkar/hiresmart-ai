import React,{useState}from'react';import{createRoot}from'react-dom/client';import axios from'axios';import'./style.css';
const API = "https://hiresmart-backend-90jm.onrender.com/api";
function App(){const[resume,setResume]=useState(null);const[jd,setJd]=useState('');const[result,setResult]=useState(null);const[role,setRole]=useState('Software Engineer');const[questions,setQuestions]=useState([]);const[answers,setAnswers]=useState({});const[evaluation,setEvaluation]=useState(null);const[loading,setLoading]=useState(false);
async function analyze(e){e.preventDefault();if(!resume||!jd)return alert('Upload resume and enter job description');setLoading(true);const fd=new FormData();fd.append('resume',resume);fd.append('jobDescription',jd);try{const res=await axios.post(`${API}/resume/analyze`,fd);setResult(res.data)}catch(err){alert(err.response?.data?.message||'Analysis failed. Start backend and AI service.')}setLoading(false)}
async function startInterview(){try{const res=await axios.post(`${API}/interview/questions`,{role,skills:result?.skills||[]});setQuestions(res.data.questions)}catch(e){alert('Could not generate questions')}}
async function evalInterview(){const payload=questions.map((q,i)=>({question:q,answer:answers[i]||''}));const res=await axios.post(`${API}/interview/evaluate`,{qa:payload});setEvaluation(res.data)}
return <div><header><h1>HireSmart AI</h1>
<p>Intelligent Resume Screening & AI Interview Evaluation Platform</p></header><main><section className="card"><h2>Resume ATS Analyzer</h2><form onSubmit={analyze}><label>Upload Resume PDF/TXT</label><input type="file" accept=".pdf,.txt" onChange={e=>setResume(e.target.files[0])}/><label>Job Description</label><textarea value={jd} onChange={e=>setJd(e.target.value)} placeholder="Paste job description here..."></textarea><button disabled={loading}>{loading?'Analyzing...':'Analyze Resume'}</button></form></section>{result&&<section className="card"><h2>Analysis Report</h2><div className="score">ATS Score: {result.atsScore}%</div><h3>Detected Skills</h3><p>{result.skills.join(', ')||'No skills detected'}</p><h3>Missing Skills</h3><p>{result.missingSkills.join(', ')||'No major missing skills'}</p><h3>Suggestions</h3><ul>{result.suggestions.map((s,i)=><li key={i}>{s}</li>)}</ul></section>}<section className="card"><h2>AI Interview</h2><input value={role} onChange={e=>setRole(e.target.value)} placeholder="Job role"/><button onClick={startInterview}>Generate Interview Questions</button>{questions.map((q,i)=><div className="q" key={i}><b>Q{i+1}. {q}</b><textarea placeholder="Type your answer" onChange={e=>setAnswers({...answers,[i]:e.target.value})}></textarea></div>)}{questions.length>0&&<button onClick={evalInterview}>Evaluate Interview</button>}{evaluation&&<div><h3>Interview Score: {evaluation.score}%</h3><ul>{evaluation.feedback.map((f,i)=><li key={i}>{f}</li>)}</ul></div>}</section></main>

<footer className="footer">
  <p>
    Developed with ❤️ by <span>Pranav Peherkar</span>
  </p>
</footer>

</div>}
createRoot(document.getElementById('root')).render(<App/>);
