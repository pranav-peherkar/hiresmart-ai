const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const mongoose = require('mongoose');
const { GoogleGenerativeAI } = require('@google/generative-ai');

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());
app.use('/uploads', express.static('src/uploads'));

app.get('/', (req, res) => {
  res.send('HireSmart AI Backend Running');
});

app.post('/api/chatbot', async (req, res) => {
  try {
    const { message, analysis } = req.body;

    if (!message) {
      return res.status(400).json({
        message: 'Message is required'
      });
    }

    if (!process.env.GEMINI_API_KEY) {
      return res.status(500).json({
        message: 'Gemini API key is missing'
      });
    }

    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

    const model = genAI.getGenerativeModel({
      model: 'gemini-flash-latest'
    });

    const prompt = `
You are HireSmart AI Assistant, an AI recruitment assistant.

Help users with:
- resume improvement
- ATS score improvement
- missing skills
- hiring recommendation
- interview preparation
- candidate comparison
- job description matching

Keep answers short, clear, and practical.

Current resume analysis context:
${analysis ? JSON.stringify({
  atsScore: analysis.resumeAnalysis?.atsScore,
  missingSkills: analysis.resumeAnalysis?.missingSkills,
  recommendation: analysis.resumeAnalysis?.hiringRecommendation,
  experienceLevel: analysis.resumeAnalysis?.experienceLevel
}) : 'No resume analysis available'}

User question:
${message}
`;

    const result = await model.generateContent(prompt);
    const response = result.response.text();

    res.json({
      reply: response
    });

  } catch (error) {
    console.error('Chatbot error:', error.message);

    res.status(500).json({
      message: 'Chatbot failed',
      error: error.message
    });
  }
});

app.use('/api/auth', require('./routes/authRoutes'));
app.use('/api/resume', require('./routes/resumeRoutes'));
app.use('/api/interview', require('./routes/interviewRoutes'));

const PORT = process.env.PORT || 5000;

mongoose
  .connect(process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/hiresmart')
  .then(() => console.log('MongoDB Connected'))
  .catch(e => console.log('MongoDB connection failed:', e.message));

app.listen(PORT, () => {
  console.log('Server running on port ' + PORT);
});