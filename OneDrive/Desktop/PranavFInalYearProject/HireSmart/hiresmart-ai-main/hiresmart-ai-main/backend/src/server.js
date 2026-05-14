const express=require('express'),cors=require('cors'),dotenv=require('dotenv'),mongoose=require('mongoose');dotenv.config();
const app=express();app.use(cors());app.use(express.json());app.use('/uploads',express.static('src/uploads'));
app.get('/',(req,res)=>res.send('HireSmart AI Backend Running'));
app.use('/api/auth',require('./routes/authRoutes'));app.use('/api/resume',require('./routes/resumeRoutes'));app.use('/api/interview',require('./routes/interviewRoutes'));
const PORT=process.env.PORT||5000;mongoose.connect(process.env.MONGO_URI||'mongodb://127.0.0.1:27017/hiresmart').then(()=>console.log('MongoDB Connected')).catch(e=>console.log('MongoDB connection failed:',e.message));
app.listen(PORT,()=>console.log('Server running on port '+PORT));
